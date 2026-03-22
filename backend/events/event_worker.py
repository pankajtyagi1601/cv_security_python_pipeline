# events/event_worker.py
import datetime
import cv2
import os
import threading
import glob
from storage.cloudinary_upload import upload_with_retry
from storage.database import log_event
from events.event_queue import event_queue
from utils.logger import logger 

def cleanup_temp_files():
    temp_files = glob.glob("temp_*.jpg")
    for file in temp_files:
        os.remove(file)
        logger.info(f"Cleaned up temp file: {file}")

def worker():
    logger.info("Event worker started")

    while True:
        # Blocks here — zero CPU usage until an event arrives
        event_type, frame, name, camera_id = event_queue.get()
        temp_file = None
        
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            temp_file = f"temp_{camera_id}_{event_type}_{timestamp}.jpg"
        
            # Save face crop disk temporarily
            cv2.imwrite(temp_file, frame)
        
            #Upload to the Cloudinary - get permanent URL
            image_url = upload_with_retry(temp_file)
        
            # Delete temp file immediately
            os.remove(temp_file)
            temp_file = None  # Avoid trying to delete again in case of error
        
            # Log to MongoDB
            log_event(timestamp, name, image_url, camera_id, event_type)
            
            logger.info(f"Event logged: {event_type} | {name} | {camera_id}")
        
        except Exception as e:
            logger.error(f"Event worker error: {e}")
            # clean up temp file if upload failed
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
                logger.warning(f"Cleaned up failed temp file: {temp_file}")
        
        finally:
            # Always mark done even if something failed
            event_queue.task_done()
        
def start_event_worker():
    thread = threading.Thread(target=worker, daemon= True)
    thread.start()