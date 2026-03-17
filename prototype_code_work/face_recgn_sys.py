import cv2
import face_recognition
import pickle
import numpy as np
import datetime
import os
import time
import sqlite3
from prototype_code_work.cloudinary_upload import upload_image

# -------------------- Creating directory for Intruder images & introducing intruduer variables  --------------------
os.makedirs("intruders", exist_ok=True)
# Cooldown variables to prevent multiple logs for the same person in a short period
last_intruder_time = 0
intruder_cooldown = 5

last_authorized_time = 0
authorized_cooldown = 10

# -------------------- Function to capture the frame with time format(especially Intruders) --------------------
def save_intruder(frame):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    temp_file = f"intruder_{timestamp}.jpg"
    cv2.imwrite(temp_file, frame)
    image_url = upload_image(temp_file)
    os.remove(temp_file)
    
    connect = sqlite3.connect("guardvision.db")
    cursor = connect.cursor()
    
    cursor.execute("""
        INSERT INTO events (timestamp, person_name, image_path, camera_id, event_type)
        VALUES (?, ?, ?, ?, ?)
    """, (timestamp, "UNKNOWN", image_url, "CAM_01", "INTRUDER"))

    connect.commit()
    connect.close()

    print(f"Intruder saved and logged: {image_url}")
    
# -------------------- Function to capture the frame with time format(especially Authorized) --------------------
def save_authorized(frame, person_name):

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # Save the authorized face image and log the event
    temp_file = f"authorized_{timestamp}.jpg"
    # Save the authorized face image to a temporary file before uploading to Cloudinary
    cv2.imwrite(temp_file, frame)
    # Upload the image to Cloudinary and get the secure URL
    image_url = upload_image(temp_file)
    # Remove the temporary file after uploading to Cloudinary
    os.remove(temp_file)

    connect = sqlite3.connect("guardvision.db")
    cursor = connect.cursor()

    cursor.execute("""
        INSERT INTO events (timestamp, person_name, image_path, camera_id, event_type)
        VALUES (?, ?, ?, ?, ?)
    """, (timestamp, person_name, image_url, "CAM_01", "AUTHORIZED"))

    connect.commit()
    connect.close()

    print(f"Authorized entry logged: {person_name}")

# -------------------- Load known faces --------------------
with open("encoding.pkl", "rb") as f:
    data = pickle.load(f)

known_faces_encodings = np.array(data["encodings"])
known_faces_names = data["names"]

print(len(known_faces_encodings))
print(known_faces_names)

# -------------------- Initialize Video Capture --------------------
cap = cv2.VideoCapture(1)

# Optionally, check if camera opened successfully
if not cap.isOpened():
    print("Error: Cannot open webcam")
    exit()

# -------------------- Parameters --------------------
process_every_n_frames = 2  # skip frames to reduce CPU
frame_count = 0
face_locations = []
face_encodings = []
face_names = []

# -------------------- Main Loop --------------------
while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame_count += 1

    # Resize frame for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Only process every n-th frame for efficiency
    if frame_count % process_every_n_frames == 0:
        face_locations = face_recognition.face_locations(rgb_small_frame, model="hog") # tried to use cnn but it is cpu expensive so using hog
        #hog model is fast and works well on CPU, but less accurate than deep learning for difficult images.
        #cnn model is much more accurate, especially on varied images but requires GPU for fast processing; slow on CPU.
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        face_names = []

        # Match each detected face encoding against known faces
        for encoding in face_encodings:
            distances = face_recognition.face_distance(known_faces_encodings, encoding)
            best_match_idx = np.argmin(distances)
            if distances[best_match_idx] < 0.5:
                name = known_faces_names[best_match_idx]
            else:
                name = "UNKNOWN"
            face_names.append(name)

    # Draw rectangles and names on the original frame
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up since we detected on a smaller frame
        top *= 2
        right *= 2
        bottom *= 2
        left *= 2

        current_time = time.time()

        # If the face is unknown, save the intruder image and log the event, but only if the cooldown has passed
        if name == "UNKNOWN":
            color = (0, 0, 255) # Red for intruders

            if current_time - last_intruder_time > intruder_cooldown: # Only save if cooldown has passed
                
                # Ensure the coordinates are within the frame boundaries
                top = max(0, top)
                left = max(0, left)
                bottom = min(frame.shape[0], bottom)
                right = min(frame.shape[1], right)

                # Extract the face region from the original frame using the scaled coordinates
                face_img = frame[top:bottom, left:right]
                
                # Save the intruder face image and log the event
                save_intruder(face_img)
                # Update the last intruder time to prevent multiple logs for the same person in a short period
                last_intruder_time = current_time
        else:
            color = (0, 255, 0) # Green for authorized

            if current_time - last_authorized_time > authorized_cooldown: # Only save if cooldown has passed

                # Scale back up since we detected on a smaller frame
                top = max(0, top)
                left = max(0, left)
                bottom = min(frame.shape[0], bottom)
                right = min(frame.shape[1], right)

                # Extract the face region from the original frame using the scaled coordinates
                face_img = frame[top:bottom, left:right]

                save_authorized(face_img, name)
                last_authorized_time = current_time           

        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    cv2.imshow("Guard Vision - AI Security System", frame)

    # Quit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()