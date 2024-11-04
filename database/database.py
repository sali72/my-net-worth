import os
import mongoengine
from dotenv import load_dotenv

load_dotenv()

MONGO_DATABASE = os.getenv("MONGO_DATABASE")
MONGO_ROOT_USERNAME = os.getenv("MONGO_ROOT_USERNAME")
MONGO_ROOT_PASSWORD = os.getenv("MONGO_ROOT_PASSWORD")
MONGO_HOST = os.getenv("MONGO_HOST")

MONGO_LOCAL_HOST = os.getenv("MONGO_LOCAL_HOST")
TEST_MODE = os.getenv("TEST_MODE")

def connect_to_db():
    if TEST_MODE == "true":
        mongoengine.connect(
            db=MONGO_DATABASE,
            host=MONGO_LOCAL_HOST,
            port=27017
        )
    else:
        mongoengine.connect(
            db=MONGO_DATABASE,
            host=MONGO_HOST,
            port=27017,
            username=MONGO_ROOT_USERNAME,
            password=MONGO_ROOT_PASSWORD,
            authentication_source='admin'
        )
    print("Connected to MongoDB")
