# config.py
INTRUDER_COOLDOWN    = 5     # seconds between intruder alerts per camera
AUTHORIZED_COOLDOWN  = 10    # seconds between authorized alerts per person
PROCESS_EVERY_N_FRAMES = 2   # only run recognition on every 2nd frame
ENCODING_RELOAD_INTERVAL = 300  # reload known faces from DB every 5 minutes

import os
from dotenv import load_dotenv
load_dotenv()

REQUIRED_ENV_VARS = [
    "MONGO_URI",
    "REDIS_URL", 
    "CLOUD_NAME",
    "API_KEY",
    "API_SECRET"
]

def validate_env():
    missing = [v for v in REQUIRED_ENV_VARS if not os.getenv(v)]
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}\n"
                            f"Please check your .env file.")