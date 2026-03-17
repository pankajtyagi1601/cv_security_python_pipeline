# events/event_worker.py
import datetime
import cv2
import os
import threading

from storage.cloudinary_upload import upload_image
from storage.database import log_event
from events.event_queue import event_queue 

def workder():
    while True:
        event_type, frame, name, camera_id = event_queue.get()
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        temp_file = f"{event_type}_{timestamp}.jpg"
        
        cv2.imwrite(temp_file, frame)
        
        image_url = upload_image(temp_file)
        
        os.remove(temp_file)
        
        log_event(timestamp, name, image_url, camera_id, event_type)
        
        event_queue.task_done()
        
def start_worker():
    thread = threading.Thread(target=workder, daemon= True)
    thread.start()