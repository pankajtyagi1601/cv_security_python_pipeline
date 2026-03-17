#  enrollment/enrollment_processor.py
import requests
import numpy as np
import face_recognition
import cv2
from storage.database import save_authorized_people

def process_enrollment(name, image_url):
    """ What this function does?
    Downloads image from Cloudinary, computes 128D face encoding, then saves to MongoDB authorized_people collection.
    Returns (success: bool, message: str)
    """
    
    print(f"[Enrollment] Processing: {name}")
    
    # ── Step 1: Download image from Cloudinary ──────────────
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return False, f"Failed to download image for {name}: {e}"
    
    # ── Step 2: Decode bytes → numpy array ──────────────────
    # requests gives us raw bytes
    # np.frombuffer turns bytes into a 1D array of numbers
    # cv2.imdecode turns that array into a proper image matrix
    img_arr = np.frombuffer(response.content, np.uint8)
    bgr_frame = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
    
    if bgr_frame is None:
        return False, f"Image could not be decoded for {name} - may be corrupted"
    
    # face_recognition expects RGB, OpenCV gives BGR
    rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
   
    # ── Step 3: Compute 128D encoding ───────────────────────
    # This is the slow step — runs a neural network (~1-2 sec)
    encodings = face_recognition.face_encodings(rgb_frame)
    
    if len(encodings) == 0:
        return False, f"No face detected in image for '{name}'"
    
    if len(encodings) > 1:
        return False, f"Multiple faces detected in image for '{name}' - please upload a solo photo"
    
    # Convert numpy array → plain Python list for MongoDB storage
    encoding = encodings[0].tolist()
    
    # ── Step 4: Save to MongoDB ──────────────────────────────
    save_authorized_people(name, image_url, encoding)
    
    print(f"[Enrollment] Done: {name}")
    return True, f"{name} enrolled successfully"

