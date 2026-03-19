# storage/databse/py
from pymongo import MongoClient
from utils.logger import logger
from dotenv import load_dotenv
import datetime
import numpy as np
import os
import certifi

load_dotenv()

# Single Client instance - reused across all operations
client = MongoClient(
    os.getenv("MONGO_URI"),
    tls=True,
    tlsCAFile=certifi.where(),
    )

db = client['cv_security']

events_collection = db["events"]
people_collection = db["authorized_people"]
cameras_collection = db["cameras"]

# -----------------------Events-----------------------

def log_event(timestamp, person_name, image_url, camera_id, event_type):
    event = {
        "timestamp": timestamp,
        "person_name": person_name,
        "image_url": image_url,
        "camera_id": camera_id,
        "event_type": event_type
    }
    events_collection.insert_one(event)
    
# -----------------------Authorized People-----------------------
def save_authorized_people(name, image_url, encoding):
#     upsert = update if exists, insert if not.
#     So if admin re-enrolls same person with new photo, it updates — no duplicates.
    people_collection.update_one(
        {"name": name},
        {"$set": {
            "name": name,
            "image_url": image_url, 
            "encoding": encoding, 
            "enrolled_at": datetime.datetime.now()
        }},
        upsert=True
    )

def load_known_faces_from_db():
    people = list(people_collection.find({}))
    
    if not people:
        logger.warning("Warning: NO authorized people found in the database. All faces will be treated as UNKNOWN.")
        return np.array([]), []
    
    encodings = [np.array(p["encoding"]) for p in people]
    names = [p["name"] for p in people]
    
    logger.info(f"Loaded {len(people)} authorized people: {names}")
    return np.array(encodings), names

# -----------------------Cameras-----------------------
def load_cameras_from_db():
    """Called by main.py on startup instead of reading config.py"""
    cameras = list(cameras_collection.find({"active": True}))

    if not cameras:
        logger.warning("Warning: No cameras found in DB. Add cameras from the dashboard.")
        return []

    result = []
    for cam in cameras:
        result.append({
            "id":     cam["camera_id"],
            "source": cam["source"]
        })
        logger.info(f"Loaded camera: {cam['camera_id']} → {cam['source']}")

    return result

def get_active_camera_count():
    """How many camera threads are currently configured"""
    return cameras_collection.count_documents({"active": True})