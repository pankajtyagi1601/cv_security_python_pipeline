# main.py
from camera.camera_manager import start_cameras
from events.event_worker import start_event_worker
from enrollment.enrollment_subscriber import start_enrollment_subscriber
from config import *
import time

print("=" * 40)
print("  CV Security  — Starting up")
print("=" * 40)

# Start event worker first — ready before cameras fire events
start_event_worker()

# Start enrollment subscriber — ready before any admin uploads
start_enrollment_subscriber()

start_cameras(CAMERAS)

print("=" * 40)
print("  All systems running  ")
print("=" * 40)

# Keep main thread alive — without this Python exits immediately and kills all daemon threads
while True:
    time.sleep(1)