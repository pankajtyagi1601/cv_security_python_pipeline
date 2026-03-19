import threading
import json
import traceback
from messaging.redis_client import get_redis

CAMERA_CHANNEL = "camera_channel"

def listen_for_camera_changes():
    """
    Subscribes to Redis camera_channel.
    Wakes up when admin add or removes a camera from the dashboard.
    """
    
    # imported here to avoid circular import
    from camera.camera_manager import add_camera, stop_camera
    r = get_redis()
    pubsub = r.pubsub()
    pubsub.subscribe(CAMERA_CHANNEL)
    
    print(f"[Camera] Subscribed to channel: {CAMERA_CHANNEL}")
    
    for message in pubsub.listen():
        if message['type'] != "message":
            continue
        
        try:
            payload = json.loads(message['data'])
            action = payload.get("action")
            camera_id = payload.get("camera_id")
            source = payload.get("source")
            
            if action == "add":
                print(f"[Camera] New camera signal: {camera_id} on source {source}")
                add_camera(camera_id, source)
                
            elif action == "remove":
                print(f"[Camera] Remove camera signal: {camera_id}")
                stop_camera(camera_id)
            
            else:
                print(f"[Camera] Unknown action: {action}")
        
        except json.JSONDecodeError:
            print(f"[Camera] Could not parse message: {message['data']}")
        
        except Exception as e:
            print(f"[Camera] Unexpected error: {e}")
            traceback.print_exc()
            
def start_camera_subscriber():
    thread = threading.Thread(
        target=listen_for_camera_changes,
        daemon=True
    )
    thread.start()
    print("[Camera] Subscriber thread started.")