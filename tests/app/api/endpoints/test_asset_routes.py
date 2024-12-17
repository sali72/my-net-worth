from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.api.controllers.auth_controller import AuthController
from app.crud.currency_crud import CurrencyCRUD
from app.crud.user_app_data_crud import UserAppDataCRUD
from app.crud.user_crud import UserCRUD
from app.main import app
from database.database import connect_to_test_db, disconnect_test_db
from models.schemas import UserSchema


@pytest.fixture(scope="session", autouse=True)
async def db():
    await connect_to_test_db()
    yield
    await disconnect_test_db()


@pytest.mark.asyncio
class TestAssetRoutesSetup:
    @pytest.fixture(scope="module", autouse=True)
    async def setup(self, db):
        await self._initialize_class_attributes()
        await self._setup_test_environment()
        yield
        await self._cleanup()

    async def _initialize_class_attributes(self):
        TestAssetRoutesSetup.client = TestClient(app)
        TestAssetRoutesSetup.test_user = None
        TestAssetRoutesSetup.test_currency = None
        TestAssetRoutesSetup.test_user_app_data = None
        TestAssetRoutesSetup.access_token = None

    async def _setup_test_environment(self):
        await self._get_predefined_currency()
        await self._register_test_user()
        await self._fetch_user_data()

    async def _cleanup(self):
        try:
            if TestAssetRoutesSetup.test_user:
                await TestAssetRoutesSetup.test_user.delete()
        except Exception as e:
            print(f"Error during teardown: {e}")

    async def _get_predefined_currency(self):
        TestAssetRoutesSetup.test_currency = (
            await CurrencyCRUD.get_one_by_user_and_code_optional(
                code="USD", user_id=None
            )
        )
        if not TestAssetRoutesSetup.test_currency:
            pytest.fail("Predefined USD currency not found in database")

    async def _register_test_user(self):
        user_schema = UserSchema(
            username="testuser",
            email="test@example.com",
            password="TestPassword!@#123",
            base_currency_id=str(TestAssetRoutesSetup.test_currency.id),
        )
        TestAssetRoutesSetup.access_token = await AuthController.register_user(
            user_schema
        )

    async def _fetch_user_data(self):
        TestAssetRoutesSetup.test_user = await UserCRUD.get_one_by_username("testuser")
        TestAssetRoutesSetup.test_user_app_data = (
            await UserAppDataCRUD.get_one_by_user_id(
                str(TestAssetRoutesSetup.test_user.id)
            )
        )

    def _get_test_asset_data(self) -> dict:
        if not self.test_currency:
            pytest.fail("test_currency is None when trying to get test asset data")
        return {
            "currency_id": str(self.test_currency.id),
            "name": "Test Asset",
            "description": "Test asset description",
            "value": "1000.00",
        }

    def _get_auth_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.access_token}"}


@pytest.mark.asyncio
class TestCreateAssetRoute(TestAssetRoutesSetup):
    async def test_create_asset(self):
        asset_data = self._get_test_asset_data()

        response = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )

        await self._verify_response(response)
        await self._verify_created_asset(response.json(), asset_data)
        await self._verify_user_app_data_update(asset_data["value"])

    async def _verify_response(self, response):
        assert response.status_code == 200

    async def _verify_created_asset(self, response_data: dict, asset_data: dict):
        created_asset = response_data["data"]["model"]
        assert created_asset["name"] == asset_data["name"]
        assert created_asset["description"] == asset_data["description"]
        assert Decimal(created_asset["value"]) == Decimal(asset_data["value"])
        assert created_asset["currency_id"] == asset_data["currency_id"]
        assert created_asset["user_id"] == str(self.test_user.id)

    async def _verify_user_app_data_update(self, asset_value: str):
        updated_user_app_data = await UserAppDataCRUD.get_one_by_user_id(
            str(self.test_user.id)
        )
        assert updated_user_app_data.assets_value == Decimal(asset_value)
        assert updated_user_app_data.net_worth == Decimal(asset_value)
