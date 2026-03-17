import os
from queue import Queue
import threading
import datetime
import cv2
from prototype_code_work.cloudinary_upload import upload_image
import sqlite3

event_queue = Queue()

def event_worker():
    while True:
        event_type, frame, person_name = event_queue.get()
        
        time_stemp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        temp_file = f"{event_type.lower()}_{time_stemp}.jpg"
        
        cv2.imwrite(temp_file, frame) 
        
        image_url = upload_image(temp_file)
        
        os.remove(temp_file)
        
        connect = sqlite3.connect("guard_vision.db")
        
        corsor = connect.cursor() # corsor is used to execute the SQL queries
        query = """
        INSERT INTO events (timestamp, person_name, image_path, camera_id, event_type)
        VALUES(?, ?, ?, ?, ?)"""
        corsor.execute(query, (time_stemp, person_name, image_url, "CAM_01", event_type))
        
        connect.commit()
        connect.close()
        
        print(f"{event_type} logged:", person_name)
        
        event_queue.task_done()

# threading.Thread(...) -> This creates a new thread (a separate worker).
# target -> This tells thread which function it should run.
# daemon= True -> means the Thread will runs in the background and it automatically stops when the main program exits. If daemon=False, the program would wait for the thread to finish before exiting      
worker_thread = threading.Thread(target=event_worker, daemon=True)

worker_thread.start()