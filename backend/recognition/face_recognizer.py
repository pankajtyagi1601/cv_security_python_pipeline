# recognition/face_recognizer.py
import face_recognition
import numpy as np
import pickle
import os

def load_known_faces():
    if not os.path.exists("encoding.pkl"):
        print("Warning: No encoding file found. All faces will be UNKNOWN.")
        return np.array([]), []
    
    with open("encoding.pkl", "rb") as f:
        data = pickle.load(f)
        
    return np.array(data["encoding"]), data["names"]

def recognize_faces(frame, known_encodings, known_names):
    locations = face_recognition.face_locations(frame, model="hog")
    encodings = face_recognition.face_encodings(frame, locations)
    
    names = []
    
    for encoding in encodings:
        distances = face_recognition.face_distance(known_encodings, encoding)
        
        best_match = np.argmin(distances)
        
        if distances[best_match] < 0.5:
            names.append(known_names[best_match])
        else:
            names.append("UNKNOWN")
            
    return locations, names        
        