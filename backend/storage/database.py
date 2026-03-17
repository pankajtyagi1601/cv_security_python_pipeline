# -------------------- LOCAL DB --------------------
# storage/database.py

# import sqlite3

# def log_event(timestamp, person_name, image_url, camera_id, event_type):
#     connect = sqlite3.connect("guardVision.db")
#     cursor = connect.cursor()
    
#     query = """
#     INSERT INTO events (timestamp, person_name, image_path, camera_id, event_type)
#     VALUES (?, ?, ?, ?, ?)
#     """
    
#     cursor.execute(query, (timestamp, person_name, image_url, camera_id, event_type))
    
#     connect.commit()
#     connect.close()

# -------------------- CLOUD DB --------------------
from pymongo.mongo_client import MongoClient
import os 
from dotenv import load_dotenv
import numpy as np

load_dotenv() 

# Create a new client and connect to the server
client = MongoClient(os.getenv("MONGO_URI"))
db = client["cv_security"]

events_collection = db["events"]
people_collection = db["authorized_people"]

def log_event(timestamp, person_name, image_url, camera_id, event_type):
    events_collection.insert_one({
        "timestamp": timestamp,
        "person_name": person_name,
        "image_url": image_url,
        "camera_id": camera_id,
        "event_type": event_type
    })
    
def save_authorized_people(name, img_url, encoding):
    people_collection.update_one(
        {"name": name},
        {"$set": {
            "name": name,
            "img_url": img_url,
            "encoding": encoding
        }},
        upsert=True
    )
    
def load_known_faces_from_db():
    people = list(people_collection.find({}))
    
    if not people:
        print("Warning: No authorized people in DB. Running in detection-only mode.")
        return np.array([]), []
    
    encodings = [np.array(p["encoding"]) for p in people]
    names = [p["name"] for p in people]
    
    print(f"Load {len(names)} authorized person(s) from DB: {names}")
    return np.array(encodings), names