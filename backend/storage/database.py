# storage/databse/py
from pymongo import MongoClient
from bson import ObjectId
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
        print("Warning: NO authorized people found in the database. All faces will be treated as UNKNOWN.")
        return np.array([]), []
    
    encodings = [np.array(p["encoding"]) for p in people]
    names = [p["name"] for p in people]
    
    print(f"Loaded {len(people)} authorized people: {names}")
    return np.array(encodings), names