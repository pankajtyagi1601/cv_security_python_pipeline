# camera/camera_manager.py
import threading
from camera.camera_stream import run_camera

def start_cameras(camera_list):
    threads = []
    
    for camera in camera_list:
        
        t = threading.Thread(
            target = run_camera,
            args=(camera["id"], camera["source"]),
            daemon=True
        )
        
        t.start()
        
        threads.append(t)
        
        print(f"Started camera: {camera['id']}")

        
    return threads