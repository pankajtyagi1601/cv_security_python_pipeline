# recognition/face_recognizer.py
from utils.logger import logger
import threading
import face_recognition
import numpy as np
from storage.database import load_known_faces_from_db

# ─── Thread Safety Lock ────────────────────────────────────────────────────────
#
# PROBLEM: dlib (the C++ library powering face_recognition) is NOT thread-safe.
# Multiple threads calling face_recognition functions simultaneously causes a
# memory conflict that silently crashes the entire Python process on Windows.
#
# SOLUTION: A threading.Lock() acts as a single-key room — only ONE thread can
# run dlib code at a time. Other threads wait at the "with dlib_lock:" line
# until the current thread finishes and releases the lock.
#
# WHY defined here (not in main.py or enrollment_processor.py):
# This module is imported by BOTH camera_stream.py and enrollment_processor.py.
# Defining the lock here means both files share the EXACT same lock object.
# If each file created its own lock, they'd be independent — no protection.
dlib_lock = threading.Lock()

#  Shared flag — enrollment worker sets this after saving a new person
# Camera threads check this and reload immediately instead of waiting for the next periodic reload
reload_lock = threading.Lock()
reload_counter = [0]  # Mutable counter to track reloads (for debugging/logging)

def signal_reload(num_cameras=1):
    """Called by enrollment_processor after saving to DB"""
    with reload_lock:
        reload_counter[0] = num_cameras
        logger.info(f"[Reload] Signal sent to {num_cameras} camera thread(s)")


def check_and_reload():
    """
    Called by each camera thread every frame.
    Returns True if this thread should reload encodings.
    """
    with reload_lock:
        if reload_counter[0] > 0:
            reload_counter[0] -= 1
            return True
    return False

def load_known_faces():
    
    # Wrapper so camera_stream only import from here not directly from db
    
    return load_known_faces_from_db()

def recognize_faces(frame, known_encodings, known_names):
    
    # Takes an RGB frame + known face data. Returns face locations and matched names.
    # Acquire the lock before ANY dlib call.
    # If enrollment_processor is currently encoding a face, camera threads
    # will pause here (~50ms max) until encoding finishes — then continue.
    # This tiny pause is invisible in practice but prevents the crash.
    with dlib_lock:  # camera threads wait here if encoding is running
        locations = face_recognition.face_locations(frame, model="hog")
        encodings = face_recognition.face_encodings(frame, locations)
    
    names = []
    
    for encoding in encodings:
        # No authorized people enrolled yet — everything is UNKNOWN
        if len(known_encodings) == 0:
            names.append("UNKNOWN")
            continue

        distances = face_recognition.face_distance(known_encodings, encoding)
        best_match = np.argmin(distances)
        
        if distances[best_match] < 0.5:
            names.append(known_names[best_match])
        else:
            names.append("UNKNOWN")
            
    return locations, names        
        