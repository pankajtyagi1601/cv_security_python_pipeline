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
            print(f"Warning: No face found in {filename}, skipping.")
            continue
        
        encodings.append(face_encodings[0])
        names.append(name)
        print(f"Encoded: {name}")
        
        with open("encoding.pkl", "wb") as f:
            pickle.dump({"encoding": encodings, "names": names}, f)
            
        print(f"Done. {len(name)} faces encoded.")
        
if __name__ == "__main__":
    encode_faces()