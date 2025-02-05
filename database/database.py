import logging
import os
from typing import Optional

import mongoengine
from dotenv import load_dotenv
from mongoengine.connection import get_connection

from database.initialize_db import (
    initialize_common_asset_types,
    initialize_common_categories,
    initialize_fiat_and_crypto_currencies,
)

load_dotenv()

logger = logging.getLogger(__name__)


class DBConnector:
    def __init__(self, db_name: Optional[str] = None):
        self.MONGO_DATABASE = db_name or os.getenv("MONGO_DATABASE")
        self.MONGO_HOST = os.getenv("MONGO_HOST")
        self.MONGO_LOCAL_HOST = os.getenv("MONGO_LOCAL_HOST")
        self.MONGO_ATLAS_CONNECTION_STRING = os.getenv("MONGO_ATLAS_CONNECTION_STRING")
        self.DB_MODE = os.getenv("DB_MODE")

    async def connect(self):
        try:
            self._establish_connection()
            await self._initialize_db()
            await self._verify_connection()
        except Exception as e:
            logger.exception(
                f" An error occurred while connecting to {self.MONGO_DATABASE}"
            )
            raise e

    def _establish_connection(self):
        if self.DB_MODE == "local":
            mongoengine.connect(
                db=self.MONGO_DATABASE,
                host=self.MONGO_LOCAL_HOST,
                port=27017,
                serverSelectionTimeoutMS=10000,
            )
        elif self.DB_MODE == "container":
            mongoengine.connect(
                db=self.MONGO_DATABASE,
                host=self.MONGO_HOST,
                port=27017,
                # # Add username and pass if you want
                # # But have to create user in mongodb too
                # username=MONGO_ROOT_USERNAME,
                # password=MONGO_ROOT_PASSWORD,
                # authentication_source="admin",
                serverSelectionTimeoutMS=10000,
            )
        elif self.DB_MODE == "atlas":
            connection_string = self.MONGO_ATLAS_CONNECTION_STRING
            if self.MONGO_DATABASE not in connection_string:
                connection_string = connection_string.replace(
                    "mongodb.net/", f"mongodb.net/{self.MONGO_DATABASE}?"
                )
            mongoengine.connect(
                host=connection_string,
                serverSelectionTimeoutMS=30000,
            )

    async def _initialize_db(self):
        await initialize_fiat_and_crypto_currencies()
        await initialize_common_asset_types()
        await initialize_common_categories()

    async def _verify_connection(self):
        connection = get_connection()
        try:
            if connection[self.MONGO_DATABASE].list_collection_names():
                logger.info(
                    f" Connected to {self.MONGO_DATABASE} successfully, mode: {self.DB_MODE}"
                )
            else:
                logger.error(f" Failed to connect to {self.MONGO_DATABASE}")
        except Exception as e:
            logger.error(f" Failed to verify {self.MONGO_DATABASE} connection: %s", e)

    async def disconnect(self):
        try:
            connection = get_connection()
            if connection:
                mongoengine.disconnect()
                logger.info(f" Disconnected from {self.MONGO_DATABASE}")
        except Exception as e:
            logger.exception(
                f" An error occurred while disconnecting from {self.MONGO_DATABASE}"
            )
            raise e


class TestDBConnector(DBConnector):
    def __init__(self):
        super().__init__(db_name=f"{os.getenv('MONGO_DATABASE')}_test")

    async def disconnect(self):
        connection = get_connection()
        if connection:
            connection.drop_database(self.MONGO_DATABASE)
            await super().disconnect()


db_connector = DBConnector()
connect_to_db = db_connector.connect

test_db_connector = TestDBConnector()
connect_to_test_db = test_db_connector.connect
disconnect_test_db = test_db_connector.disconnect
