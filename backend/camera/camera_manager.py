# camera/camera_manager.py
import threading
from camera.camera_stream import run_camera
from utils.logger import logger

_active_cameras: dict[str, threading.Event] = {}
_lock = threading.Lock()

def start_cameras(camera_list):
    logger.info(f"Starting {len(camera_list)} camera(s)...")
    
    for camera in camera_list:
        _start_camera(camera["id"], camera["source"])
        
def _start_camera(camera_id, source):
    # Internal helper to start a single camera thread
    """Spawn a single camera thread with its own flag."""
    
    with _lock:
        if camera_id in _active_cameras:
            logger.warning(f"{camera_id} Already running - skipping.")
            return
        
        stop_flag = threading.Event()
        _active_cameras[camera_id] = stop_flag
    
    thread = threading.Thread(
        target=run_camera,
        args = (camera_id, source, stop_flag),
        daemon=True
    )
    
    thread.start()
    logger.info(f"{camera_id} Started on source {source}")
    
def stop_camera(camera_id):
    """Signal a specific camera thread to stop."""
    
    with _lock:
        flag = _active_cameras.pop(camera_id, None)
        
    if flag:
        flag.set() # Signal the thread to exit on next frame
        logger.info(f"{camera_id} Stop signal sent.")
    else:
        logger.warning(f"{camera_id} Not found among active cameras.")
        
def add_camera(camera_id, source):
    """Called by camera_subscriber when admins add a new camera."""
    _start_camera(camera_id, source)
    
def get_active_camera_ids():
    with _lock:
        return list(_active_cameras.keys())