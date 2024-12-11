import logging
import os

import mongoengine
from dotenv import load_dotenv
from mongoengine.connection import get_connection

from commons.logging_config import setup_logging
from database.initialize_db import (
    initialize_common_asset_types,
    initialize_common_categories,
    initialize_fiat_and_crypto_currencies,
)

load_dotenv()

MONGO_DATABASE = os.getenv("MONGO_DATABASE")
MONGO_ROOT_USERNAME = os.getenv("MONGO_ROOT_USERNAME")
MONGO_ROOT_PASSWORD = os.getenv("MONGO_ROOT_PASSWORD")
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_LOCAL_HOST = os.getenv("MONGO_LOCAL_HOST")
MONGO_ATLAS_CONNECTION_STRING = os.getenv("MONGO_ATLAS_CONNECTION_STRING")
DB_MODE = os.getenv("DB_MODE")


setup_logging()
logger = logging.getLogger(__name__)


async def connect_to_db():
    try:
        if DB_MODE == "true":
            mongoengine.connect(
                db=MONGO_DATABASE,
                host=MONGO_LOCAL_HOST,
                port=27017,
                serverSelectionTimeoutMS=10000,
            )
        elif DB_MODE == "container":
            mongoengine.connect(
                db=MONGO_DATABASE,
                host=MONGO_HOST,
                port=27017,
                # # Add username and pass if you want
                # # But have to create user in mongodb too
                # username=MONGO_ROOT_USERNAME,
                # password=MONGO_ROOT_PASSWORD,
                # authentication_source="admin",
                serverSelectionTimeoutMS=10000,
            )
        elif DB_MODE == "atlas":
            mongoengine.connect(
                host=MONGO_ATLAS_CONNECTION_STRING,
                serverSelectionTimeoutMS=30000,
            )

        # Perform a simple operation to verify the connection
        connection = get_connection()
        # Initialize db with predefined values
        # It also creates db if you haven't manually done
        await initialize_fiat_and_crypto_currencies()
        await initialize_common_asset_types()
        await initialize_common_categories()
        try:
            if connection[MONGO_DATABASE].list_collection_names():
                logger.info(f" Connected to MongoDB successfully, mode: {DB_MODE}")
            else:
                logger.error(" Failed to connect to MongoDB")
        except Exception as e:
            logger.error(" Failed to verify MongoDB connection: %s", e)

    except Exception as e:
        logger.exception(" An error occurred while connecting to MongoDB")
        raise e
