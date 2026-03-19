# camera/camera_stream.py
import cv2
import time
import threading
from recognition.face_recognizer import recognize_faces, load_known_faces, check_and_reload
from events.event_queue import event_queue
from config import *

RECONNECT_AFTER = 30  # consecutive failed frames before attempting reconnect
# To start integrated camera
# def start_camera(index=1):
    
#     cap = cv2.VideoCapture(index)
    
#     if not cap.isOpened():
#         raise Exception("Cannot open camera")
    
#     return cap

def _open_capture(source):
    """Open the right capture backend based on source type"""
    if isinstance(source, int):
        cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)   # local webcam on Windows
    else:
        cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)  # RTSP / HTTP stream

    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # always keep buffer minimal
    return cap

def run_camera(camera_id, source, stop_flag: threading.Event):
    print(f"[{camera_id}] Starting...")

    # Load known faces once at startup
    known_encodings, known_names = load_known_faces()
    last_reload   = time.time()
    last_intruder = 0
    last_seen     = {}   # {name: last_event_timestamp} — per-person cooldown
    frame_count   = 0

    # Convert "0" / "1" string from MongoDB → int for OpenCV
    if isinstance(source, str) and source.isdigit():
        source = int(source)
        
    cap = _open_capture(source)

    
    if not cap.isOpened():
        print(f"[{camera_id}] ERROR: Cannot open camera source {source}")
        return
    
    print(f"[{camera_id}] Camera opened successfully")
    
    while not stop_flag.is_set():
        ret, frame = cap.read()
        
        if not ret:
            fail_count += 1
            if fail_count >= RECONNECT_AFTER:
                print(f"[{camera_id}] Stream lost — reconnecting...")
                cap.release()
                time.sleep(2)
                cap = _open_capture(source)
                fail_count = 0
            else:
                time.sleep(0.1)
            continue
        
        fail_count = 0  # reset on successful frame
        
        # ── Hot reload ──────────────────────────────────────
        # Picks up newly enrolled people without restarting
        
        # check_and_reload() returns True if the reload_counter is set to a 1, indicating that new enrollments have been processed and the camera should reload its known faces.
        if check_and_reload():
            print(f"[{camera_id}] New enrollment detected — reloading encodings...")
            known_encodings, known_names = load_known_faces()
            last_reload = time.time()
            # Don't clear the flag here — let ALL camera threads reload first

        # Fallback timer reload — catches any edge cases
        elif time.time() - last_reload > ENCODING_RELOAD_INTERVAL:
            print(f"[{camera_id}] Scheduled reload — reloading encodings...")
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
    
        # cv2.imshow(camera_id, frame)
        # # Press 'q' to quit this camera window
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
    
    # Clean exit
    cap.release()
    print(f"[{camera_id}] Stopped.")
        