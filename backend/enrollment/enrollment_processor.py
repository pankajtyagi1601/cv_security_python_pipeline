#  enrollment/enrollment_processor.py
import requests
import numpy as np
import face_recognition
import cv2
import traceback
from storage.database import save_authorized_people
from recognition.face_recognizer import dlib_lock

def process_enrollment(name, image_url):
    """ What this function does?
    Downloads image from Cloudinary, computes 128D face encoding, then saves to MongoDB authorized_people collection.
    Returns (success: bool, message: str)
    """
    
    print(f"[Enrollment] Processing: {name}")
    # print(f"[Enrollment] Step 1 — downloading image for {name}")
    
    # ── Step 1: Download image from Cloudinary ──────────────
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        # print(f"[Enrollment] Step 1 done — {len(response.content)} bytes downloaded")
    except Exception as e:
        traceback.print_exc()
        return False, f"Failed to download image for {name}: {e}"
    
    # ── Step 2: Decode bytes → numpy array ──────────────────
    # requests gives us raw bytes
    # np.frombuffer turns bytes into a 1D array of numbers
    # cv2.imdecode turns that array into a proper image matrix
    
    # print(f"[Enrollment] Step 2 — decoding image")
    try:
        img_arr = np.frombuffer(response.content, np.uint8)
        bgr_frame = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
        
        if bgr_frame is None:
            return False, f"Image could not be decoded for {name} - may be corrupted"
    
        # face_recognition expects RGB, OpenCV gives BGR
        rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
    except Exception as e:
        traceback.print_exc()
        return False, f"Image decode failed: {e}"
   
    # ── Step 3: Compute 128D encoding ───────────────────────
    # This is the slow step — runs a neural network (~1-2 sec)
    try:
        with dlib_lock:
            locations = face_recognition.face_locations(rgb_frame, model="hog")
            encodings = face_recognition.face_encodings(rgb_frame, locations)
    
        if len(encodings) == 0:
            return False, f"No face detected in image for '{name}'"
        
        if len(encodings) > 1:
            return False, f"Multiple faces detected in image for '{name}' - please upload a solo photo"
    
        # Convert numpy array → plain Python list for MongoDB storage
        encoding = encodings[0].tolist()
        
    except Exception as e:
        traceback.print_exc()
        return False, f"Face encoding failed: {e}"
    
    # ── Step 4: Save to MongoDB ──────────────────────────────
    try:
        save_authorized_people(name, image_url, encoding)
    except Exception as e:
        traceback.print_exc()
        return False, f"Database save failed: {e}"
    
    print(f"[Enrollment] Done: {name}")
    return True, f"{name} enrolled successfully"