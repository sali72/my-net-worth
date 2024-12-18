from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from mongoengine import DoesNotExist, NotUniqueError

from app.api.controllers.auth_controller import AuthController
from app.crud.asset_type_crud import AssetTypeCRUD
from app.crud.currency_crud import CurrencyCRUD
from app.crud.user_app_data_crud import UserAppDataCRUD
from app.crud.user_crud import UserCRUD
from app.main import app
from database.database import connect_to_test_db, disconnect_test_db
from models.models import Asset, AssetType
from models.schemas import UserSchema


@pytest.fixture(scope="session", autouse=True)
async def db():
    await connect_to_test_db()
    yield
    await disconnect_test_db()


@pytest.mark.asyncio
class TestAssetRoutesSetup:
    @pytest.fixture(scope="module", autouse=True)
    async def module(self, db):
        await self._initialize_class_attributes()
        await self._setup_test_environment()
        yield
        await self._cleanup()

    @pytest.fixture(scope="function", autouse=True)
    async def method(self):
        yield
        if Asset.objects.count() > 0:
            Asset.objects.delete()

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
            if TestAssetRoutesSetup.test_user_app_data:
                await TestAssetRoutesSetup.test_user_app_data.delete()
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

    def _get_test_asset_data(self, **overrides) -> dict:
        if not self.test_currency:
            pytest.fail("test_currency is None when trying to get test asset data")
        asset_data = {
            "currency_id": str(self.test_currency.id),
            "name": "Test Asset",
            "description": "Test asset description",
            "value": "1000.00",
        }
        asset_data.update(overrides)
        return asset_data

    def _get_auth_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.access_token}"}

    async def _create_test_asset_type(self) -> AssetType:
        test_asset_type = AssetType(
            user_id=self.test_user,
            name="test asset name",
            is_predefined=True,
            description="test asset type description",
        )
        return await AssetTypeCRUD.create_one(test_asset_type)

    async def _delete_test_asset_type(self, test_asset_type_id: str) -> bool:
        return await AssetTypeCRUD.delete_one_by_user(
            test_asset_type_id, self.test_user.id
        )


@pytest.mark.asyncio
class TestCreateAssetRoute(TestAssetRoutesSetup):
    async def test_create_asset_success(self):
        """Test creating an asset with valid data."""
        asset_data = self._get_test_asset_data()

        response = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )

        await self._verify_response(response, status_code=200)
        await self._verify_created_asset(response.json(), asset_data)
        await self._verify_user_app_data_update(asset_data["value"])

    async def test_create_asset_missing_required_field(self):
        """Test creating an asset with missing required 'name' field."""
        asset_data = self._get_test_asset_data()
        del asset_data["name"]

        response = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )

        await self._verify_response(response, status_code=422)
        response_data = response.json()
        assert "name" in response_data["detail"][0]["loc"]

    async def test_create_asset_invalid_value_type(self):
        """Test creating an asset with invalid 'value' type."""
        asset_data = self._get_test_asset_data(value="invalid_decimal")

        response = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )

        await self._verify_response(response, status_code=422)
        response_data = response.json()
        assert "value" in response_data["detail"][0]["loc"]

    async def test_create_asset_negative_value(self):
        """Test creating an asset with negative 'value'."""
        asset_data = self._get_test_asset_data(value="-1000.00")

        response = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )

        await self._verify_response(response, status_code=422)

    async def test_create_asset_nonexistent_currency(self):
        """Test creating an asset with a nonexistent 'currency_id'."""
        asset_data = self._get_test_asset_data(currency_id="6745dbed6b99c20aab2de000")

        with pytest.raises(DoesNotExist):
            response = self.client.post(
                "/assets", json=asset_data, headers=self._get_auth_headers()
            )

    async def test_create_asset_exceeding_max_length(self):
        """Test creating an asset with 'name' exceeding max length."""
        long_name = "A" * 51  # max_length=50
        asset_data = self._get_test_asset_data(name=long_name)

        response = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )

        await self._verify_response(response, status_code=422)

    async def test_create_asset_unauthenticated(self):
        """Test creating an asset without authentication."""
        asset_data = self._get_test_asset_data()

        response = self.client.post("/assets", json=asset_data)  # No headers

        await self._verify_response(response, status_code=401)

    async def test_create_asset_invalid_token(self):
        """Test creating an asset with an invalid access token."""
        asset_data = self._get_test_asset_data()

        headers = {"Authorization": "Bearer invalid_token"}
        response = self.client.post("/assets", json=asset_data, headers=headers)

        await self._verify_response(response, status_code=401)

    async def test_create_asset_special_characters_in_name(self):
        """Test creating an asset with special characters in 'name'."""
        special_name = "Test @$$et #1"
        asset_data = self._get_test_asset_data(name=special_name)

        response = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )

        await self._verify_response(response, status_code=200)
        await self._verify_created_asset(response.json(), asset_data)

    async def test_create_asset_duplicate_name(self):
        """Test creating an asset with a duplicate 'name'."""
        asset_data = self._get_test_asset_data(name="Unique Asset Name")

        # Create the asset for the first time
        response1 = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )
        await self._verify_response(response1, status_code=200)

        # Attempt to create the asset again with the same name
        with pytest.raises(NotUniqueError):
            response2 = self.client.post(
                "/assets", json=asset_data, headers=self._get_auth_headers()
            )

    async def test_create_asset_value_zero(self):
        """Test creating an asset with 'value' equal to zero."""
        asset_data = self._get_test_asset_data(value="0.00")

        response = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )

        await self._verify_response(response, status_code=422)

    async def test_create_asset_with_asset_type(self):
        """Test creating an asset with a valid 'asset_type_id'."""
        asset_type = await self._create_test_asset_type()
        asset_type_id = str(asset_type.id)
        asset_data = self._get_test_asset_data(asset_type_id=asset_type_id)

        response = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )

        await self._verify_created_asset(response.json(), asset_data)
        await self._delete_test_asset_type(asset_type_id)

    async def test_edge_create_asset_with_large_value(self):
        """Test creating an asset with a very large 'value'."""
        large_value = "9999999999"
        asset_data = self._get_test_asset_data(value=large_value)

        response = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )

        await self._verify_response(response, status_code=200)
        await self._verify_created_asset(response.json(), asset_data)

    async def test_edge_create_asset_with_decimal_precision(self):
        """Test creating an asset with maximum decimal precision."""
        precise_value = "1234.12345678"
        asset_data = self._get_test_asset_data(value=precise_value)

        response = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )

        await self._verify_response(response, status_code=200)
        await self._verify_created_asset(response.json(), asset_data)

    async def test_edge_create_asset_with_empty_description(self):
        """Test creating an asset with an empty 'description'."""
        asset_data = self._get_test_asset_data(description="")

        response = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )

        await self._verify_response(response, status_code=200)
        await self._verify_created_asset(response.json(), asset_data)

    async def test_edge_create_asset_max_length_description(self):
        """Test creating an asset with maximum 'description' length."""
        max_length_description = "D" * 255  # max_length=255
        asset_data = self._get_test_asset_data(description=max_length_description)

        response = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )

        await self._verify_response(response, status_code=200)
        await self._verify_created_asset(response.json(), asset_data)

    async def _verify_response(self, response, status_code=200):
        assert response.status_code == status_code

    async def _verify_created_asset(self, response_data: dict, asset_data: dict):
        created_asset = response_data["data"]["model"]
        assert created_asset["name"] == asset_data["name"]
        assert created_asset["description"] == asset_data.get("description", "")
        assert Decimal(str(created_asset["value"])) == Decimal(asset_data["value"])
        assert created_asset["currency_id"] == asset_data["currency_id"]
        assert created_asset["user_id"] == str(self.test_user.id)
        if "asset_type_id" in asset_data:
            assert created_asset["asset_type_id"] == asset_data["asset_type_id"]

    async def _verify_user_app_data_update(self, asset_value: str):
        updated_user_app_data = await UserAppDataCRUD.get_one_by_user_id(
            str(self.test_user.id)
        )
        expected_assets_value = self.test_user_app_data.assets_value + Decimal(
            asset_value
        )
        expected_net_worth = self.test_user_app_data.net_worth + Decimal(asset_value)

        assert updated_user_app_data.assets_value == expected_assets_value
        assert updated_user_app_data.net_worth == expected_net_worth
