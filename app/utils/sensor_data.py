import os
import requests
import logging
from dotenv import load_dotenv
from datetime import datetime
from firebase_admin import db


load_dotenv()

THINGSPEAK_API_KEY = os.getenv('THINGSPEAK_API_KEY')
THINGSPEAK_CHANNEL_ID = os.getenv('THINGSPEAK_CHANNEL_ID')
user_id = os.getenv("USER_ID")
cow_id = os.getenv("COW_ID")


def fetch_thingspeak_data():
    url = f'https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json?api_key={THINGSPEAK_API_KEY}&results=1'
    logging.info(" Fetching data from ThingSpeak...")
    
    response = requests.get(url)

    if response.status_code != 200:
        logging.error(f" Failed to fetch data from ThingSpeak: {response.status_code} - {response.text}")
        return None

    try:
        feed = response.json()['feeds'][0]
        logging.debug(f"📥 Raw Feed: {feed}")

        required_fields = ["field1", "field2", "field3", "field4", "field5", "field6", "field7"]
        for field in required_fields:
            if field not in feed or feed[field] is None:
                logging.error(f" Missing or null field: {field}")
                return None

        data = {
            "accelerometer": {
                "x": float(feed["field2"]),
                "y": float(feed["field3"]),
                "z": float(feed["field4"])
            },
            "gyroscope": {
                "x": float(feed["field5"]),
                "y": float(feed["field6"]),
                "z": float(feed["field7"])
            },
            "temperature": float(feed["field1"]),
            "timestamp": feed["created_at"]
        }

        logging.info(" Successfully parsed ThingSpeak data.")
        print (f"Data fetched: {data}")
        return data

    except (KeyError, TypeError, ValueError) as e:
        logging.exception(" Error parsing ThingSpeak response.")
        return None

def save_data_to_firebase(user_id, cow_id, data):
    try:
        timestamp = data["timestamp"].replace(":", "-")
        ref_path = f"users/{user_id}/cows/{cow_id}/readings"
        logging.info(f" Saving data to Firebase path: {ref_path}")
        ref = db.reference(ref_path)
        ref.child(timestamp).set(data)
        logging.info(f" Data successfully saved for cow '{cow_id}' at {timestamp}")
    except Exception as e:
        logging.exception(" Failed to save data to Firebase.")


def ingest_and_save():
    data = fetch_thingspeak_data()
    if data:
        user_id = os.getenv("USER_ID")
        cow_id = os.getenv("COW_ID")
        save_data_to_firebase(user_id, cow_id, data)
