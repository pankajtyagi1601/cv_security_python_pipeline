import cv2
import face_recognition

known_image = face_recognition.load_image_file("Pankaj.jpg")
known_encoding = face_recognition.face_encodings(known_image)[0];

# It could be a list of encodings if you have multiple known faces
known_faces = [known_encoding]
# known_names = ["Pankaj"] # Corresponding names for the known faces
known_names = ["Pankaj"]

#used to open camera feed
cap = cv2.VideoCapture(1)

# main to loop to read frames from the camera and perform face recognition
while True:
    # Read a frame from the camera, ret is a boolean indicating if the frame was read successfully, and frame is the actual image
    ret, frame = cap.read()
    
    # If frame not captured, skip to the next iteration of the loop
    if not ret:
        continue
    
    # Convert the frame from BGR color space (used by OpenCV) to RGB color space (used by face_recognition)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Detect faces in the RGB frame and get their locations (top, right, bottom, left) and encodings (128-dimension feature vector)
    face_locations = face_recognition.face_locations(rgb)
    
    # Get the face encodings for the detected faces in the current frame
    face_encodings = face_recognition.face_encodings(rgb, face_locations)
    
    # Loop through each detected face and its corresponding encoding
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Compare the detected face encoding with the known face encodings to see if there is a match
        matches = face_recognition.compare_faces(known_faces, face_encoding)
        
        # Initialize the name as "Unknown" and set the color for the rectangle to red because we assume it's unknown until we find a match
        name = "Unknown"
        color = (0, 0, 255)
        
        # If there is a match (i.e., if True is in the matches list), we change the color to green and set the name to the corresponding known name
        if True in matches:
            color = (0, 255, 0)
            name = "Pankaj Tyagi"
        
        # Draw a rectangle around the detected face in the original frame using the determined color (green for known, red for unknown). This rectangle is called a bounding box and is drawn using the coordinates (left, top) for the top-left corner and (right, bottom) for the bottom-right corner of the detected face.
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        
        # Put the name of the person (either the known name or "Unknown") above the rectangle. The text is drawn using the cv2.putText function, which takes the frame, the text to display, the position (left, top - 10) which is slightly above the rectangle, the font type, font scale, color, and thickness of the text.
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    
    # Display the resulting frame with the detected faces and their names in a window titled 'GuardVision Recognition'
    cv2.imshow('GuardVision Recognition', frame)
    
    # Wait for 1 millisecond and check if the 'q' key has been pressed. If it has, break the loop and exit the program. This allows the user to quit the face recognition system by pressing 'q'.
    if cv2.waitKey(1) == ord('q'):
        break

