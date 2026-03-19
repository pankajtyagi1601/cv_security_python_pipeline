# test_camera.py
import cv2

for i in range(3):
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)  # CAP_DSHOW = Windows DirectShow
    if cap.isOpened():
        print(f"Camera {i} → works ✅")
        cap.release()
    else:
        print(f"Camera {i} → not found ❌")