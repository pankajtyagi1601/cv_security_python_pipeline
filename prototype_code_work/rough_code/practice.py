# import cv2
# import face_recognition

# known_facial = face_recognition.load_image_file("Pankaj.jpg")
# known_encode = face_recognition.face_encodings(known_facial)[0]

# known_faces = [known_encode]
# known_names = ["Rahul", "Dexter"]
# # print(known_facial)
# # print(known_encode)

# cap = cv2.VideoCapture(1)

# process_this_frame = True

# while True:
#     ret, frame = cap.read()

#     if not ret:
#         continue

#     # cv2.resize(image, size, fx, fy)
#     # size = (0,0) means don't use fixed width and height instead use scale factors fx, fy
#     # fx , fy = 0.25 means scale the image 25% of its original size
#     # 1280 × 720  = 0.25*320 × 0.25*180
#     small_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
#     rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

#     if process_this_frame:
#         facial_locations = face_recognition.face_locations(rgb)
#         facial_encodings = face_recognition.face_encodings(rgb, facial_locations)
    
#     process_this_frame = not process_this_frame  

#     for(top, right, bottom, left), face_encoding in zip(facial_locations, facial_encodings):
#         matches = face_recognition.compare_faces([known_encode], face_encoding)

#         name = "UNKNOWN"
#         color = (0, 0, 255)

#         if True in matches:
#             match_idx = matches.index(True)
#             name = known_names[match_idx]            
#             color = (0, 255, 0)
            
#         top *=4
#         bottom *=4
#         right *= 4
#         left *= 4 

#         cv2.rectangle(frame, (left, top), (right, bottom), color, 3)
#         cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        
#     cv2.imshow("VisionProtector", frame)

#     if(cv2.waitKey(1)==ord('q')):
#         break

# cap.release()
# cv2.destroyAllWindows()



# print(os.listdir())

# import os 
# import cv2
# import face_recognition

# known_faces_encoding = []
# known_names = []

# dataset_path = "known_faces"

# for p in os.listdir(dataset_path):
#     p_folder = os.path.join(dataset_path, p)
    
#     if not os.path.isdir(p_folder):
#         continue
    
#     for file in os.listdir(p_folder):
#         if not file.lower().endswith((".jpg", ".jpeg", ".png")):
#                 conitinue
                
#         image_path = os.path.join(p_folder, file)
#         image = face_recognition.load_image_file(image_path)
#         encodings = face_recognition.face_encodings(image)
        
#         if len(encodings) > 0:
#             known_faces_encoding.append(encodings[0])
#             known_names.append(p)
#         else:
#             print("Face not detected in:", image_path)
                
# print("Loaded faces:", len(known_faces_encoding))
# print("People:", (known_names))


import os
import cv2
import face_recognition
from datetime import datetime

known_encodings = []
known_names = []

os.makedirs("logs", exist_ok=True)
os.makedirs("unknown_faces", exist_ok=True)

dataset_path = "known_faces"

# LOAD DATASET
for person_name in os.listdir(dataset_path):

    person_folder = os.path.join(dataset_path, person_name)

    if not os.path.isdir(person_folder):
        continue

    for file in os.listdir(person_folder):

        if not file.lower().endswith((".jpg",".jpeg",".png")):
            continue

        image_path = os.path.join(person_folder, file)
        image = face_recognition.load_image_file(image_path)

        encodings = face_recognition.face_encodings(image)

        if len(encodings) == 0:
            continue

        known_encodings.append(encodings[0])
        known_names.append(person_name)

print("Loaded Users:", set(known_names))

cap = cv2.VideoCapture(1)

while True:

    ret, frame = cap.read()
    if not ret:
        continue

    small_frame = cv2.resize(frame,(0,0),fx=0.25,fy=0.25)
    rgb_small = cv2.cvtColor(small_frame,cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small)
    face_encodings = face_recognition.face_encodings(rgb_small,face_locations)

    for (top,right,bottom,left),face_encoding in zip(face_locations,face_encodings):

        matches = face_recognition.compare_faces(known_encodings,face_encoding)

        name = "Unknown"
        color = (0,0,255)

        if True in matches:

            match_index = matches.index(True)
            name = known_names[match_index]
            color = (0,255,0)

        # else:

        #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        #     filename = f"unknown_faces/{timestamp}.jpg"

        #     cv2.imwrite(filename,frame)

        #     with open("logs/log.txt","a") as f:
        #         f.write(f"{timestamp} - Unknown Person Detected\n")

        top*=4
        right*=4
        bottom*=4
        left*=4

        cv2.rectangle(frame,(left,top),(right,bottom),color,3)

        cv2.putText(frame,name,(left,top-10),
                    cv2.FONT_HERSHEY_SIMPLEX,0.8,color,2)

    cv2.imshow("Guard Vision",frame)

    if cv2.waitKey(1)==ord('q'):
        break

cap.release()
cv2.destroyAllWindows()