# recognition/face_recognizer.py
import face_recognition
import numpy as np
from storage.database import load_known_faces_from_db

def load_known_faces():
    
    # Wrapper so camera_stream only import from here not directly from db
    
    return load_known_faces_from_db()

def recognize_faces(frame, known_encodings, known_names):
    
    # Takes an RGB frame + known face data. Returns face locations and matched names.
    
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
        