# camera/camera_stream.py
import cv2, numpy as np
import time, datetime
import threading
from recognition.face_recognizer import recognize_faces, load_known_faces, check_and_reload
from events.event_queue import event_queue
from config import *
from utils.logger import logger
from streaming.frame_buffer import buffer
import platform

RECONNECT_AFTER = 30  # consecutive failed frames before attempting reconnect
ANNOTATION_PERSIST = 2.0

def _open_capture(source):
    """Open the right capture backend based on source type"""
    if isinstance(source, int):
        # CAP_DSHOW is Windows only — use default on Linux
        if platform.system() == "Windows":
            cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(source)
    else:
        cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)  # RTSP / HTTP stream

    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # always keep buffer minimal
    return cap

def draw_annotations(frame, scaled_loactions, names, camera_id):
    """
    Draws bounding boxes, labels and camera overlaay on the frame.
    Returns the annotated frame - original frame is not modified.
    
    Color coding:
    Green -> AUTHORIZED person (name found in known_names)
    Red   -> UNKNOWN / INTRUDER
    """
    annotated = frame.copy()    #copying so that original frames remians
    height, width = annotated.shape[:2]
    
    for (top, right, bottom, left), name in zip(scaled_loactions, names):        
        is_authorized = name != "UNKNOWN"
        color = (0, 255, 0) if is_authorized else (0, 0, 255) #cv2 reads frames in BGR format
        label = name if is_authorized else "UNKNOWN"
        
        # ── Bounding Box ──────────────────────────────────────
        cv2.rectangle(annotated, (left, top), (right, bottom), color, 2)
        
        # ── Label background - makes text readable ──────────────────────────────────────
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
        cv2.rectangle(
            annotated,
            (left, top - label_size[1] - 12),
            (left + label_size[0] + 8, top),
            color,
            -1  # filled rectangle
        ) 
        
        # ── Label text ──────────────────────────────────────
        cv2.putText(
            annotated, label,
            (left + 4, top - 6),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6,
            (255, 255, 255),   # white text on colored background
            1, cv2.LINE_AA
        )
        
    # Camera info bar at bottom
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d  %H%M:%S")
    overlay = f"{camera_id} | {timestamp}"
    
    # Semi-transparent black bar at bottom
    bar_height = 28
    cv2.rectangle(
        annotated,
        (0, height - bar_height),
        (width, height),
        (0, 0, 0),
        -1
    )
    cv2.putText(
        annotated, overlay, (8, height - 8),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5,
        (200, 200, 200), 1, cv2.LINE_AA
    )

    return annotated
        
def encode_frame(frame, quality=70):
    """Helper — encode numpy frame to JPEG bytes"""
    # Ensure frame is valid before encoding
    if frame is None or frame.size == 0:
        return None
    if frame.dtype != np.uint8:
        frame = frame.astype(np.uint8)
    _, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return jpeg.tobytes()

def run_camera(camera_id:str, source, stop_flag: threading.Event):
    logger.info(f"[{camera_id}] Starting...")

    # Load known faces once at startup
    known_encodings, known_names = load_known_faces()
    last_reload   = time.time()
    last_intruder = 0
    last_seen     = {}   # {name: last_event_timestamp} — per-person cooldown
    frame_count   = 0
    fail_count    = 0
    last_annotated = None
    last_detection_time = 0
    
    # Checking if encodings changed while camera was offline
    from storage.database import is_encodings_dirty, clear_encodings_dirty
    if is_encodings_dirty():
        logger.info(f"[{camera_id}] Encodings were changed offline — reloading...")
        known_encodings, known_names = load_known_faces()
        clear_encodings_dirty()

    # Convert "0" / "1" string from MongoDB → int for OpenCV
    if isinstance(source, str) and source.isdigit():
        source = int(source)
        
    cap = _open_capture(source)

    
    if not cap.isOpened():
        logger.error(f"[{camera_id}] ERROR: Cannot open camera source {source}")
        return
    
    logger.info(f"[{camera_id}] Camera opened successfully")
    
    while not stop_flag.is_set():
        ret, frame = cap.read()
        
        if not ret:
            fail_count += 1
            if fail_count >= RECONNECT_AFTER:
                logger.warning(f"[{camera_id}] Stream lost — reconnecting...")
                cap.release()
                time.sleep(2)
                cap = _open_capture(source)
                fail_count = 0
                last_annotated = None
            else:
                time.sleep(0.1)
            continue
        
        fail_count = 0  # reset on successful frame
        
        # ── Hot reload ──────────────────────────────────────
        # Picks up newly enrolled people without restarting
        
        # check_and_reload() returns True if the reload_counter is set to a 1, indicating that new enrollments have been processed and the camera should reload its known faces.
        if check_and_reload():
            logger.info(f"[{camera_id}] New enrollment detected — reloading encodings...")
            known_encodings, known_names = load_known_faces()
            last_reload = time.time()
            last_annotated = None
            last_detection_time = 0
            # Don't clear the flag here — let ALL camera threads reload first

        # Fallback timer reload — catches any edge cases
        elif time.time() - last_reload > ENCODING_RELOAD_INTERVAL:
            logger.info(f"[{camera_id}] Scheduled reload — reloading encodings...")
            known_encodings, known_names = load_known_faces()
            last_reload = time.time()
            last_annotated      = None      
            last_detection_time = 0

            
        # ── Skip frames for performance ─────────────────────
        frame_count += 1
        is_recognition_frame = (frame_count % PROCESS_EVERY_N_FRAMES == 0)
        
        if is_recognition_frame:    
            # ── Run recognition on this frame ────────────────
            # ── Preprocess ──────────────────────────────────────
            small_frame  = cv2.resize(frame, (0,0), fx=0.6, fy=0.6)
            # Ensure frame is 8-bit BGR before color conversion
            # HTTP/ngrok streams sometimes return frames in unexpected formats
            if small_frame.dtype != np.uint8:
                small_frame = small_frame.astype(np.uint8)

            # Handle both grayscale and BGRA frames from HTTP streams
            if len(small_frame.shape) == 2:
                # Grayscale → convert to RGB
                rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_GRAY2RGB)
            elif small_frame.shape[2] == 4:
                # BGRA → convert to RGB
                rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGRA2RGB)
            else:
                # Normal BGR → convert to RGB
                rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # ── Recognize ───────────────────────────────────────
            locations, names = recognize_faces(rgb_frame, known_encodings, known_names)
            
            # ── Draw annotations + update buffer ─────────────────
            if locations:
                # Scale coordinates ONCE here — used by both draw and events
                scaled = [
                    (int(top / 0.6), int(right / 0.6), int(bottom / 0.6), int(left / 0.6))
                    for (top, right, bottom, left) in locations
                ]
                
                annotated = draw_annotations(frame, scaled, names, camera_id)
                last_annotated = encode_frame(annotated)
                last_detection_time = time.time()          # stamp when we last saw a face
                buffer.update(camera_id, last_annotated)

                # ── Handle each detected face ────────────────────────
                for(top, right, bottom, left), name in zip(scaled, names):            
                
                    # Guard: face at frame edge can produce empty crop
                    face_img = frame[top:bottom, left:right]
                    if face_img.size == 0:
                        continue
                    
                    now = time.time()
                    
                    if name == "UNKNOWN":
                        if now - last_intruder > INTRUDER_COOLDOWN:
                            event_queue.put(("INTRUDER", face_img, name, camera_id))
                            last_intruder = now
                    else:
                        if now - last_seen.get(name, 0) > AUTHORIZED_COOLDOWN:
                            event_queue.put(("AUTHORIZED", face_img, name, camera_id))
                            last_seen[name] = now
                            
            else:
                if time.time() - last_detection_time > ANNOTATION_PERSIST:
                    last_annotated = None
                    jpeg = encode_frame(frame)
                    if jpeg:
                        buffer.update(camera_id, jpeg)
                else:
                    buffer.update(camera_id, last_annotated if last_annotated else encode_frame(frame))
        
        else:
            # ── Non-recognition frame ─────────────────────────
            if last_annotated and (time.time() - last_detection_time <= ANNOTATION_PERSIST):
                # Face was detected recently — keep showing annotated frame
                # This is the key fix — boxes persist between recognition cycles
                buffer.update(camera_id, last_annotated)
            else:
                # No recent detection — show raw frame
                last_annotated = None
                jpeg = encode_frame(frame)
                if jpeg:
                    buffer.update(camera_id, jpeg)
    
    # Clean exit
    cap.release()
    logger.info(f"[{camera_id}] Stopped.")
        