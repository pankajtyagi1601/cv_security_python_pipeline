import cv2

url = "http://10.196.2.35:4747/video"
cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 👉 Apply transformation here
    frame = cv2.flip(frame, 1)  # mirror

    cv2.imshow("Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()