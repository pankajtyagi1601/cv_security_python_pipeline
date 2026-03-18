# main.py
from camera.camera_manager import start_cameras
from events.event_worker import start_event_worker
from enrollment.enrollment_subscriber import start_enrollment_subscriber
from enrollment.enrollment_pending_recover import recover_pending_enrollments
from config import *
import time

if __name__ == "__main__":
    print("=" * 40)
    print("  CV Security  — Starting up")
    print("=" * 40)

    start_event_worker()
    start_enrollment_subscriber()
    recover_pending_enrollments()
    start_cameras(CAMERAS)

    print("=" * 40)
    print("  All systems running  ")
    print("=" * 40)

    while True:
        time.sleep(1)