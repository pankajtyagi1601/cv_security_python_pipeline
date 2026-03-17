# camera/camera_manager.py
import threading
from camera.camera_stream import run_camera

def start_cameras(camera_list):
    print(f"Starting {len(camera_list)} camera(s)...")
    
    for camera in camera_list:
        
        t = threading.Thread(
            target = run_camera,
            args=(camera["id"], camera["source"]),
            daemon=True
        )
        
        t.start()
        
        print(f"Started: {camera['id']} on source {camera['source']}")