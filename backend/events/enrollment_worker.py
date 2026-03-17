import threading
import requests
import numpy as np
import face_recognition
import cv2
import os
from events.enrollment_queue import enrollment_queue
from storage.database import save_authorized_person, load_known_faces_from_db

def process_enrollment(name, img_url):
    # Step 1: Download the image from Cloudinary
    response = requests.get(img_url)
    
    if response.status_code != 200:
        print(f"Enrollment failed: could not damange image for {name}")
        return 
    
    # Step 2: Convert raw bytes -> numpy array OPpenCV can read
    image_array = np.frombuffer(response.content, np.uint8)
    bgr_frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    rgb_frame = cv2.cvtColor(bgr_frame, cv2.Color_BGR2RGB)
    
    # Step 3: Compute the 128D encoding - the slow step
    encoding = encoding[0].tolist()
    
    save_authorized_person(name, img_url, encoding)
    print(f"Enrolled: {name} - encoding saved to DB")
    
def enrollment_worker():
    while True:
        name, img_url = enrollment_queue.get()
        print(f"Processing enrollment for: {name}")
        
        try:
            process_enrollment(name, img_url)
        except Exception as e:
            print(f"Enrollment error for {name}: {e}")
            
        enrollment_queue.task_done()
        
def start_enrollment_worker():
    thread = threading.Thread(target=enrollment_worker, daemon=True)
    thread.start()
    print("Enrollment work started")