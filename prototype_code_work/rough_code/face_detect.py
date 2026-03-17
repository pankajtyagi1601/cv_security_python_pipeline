import cv2
import face_recognition
# import numpy as np

cap1 = cv2.VideoCapture(1) # for webcam
# cap2 = cv2.VideoCapture("http://10.166.199.35:4747/video") # for IP camera

while True:
    ret, frame = cap1.read()
    
    # If frame not captured, skip
    if not ret:
        continue
    
    # frame = frame.astype(np.uint8)

    # Convert BGR to RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Detect faces
    faces = face_recognition.face_locations(rgb)
    
    # Draw rectangle around each face
    for (top, right, bottom, left) in faces:
        cv2.rectangle(frame, (left, top), (right, bottom), (0,0, 255), 2)
        
    # Show video
    cv2.imshow('Face Detection', frame)
    
    if cv2.waitKey(1) == ord('q'):
        break

cap1.release()
cv2.destroyAllWindows()