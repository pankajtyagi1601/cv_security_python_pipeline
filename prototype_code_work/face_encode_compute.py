import os
import face_recognition
import pickle

dataset_path = "known_faces"

known_faces_encodings = []
known_faces_names = []

for person_name in os.listdir(dataset_path):
    person_folder = os.path.join(dataset_path, person_name)
    
    if not os.listdir(person_folder):
        continue
    
    for file in os.listdir(person_folder):
        if not file.lower().endswith(("jpg", "png", "jpeg")):
            continue
            
        image_path = os.path.join(person_folder, file)
        
        load_image = face_recognition.load_image_file(image_path)
        
        image_encoding = face_recognition.face_encodings(load_image)
        
        if len(image_encoding) > 0:
            known_faces_encodings.append(image_encoding[0])
            known_faces_names.append(person_name)
            
data = {
    "encodings" : known_faces_encodings,
    "names": known_faces_names
}
        
with open("encoding.pkl", "wb") as f:
    pickle.dump(data, f)
    
print("Encoding saved sucessfully!")
        