import os
import uuid

from dotenv import load_dotenv
from locust import HttpUser, between, task

load_dotenv()
TEST_AUTH_BEARER = os.getenv("TEST_AUTH_BEARER")


class AssetTestUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def create_asset(self):
        # Sample data conforming to AssetCreateSchema
        payload = {
            # "asset_type_id": None,  # or some existing asset_type_id
            "currency_id": "6745dbed6b99c20aab2de4e0",
            "name": f"Test Asset {uuid.uuid4()}",
            "description": "An automated test asset",
            "value": "350000.00",
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {TEST_AUTH_BEARER}",
        }

        # Make a POST request to the create-asset endpoint
        response = self.client.post("/assets", json=payload, headers=headers)

        if response.status_code != 200:
            response.failure(
                f"Failed to create asset. Status: {response.status_code}, body: {response.text}"
            )
