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
    
    known_encodings, known_names = load_known_faces()

    cap = cv2.VideoCapture(source)
    
    last_intruder = 0
    last_seen = {}
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            continue
        
        small_frame  = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    
        locations, names = recognize_faces(rgb_frame, known_encodings, known_names)
    
        for(top, right, bottom, left), name in zip(locations, names):
            top *= 2 
            bottom *=2
            right *= 2
            left *= 2
            
            now = time.time()
        
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
        