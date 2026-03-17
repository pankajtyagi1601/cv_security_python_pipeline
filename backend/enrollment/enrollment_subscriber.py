# enrollment/enrollment_subscriber.py
import threading
import json
from messaging.redis_client import get_redis
from enrollment.enrollment_processor import process_enrollment

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
    print(f"[Enrollment] Subscribed to channel: {ENROLLMENT_CHANNEL}")
    
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
            
            name = payload.get("name")
            image_url = payload.get("image_url")
            
            if not name or not image_url:
                print(f"[Enrollment] Invalid payload: {payload}")
                continue
            
            # Process the enrollment - download, encode, save to DB
            success, msg = process_enrollment(name, image_url)
            
            if success:
                print(f"[Enrollment] Success: {msg}")
            else:
                print(f"[Enrollment] Failed: {msg}")
        
        except json.JSONDecodeError:
            print(f"[Enrollment] Could not parse message: {message['data']}")
        
        except Exception as e:
            print(f"[Enrollment] Unexpected error: {e}")
            
def start_enrollment_subscriber():
    thread = threading.Thread(
        target=listen_for_enrollments,
        daemon=True
    )
    thread.start()
    print("[Enrollment] Subscriber thread started")