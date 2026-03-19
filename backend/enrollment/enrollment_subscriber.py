# enrollment/enrollment_subscriber.py
import threading
import json
from messaging.redis_client import get_redis
from enrollment.enrollment_processor import process_enrollment
import traceback

from utils.logger import logger

ENROLLMENT_CHANNEL = "enrollment_channel"

def listen_for_enrollments():
    """ What this function doe/:
    Subscribes to Redis enrollment_channel.
    Blocks forever — wakes up ONLY when a message arrives.
    Zero CPU usage while waiting.
    """
    
    # For Pub/Sub we need a SEPARATE Redis connection
    # The main redis_client is used for publishing
    # A subscriber connection can ONLY listen — it can't do anything else
    r = get_redis()
    pubsub = r.pubsub()
    
    # Tell Redis: "I want to receive messages on this channel"
    pubsub.subscribe(ENROLLMENT_CHANNEL)
    logger.info(f"[Enrollment] Subscribed to channel: {ENROLLMENT_CHANNEL}")
    
    # listen() blocks here — Python sleeps until a message arrives
    # When Next.js publishes → this loop wakes up with the message
    for message in pubsub.listen():
        # Redis sends a "subscribe confirmation" message first when you connect
        # It looks like: {"type": "subscribe", "data": 1}
        # We only want actual data messages
        if message["type"] != "message":
            continue
        
        try:
            # message["data"] is the JSON string Next.js published
            # e.g. '{"name": "Rahul", "image_url": "https://cloudinary..."}'
            payload = json.loads(message["data"])
            
            # ── Handle reload signal (triggered when person is deleted) ──
            if payload.get("action") == "reload_encodings":
                from storage.database import get_active_camera_count
                from recognition.face_recognizer import signal_reload
                num_cameras = get_active_camera_count()
                signal_reload(num_cameras)
                logger.info("[Enrollment] Encoding reload triggered by dashboard")
                continue
            
            # ── Handle new enrollment ────────────────────────────────────
            name = payload.get("name")
            image_url = payload.get("image_url")
            
            if not name or not image_url:
                logger.warning(f"[Enrollment] Invalid payload: {payload}")
                continue
            
            # Process the enrollment - download, encode, save to DB
            success, msg = process_enrollment(name, image_url)
            
            if success:
                logger.info(f"[Enrollment] Success: {msg}")
            else:
                logger.error(f"[Enrollment] Failed: {msg}")
        
        except json.JSONDecodeError:
            logger.error(f"[Enrollment] Could not parse message: {message['data']}")
        
        except Exception as e:
            logger.error(f"[Enrollment] Unexpected error: {e}")
            traceback.print_exc()
            
def start_enrollment_subscriber():
    thread = threading.Thread(
        target=listen_for_enrollments,
        daemon=False
    )
    thread.start()
    logger.info("[Enrollment] Subscriber thread started")