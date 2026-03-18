# test_encoding.py — run this alone: python test_encoding.py
import face_recognition
import cv2
import numpy as np
import requests

# Use one of the Cloudinary URLs from your MongoDB enrollment_jobs
image_url = "https://res.cloudinary.com/da1pepz3s/image/upload/v1773752738/cv_security_people/ofvizsxeblmuyoozgbrg.jpg"  # paste your full URL

print("Downloading...")
response = requests.get(image_url, timeout=10)
print(f"Downloaded: {len(response.content)} bytes")

print("Decoding...")
img_arr = np.frombuffer(response.content, np.uint8)
bgr = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
print(f"Shape: {rgb.shape}")

print("Encoding — if this hangs or crashes, it's a dlib issue...")
encodings = face_recognition.face_encodings(rgb)
print(f"Done — found {len(encodings)} face(s)")