import os
import face_recognition
import cv2

known_faces_encoding = []
known_faces_names = []

cap =cv2.VideoCapture(1)

dataset_path = "known_faces" 

for person_name in os.listdir(dataset_path):
    
    person_folder = os.path.join(dataset_path, person_name)
    
    if not os.listdir(person_folder):
        continue
    
    for file in os.listdir(person_folder):
        if not file.lower().endswith((".jpg", "jpeg", ".png")):
            continue
        
        image_path = os.path.join(person_folder, file)
        
        image = face_recognition.load_image_file(image_path)
        
        image_encoding = face_recognition.face_encodings(image)
        
        if len(image_encoding) > 0:
            known_faces_encoding.append(image_encoding[0])
            known_faces_names.append(person_name) 
            
print("Loaded dataset", len(known_faces_encoding), ":", known_faces_names)
        
        
while True :
    ret, frame = cap.read()
     
    if not ret:
        continue
    
    small_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
    rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    
    face_locations_in_frame = face_recognition.face_locations(rgb)
    face_encoding_of_located_faces = face_recognition.face_encodings(rgb, face_locations_in_frame)
    
    for(top, right, bottom, left), facial_encoding in zip(face_locations_in_frame, face_encoding_of_located_faces):
        matches = face_recognition.compare_faces(known_faces_encoding, facial_encoding)
        
        name = "Unknown"
        bounding_box_color = (0, 0, 255)
        
        if True in matches:
            match_idx = matches.index(True)
            name = known_faces_names[match_idx]
            bounding_box_color = (0, 255, 0)
            
        top*=4
        bottom*=4
        left*=4
        right*=4
        
        cv2.rectangle(frame, (left, top), (right, bottom), bounding_box_color, 2)
        # cv2.putText(image, text, position, font, fontScale, color, thickness)
        cv2.putText(frame, name, (left, top-2), cv2.FONT_HERSHEY_SIMPLEX, 0.9, bounding_box_color, 1)
        
    cv2.imshow("Gurad Vision", frame)
    
    if(cv2.waitKey(1)==ord('q')):
        break
    
cap.release()
cv2.destroyAllWindows()
     