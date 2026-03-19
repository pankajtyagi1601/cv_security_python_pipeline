# recognition/encode_faces.py
from utils.logger import logger

import face_recognition
import os
import pickle

def encode_faces(images_folder="known_faces"):
    encodings = []
    names = []
    
    for filename in os.listdir(images_folder):
        if not filename.lower().endswith((".jpg", ".png", ".jpeg")):
            continue
        
        name = os.path.splitext(filename)[0]  #rahul.png -> rahul
        path  = os.path.join(images_folder, filename)
        
        image = face_recognition.load_image_file(path)
        face_encodings = face_recognition.face_encodings(image)
        
        if len(face_encodings) == 0:
            logger.warning(f"Warning: No face found in {filename}, skipping.")
            continue
        
        encodings.append(face_encodings[0])
        names.append(name)
        logger.info(f"Encoded: {name}")
        
    with open("encoding.pkl", "wb") as f:
        pickle.dump({"encoding": encodings, "names": names}, f)
            
    logger.info(f"Done. {len(names)} faces encoded.")
        
if __name__ == "__main__":
    encode_faces()