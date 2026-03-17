import redis
import os 
from dotenv import load_dotenv

load_dotenv()

# decode_responses=True means Redis returns strings instead of raw bytes
# ssl=True is required for Upstash — their free tier enforces encrypted connections

redis_url = os.getenv("REDIS_URL")

print(redis_url)
redis_client = redis.from_url(
    redis_url,
    decode_responses=True,
    ssl_cert_reqs=None # Upstash free tier doesn't require cert verification
) 

def get_redis():
    return redis_client