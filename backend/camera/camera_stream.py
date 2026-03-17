# camera/camera_stream.py
import cv2
import time
from recognition.face_recognizer import recognize_faces, load_known_faces
from events.event_queue import event_queue
from config import *


# To start integrated camera
# def start_camera(index=1):
    
#     cap = cv2.VideoCapture(index)
    
#     if not cap.isOpened():
#         raise Exception("Cannot open camera")
    
#     return cap

def run_camera(camera_id, source):
    print(f"[{camera_id}] Starting...")

    # Load known faces once at startup
    known_encodings, known_names = load_known_faces()
    last_reload   = time.time()
    last_intruder = 0
    last_seen     = {}   # {name: last_event_timestamp} — per-person cooldown
    frame_count   = 0

    cap = cv2.VideoCapture(source)
    
    if not cap.isOpened():
        print(f"[{camera_id}] ERROR: Cannot open camera source {source}")
        return
        
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print(f"[{camera_id}] Frame read failed — retrying...")
            time.sleep(0.1)
            continue
        
        # ── Hot reload ──────────────────────────────────────
        # Picks up newly enrolled people without restarting
        
        if time.time() - last_reload > ENCODING_RELOAD_INTERVAL:
            print(f"[{camera_id}] Reloading encodings from DB...")
            known_encodings, known_names = load_known_faces()
            last_reload = time.time()
            
        # ── Skip frames for performance ─────────────────────
        frame_count += 1
        if frame_count % PROCESS_EVERY_N_FRAMES != 0:
            continue
            
        # ── Preprocess ──────────────────────────────────────
        small_frame  = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    
        # ── Recognize ───────────────────────────────────────
        locations, names = recognize_faces(rgb_frame, known_encodings, known_names)
    
        # ── Handle each detected face ────────────────────────
        for(top, right, bottom, left), name in zip(locations, names):
            
            # Scale coords back to original frame size
            top *= 2 
            bottom *=2
            right *= 2
            left *= 2
            
            now = time.time()
        
            # Guard: face at frame edge can produce empty crop
            face_img = frame[top:bottom, left:right]
            
            if face_img.size == 0:
                continue
            
            if name == "UNKNOWN":
                if now - last_intruder > INTRUDER_COOLDOWN:
                    event_queue.put(("INTRUDER", face_img, name, camera_id))
                    last_intruder = now
            else:
                if now - last_seen.get(name, 0) > AUTHORIZED_COOLDOWN:
                    event_queue.put(("AUTHORIZED", face_img, name, camera_id))
                    last_seen[name] = now
    
        cv2.imshow(camera_id, frame)
        # Press 'q' to quit this camera window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        