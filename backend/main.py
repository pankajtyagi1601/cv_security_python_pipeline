# main.py
from camera.camera_manager import start_cameras
from camera.camera_subscriber import start_camera_subscriber
from events.event_worker import start_event_worker, cleanup_temp_files
from enrollment.enrollment_subscriber import start_enrollment_subscriber
from enrollment.enrollment_pending_recover import recover_pending_enrollments
from storage.database import load_cameras_from_db
from config import validate_env
from utils.logger import logger
import time

validate_env()  # Ensure all required environment variables are set before starting any services

if __name__ == "__main__":
    logger.info("=" * 40)
    logger.info("  CV Security  — Starting up")
    logger.info("=" * 40)
    
    cleanup_temp_files()  # Clean up any leftover temp files from previous runs on startup
    start_event_worker()
    start_enrollment_subscriber()
    start_camera_subscriber()  # Start subscriber BEFORE loading cameras — ensures we catch any add/remove signals during startup
    
    cameras = load_cameras_from_db()
    
    if not cameras:
        logger.info("No cameras configured — add cameras from the dashboard then restart.")
    else:
        start_cameras(cameras)
        
    recover_pending_enrollments()
    
    logger.info("=" * 40)
    logger.info("  All systems running  ")
    logger.info("=" * 40)

    while True:
        time.sleep(1)