# enrollment/enrollment_subscriber.py
import threading, time
import json
from messaging.redis_client import get_redis
import traceback

from utils.logger import logger

ENROLLMENT_CHANNEL = "enrollment_channel"

def handle_message(payload: dict):
    """
    Runs in its own thread — subscriber never blocks.
    Heavy work (encoding) happens here, not in the listener loop.
    """
    try:
        if payload.get("action") == "reload_encodings":
            from camera.camera_manager import get_active_camera_count
            from recognition.face_recognizer import signal_reload
            from storage.database import set_encodings_dirty

            set_encodings_dirty()
            num_cameras = get_active_camera_count()
            logger.info(f"[Enrollment] reload_encodings — active threads: {num_cameras}")

            if num_cameras > 0:
                signal_reload(num_cameras)
                logger.info("[Enrollment] Camera threads notified to reload")
            else:
                logger.info("[Enrollment] No active cameras — dirty flag saved for next startup")
            return

        # ── Handle new enrollment ────────────────────────────────────
        name      = payload.get("name")
        image_url = payload.get("image_url")

        if not name or not image_url:
            logger.warning(f"[Enrollment] Invalid payload: {payload}")
            return

        # Process the enrollment - download, encode, save to DB
        from enrollment.enrollment_processor import process_enrollment
        success, msg = process_enrollment(name, image_url)

        # success, msg = process_enrollment(name, image_url)
        if success:
            logger.info(f"[Enrollment] Success: {msg}")
        else:
            logger.error(f"[Enrollment] Failed: {msg}")

    except Exception as e:
        logger.error(f"[Enrollment] Handler error: {e}")
        traceback.print_exc()


def listen_for_enrollments():
    """ What this function does:
    Subscribes to Redis enrollment_channel.
    Blocks forever — wakes up ONLY when a message arrives.
    Zero CPU usage while waiting.
    """
    while True:
        try:
            # For Pub/Sub we need a SEPARATE Redis connection
            # The main redis_client is used for publishing
            # A subscriber connection can ONLY listen — it can't do anything else
            r       = get_redis()
            pubsub  = r.pubsub()
            
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
                    threading.Thread(
                        target=handle_message,
                        args=(payload,),
                        daemon=True
                    ).start()
                    
                except json.JSONDecodeError:
                    logger.error(f"[Enrollment] Could not parse message: {message['data']}")
                
                except Exception as e:
                    logger.error(f"[Enrollment] Unexpected error: {e}")
                    traceback.print_exc()
        
        except Exception as e:
           # Connection dropped — wait and reconnect
            logger.error(f"[Enrollment] Redis connection lost: {e}")
            logger.info("[Enrollment] Reconnecting in 5 seconds...")
            time.sleep(5)  # wait before retry
        
            
def start_enrollment_subscriber():
    thread = threading.Thread(
        target=listen_for_enrollments,
        daemon=False
    )
    thread.start()
    logger.info("[Enrollment] Subscriber thread started")