# main.py
from camera.camera_manager import start_cameras
from events.event_worker import start_worker
from config import *
import time

print("Starting Guard Vision System")

# cap = start_camera(1)

start_worker()

start_cameras(CAMERAS)

while True:
    time.sleep(1)