# events/event_worker.py
import datetime
import cv2
import os
import threading

from storage.cloudinary_upload import upload_image
from storage.database import log_event
from events.event_queue import event_queue 

def workder():
    print("Event worker started")

    while True:
        # Blocks here — zero CPU usage until an event arrives
        event_type, frame, name, camera_id = event_queue.get()
        
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            temp_file = f"{event_type}_{timestamp}.jpg"
        
            # Save face crop disk temporarily
            cv2.imwrite(temp_file, frame)
        
            #Upload to the Cloudinary - get permanent URL
            image_url = upload_image(temp_file)
        
            # Delete temp file immediately
            os.remove(temp_file)
        
            # Log to MongoDB
            log_event(timestamp, name, image_url, camera_id, event_type)
            
            print(f"Event logged: {event_type} | {name} | {camera_id}")
        
        except Exception as e:
            print(f"Event worker error: {e}")
        
        finally:
            # Always mark done even if something failed
            event_queue.task_done()
        
def start_event_worker():
    thread = threading.Thread(target=workder, daemon= True)
    thread.start()