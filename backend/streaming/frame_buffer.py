import threading

class FrameBuffer:
    """
    Thread-safe dictionary that stores the latest annotated frames for each camera.
    
    Camera threads -> call update() to write latest frame
    Flask Server -> calls get() to read latest frame for streaming
    
    Why a class and not just a plain dict?
    Beacuse 2 threads writing/reading simulataneously without a lock can cause a 
    race condition - one thread a half-written frame. The lock prevent this.   
    """
    
    def __init__(self):
        self._frames = {}
        self._lock = threading.Lock()
        
    def update(self, camera_id: str, frame_bytes: bytes):
        # Camera thread calls this after drawing annotations
        with self._lock:
            self._frames[camera_id] = frame_bytes
    
    def get(self, camera_id: str) -> bytes | None:
        # Flask thread calls this to get latest frame
        with self._lock:
            return self._frames.get(camera_id)
        
    def get_all_ids(self) -> list[str]:
        # Return list of all active camera IDs
        with self._lock:
            return list(self._frames.keys())
            
# Single instance shared across whole app
# Every files import this object - not the class
buffer = FrameBuffer()

# buffer is like a notice board
# Camera thread -> pins latest frame to notice board
# Flask Thread  -> reads from the notice board whenever browser asks
# Lock          -> only one person can touch the board at atime 