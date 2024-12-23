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


@pytest.fixture(scope="module", autouse=True)
async def module_setup(db):
    test_setup = TestAssetRoutesSetup()
    await test_setup._initialize_class_attributes()
    await test_setup._setup_test_environment()
    yield test_setup
    await test_setup._cleanup()


@pytest.fixture(scope="function", autouse=True)
async def method():
    yield
    if Asset.objects.count() > 0:
        Asset.objects.delete()


@pytest.mark.asyncio
class TestAssetRoutesSetup:
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

    async def _verify_response(self, response, status_code=200):
        assert response.status_code == status_code

    async def _verify_asset(self, response_data: dict, asset_data: dict):
        created_asset = response_data["data"]["model"]
        assert created_asset["name"] == asset_data["name"]
        assert created_asset["description"] == asset_data.get("description", "")
        assert Decimal(str(created_asset["value"])) == Decimal(asset_data["value"])
        assert created_asset["currency_id"] == asset_data["currency_id"]
        assert created_asset["user_id"] == str(self.test_user.id)
        if "asset_type_id" in asset_data:
            assert created_asset["asset_type_id"] == asset_data["asset_type_id"]

    async def _verify_user_app_data_increased_assets_value(self, asset_value: str):
        updated_user_app_data = await UserAppDataCRUD.get_one_by_user_id(
            str(self.test_user.id)
        )
        expected_assets_value = self.test_user_app_data.assets_value + Decimal(
            asset_value
        )
        expected_net_worth = self.test_user_app_data.net_worth + Decimal(asset_value)

        assert updated_user_app_data.assets_value == expected_assets_value
        assert updated_user_app_data.net_worth == expected_net_worth


@pytest.mark.asyncio
class TestCreateAssetRoutePositive(TestAssetRoutesSetup):
    """Happy path tests for asset creation"""

    async def test_create_asset_success(self):
        """Test creating an asset with valid data."""
        asset_data = self._get_test_asset_data()
        response = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )
        await self._verify_response(response)
        await self._verify_asset(response.json(), asset_data)
        await self._verify_user_app_data_increased_assets_value(asset_data["value"])

    async def test_create_asset_with_asset_type(self):
        """Test creating an asset with a valid asset_type_id."""
        asset_type = await self._create_test_asset_type()
        asset_data = self._get_test_asset_data(asset_type_id=str(asset_type.id))
        response = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )
        await self._verify_response(response)
        await self._verify_asset(response.json(), asset_data)
        await self._delete_test_asset_type(str(asset_type.id))

    async def test_create_asset_with_special_characters_in_name(self):
        """Test creating an asset with special characters in name."""
        asset_data = self._get_test_asset_data(name="Test @$$et #1")
        response = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )
        await self._verify_response(response)
        await self._verify_asset(response.json(), asset_data)

    async def test_create_asset_with_empty_description(self):
        """Test creating an asset with empty description."""
        asset_data = self._get_test_asset_data(description="")
        response = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )
        await self._verify_response(response)
        await self._verify_asset(response.json(), asset_data)


@pytest.mark.asyncio
class TestCreateAssetRouteValidation(TestAssetRoutesSetup):
    """Input validation tests for asset creation"""

    async def test_create_asset_missing_required_field(self):
        """Test creating an asset with missing required name field."""
        asset_data = self._get_test_asset_data()
        del asset_data["name"]
        response = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )
        await self._verify_response(response, status_code=422)
        assert "name" in response.json()["detail"][0]["loc"]

    async def test_create_asset_invalid_value_type(self):
        """Test creating an asset with invalid value type."""
        asset_data = self._get_test_asset_data(value="invalid_decimal")
        response = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )
        await self._verify_response(response, status_code=422)
        assert "value" in response.json()["detail"][0]["loc"]

    async def test_create_asset_negative_value(self):
        """Test creating an asset with negative value."""
        asset_data = self._get_test_asset_data(value="-1000.00")
        response = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )
        await self._verify_response(response, status_code=422)

    async def test_create_asset_value_zero(self):
        """Test creating an asset with zero value."""
        asset_data = self._get_test_asset_data(value="0.00")
        response = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )
        await self._verify_response(response, status_code=422)

    async def test_create_asset_exceeding_max_length(self):
        """Test creating an asset with name exceeding maximum length."""
        asset_data = self._get_test_asset_data(name="A" * 256)
        response = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )
        await self._verify_response(response, status_code=422)


@pytest.mark.asyncio
class TestCreateAssetRouteNegative(TestAssetRoutesSetup):
    """Error case tests for asset creation"""

    async def test_create_asset_nonexistent_currency(self):
        """Test creating an asset with a nonexistent currency_id."""
        asset_data = self._get_test_asset_data(currency_id="6745dbed6b99c20aab2de000")
        with pytest.raises(DoesNotExist):
            self.client.post(
                "/assets", json=asset_data, headers=self._get_auth_headers()
            )

    async def test_create_asset_duplicate_name(self):
        """Test creating an asset with a duplicate name."""
        asset_data = self._get_test_asset_data(name="Unique Asset Name")
        response1 = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )
        await self._verify_response(response1)

        with pytest.raises(NotUniqueError):
            self.client.post(
                "/assets", json=asset_data, headers=self._get_auth_headers()
            )

    async def test_create_asset_unauthenticated(self):
        """Test creating an asset without authentication."""
        asset_data = self._get_test_asset_data()
        response = self.client.post("/assets", json=asset_data)
        await self._verify_response(response, status_code=401)

    async def test_create_asset_invalid_token(self):
        """Test creating an asset with an invalid token."""
        asset_data = self._get_test_asset_data()
        response = self.client.post(
            "/assets",
            json=asset_data,
            headers={"Authorization": "Bearer invalid_token"},
        )
        await self._verify_response(response, status_code=401)


@pytest.mark.asyncio
class TestCreateAssetRouteEdge(TestAssetRoutesSetup):
    """Edge case tests for asset creation"""

    async def test_edge_create_asset_with_large_value(self):
        """Test creating an asset with a very large value."""
        asset_data = self._get_test_asset_data(value="9999999999")
        response = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )
        await self._verify_response(response)
        await self._verify_asset(response.json(), asset_data)

    async def test_edge_create_asset_with_decimal_precision(self):
        """Test creating an asset with maximum decimal precision."""
        asset_data = self._get_test_asset_data(value="1234.12345678")
        response = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )
        await self._verify_response(response)
        await self._verify_asset(response.json(), asset_data)

    async def test_edge_create_asset_max_length_description(self):
        """Test creating an asset with maximum description length."""
        asset_data = self._get_test_asset_data(description="D" * 255)
        response = self.client.post(
            "/assets", json=asset_data, headers=self._get_auth_headers()
        )
        await self._verify_response(response)
        await self._verify_asset(response.json(), asset_data)


@pytest.mark.asyncio
class TestTotalValueRoutePositive(TestAssetRoutesSetup):
    """Happy path tests for calculating total asset value"""

    async def _create_test_asset(self, value: str, name_suffix: str) -> None:
        """Helper method to create a test asset using CRUD"""
        asset_data = self._get_test_asset_data(
            value=value,
            name=f"Test Asset {name_suffix}"
        )
        asset = Asset(
            user_id=self.test_user,
            currency_id=self.test_currency,
            name=asset_data["name"],
            description=asset_data["description"],
            value=Decimal(asset_data["value"])
        )
        asset.save()

    async def _verify_total_value_response(
        self, response_data: dict, expected_value: Decimal
    ):
        """Helper method to verify total value response"""
        total_value = response_data["data"]["total_value"]
        assert Decimal(str(total_value)) == expected_value
        assert response_data["message"] == "Total asset value calculated successfully"

    async def test_calculate_total_value_single_asset(self):
        """Test calculating total value with a single asset."""
        await self._create_test_asset("1000.00", "1")

        response = self.client.get(
            "/assets/total-value", headers=self._get_auth_headers()
        )

        await self._verify_response(response)
        await self._verify_total_value_response(response.json(), Decimal("1000.00"))

    async def test_calculate_total_value_multiple_assets(self):
        """Test calculating total value with multiple assets."""
        await self._create_test_asset("1000.00", "2")
        await self._create_test_asset("2000.00", "3")
        await self._create_test_asset("3000.00", "4")

        response = self.client.get(
            "/assets/total-value", headers=self._get_auth_headers()
        )

        await self._verify_response(response)
        await self._verify_total_value_response(response.json(), Decimal("6000.00"))

    async def test_calculate_total_value_decimal_precision(self):
        """Test calculating total value with decimal precision."""
        await self._create_test_asset("1000.50", "5")
        await self._create_test_asset("2000.75", "6")

        response = self.client.get(
            "/assets/total-value", headers=self._get_auth_headers()
        )

        await self._verify_response(response)
        await self._verify_total_value_response(response.json(), Decimal("3001.25"))

    async def test_calculate_total_value_no_assets(self):
        """Test calculating total value with no assets."""
        response = self.client.get(
            "/assets/total-value", headers=self._get_auth_headers()
        )

        await self._verify_response(response)
        await self._verify_total_value_response(response.json(), Decimal("0"))
        

@pytest.mark.asyncio
class TestFilterRoutePositive(TestAssetRoutesSetup):
    """Happy path tests for filtering assets"""

    async def _create_test_assets_for_filtering(self) -> None:
        """Helper method to create test assets for filtering"""
        assets_data = [
            ("1000.00", "Stock A"),
            ("2000.00", "Bond B"),
            ("3000.00", "Stock C"),
            ("4000.00", "Bond D"),
        ]
        for value, name in assets_data:
            asset = Asset(
                user_id=self.test_user,
                currency_id=self.test_currency,
                name=name,
                description="Test asset description",
                value=Decimal(value)
            )
            asset.save()

    async def _verify_filtered_assets_response(
        self, response_data: dict, expected_count: int, expected_names: list[str]
    ):
        """Helper method to verify filtered assets response"""
        assets = response_data["data"]["assets"]
        assert len(assets) == expected_count
        actual_names = [asset["name"] for asset in assets]
        assert sorted(actual_names) == sorted(expected_names)
        assert response_data["message"] == "Filtered assets retrieved successfully"

    async def test_filter_assets_by_name(self):
        """Test filtering assets by name."""
        await self._create_test_assets_for_filtering()
        
        response = self.client.get(
            "/assets/filter",
            params={"name": "Stock"},
            headers=self._get_auth_headers()
        )
        
        await self._verify_response(response)
        await self._verify_filtered_assets_response(
            response.json(), 2, ["Stock A", "Stock C"]
        )

    async def test_filter_assets_by_date_range(self):
        """Test filtering assets by creation date range."""
        await self._create_test_assets_for_filtering()
        
        response = self.client.get(
            "/assets/filter",
            params={
                "created_at_start": "2024-01-01T00:00:00Z",
                "created_at_end": "2024-12-31T23:59:59Z"
            },
            headers=self._get_auth_headers()
        )
        
        await self._verify_response(response)
        await self._verify_filtered_assets_response(
            response.json(), 4, ["Stock A", "Bond B", "Stock C", "Bond D"]
        )

    async def test_filter_assets_by_asset_type(self):
        """Test filtering assets by asset type."""
        await self._create_test_assets_for_filtering()
        test_asset_type = await self._create_test_asset_type()
        
        response = self.client.get(
            "/assets/filter",
            params={"asset_type_id": str(test_asset_type.id)},
            headers=self._get_auth_headers()
        )
        
        await self._verify_response(response)
        await self._verify_filtered_assets_response(response.json(), 0, [])
        await self._delete_test_asset_type(str(test_asset_type.id))

    async def test_filter_assets_by_currency(self):
        """Test filtering assets by currency."""
        await self._create_test_assets_for_filtering()
        
        response = self.client.get(
            "/assets/filter",
            params={"currency_id": str(self.test_currency.id)},
            headers=self._get_auth_headers()
        )
        
        await self._verify_response(response)
        await self._verify_filtered_assets_response(
            response.json(), 
            4, 
            ["Stock A", "Bond B", "Stock C", "Bond D"]
        )

    async def test_filter_assets_combined_criteria(self):
        """Test filtering assets with combined criteria."""
        await self._create_test_assets_for_filtering()
        
        response = self.client.get(
            "/assets/filter",
            params={
                "name": "Stock",
                "currency_id": str(self.test_currency.id)
            },
            headers=self._get_auth_headers()
        )
        
        await self._verify_response(response)
        await self._verify_filtered_assets_response(
            response.json(), 2, ["Stock A", "Stock C"]
        )

    async def test_filter_assets_no_criteria(self):
        """Test filtering assets without any criteria (returns all assets)."""
        await self._create_test_assets_for_filtering()
        
        response = self.client.get(
            "/assets/filter",
            params={},
            headers=self._get_auth_headers()
        )
        
        await self._verify_response(response)
        await self._verify_filtered_assets_response(
            response.json(), 
            4, 
            ["Stock A", "Bond B", "Stock C", "Bond D"]
        )

@pytest.mark.asyncio
class TestGetAssetRoutePositive(TestAssetRoutesSetup):
    """Happy path tests for getting a single asset"""

    async def _create_test_asset_and_return_id(self, **overrides) -> str:
        """Helper method to create a test asset and return its ID"""
        asset_data = self._get_test_asset_data(**overrides)
        asset = Asset(
            user_id=self.test_user,
            currency_id=self.test_currency,
            name=asset_data["name"],
            description=asset_data["description"],
            value=Decimal(asset_data["value"])
        )
        asset.save()
        return str(asset.id)

    async def _verify_get_asset_response(self, response_data: dict, expected_data: dict):
        """Helper method to verify get asset response"""
        asset = response_data["data"]["asset"]
        assert asset["name"] == expected_data["name"]
        assert asset["description"] == expected_data["description"]
        assert Decimal(str(asset["value"])) == Decimal(expected_data["value"])
        assert asset["currency_id"] == expected_data["currency_id"]
        assert response_data["message"] == "Asset retrieved successfully"

    async def test_get_asset_basic(self):
        """Test getting an asset with basic data."""
        asset_data = self._get_test_asset_data()
        asset_id = await self._create_test_asset_and_return_id()

        response = self.client.get(
            f"/assets/{asset_id}",
            headers=self._get_auth_headers()
        )

        await self._verify_response(response)
        await self._verify_get_asset_response(response.json(), asset_data)

    async def test_get_asset_with_asset_type(self):
        """Test getting an asset that has an asset type."""
        test_asset_type = await self._create_test_asset_type()
        asset_data = self._get_test_asset_data(
            asset_type_id=str(test_asset_type.id)
        )
        asset_id = await self._create_test_asset_and_return_id(
            asset_type_id=str(test_asset_type.id)
        )

        response = self.client.get(
            f"/assets/{asset_id}",
            headers=self._get_auth_headers()
        )

        await self._verify_response(response)
        await self._verify_get_asset_response(response.json(), asset_data)
        await self._delete_test_asset_type(str(test_asset_type.id))

    async def test_get_asset_with_special_characters(self):
        """Test getting an asset with special characters in name."""
        asset_data = self._get_test_asset_data(name="Test @$$et #1")
        asset_id = await self._create_test_asset_and_return_id(
            name="Test @$$et #1"
        )

        response = self.client.get(
            f"/assets/{asset_id}",
            headers=self._get_auth_headers()
        )

        await self._verify_response(response)
        await self._verify_get_asset_response(response.json(), asset_data)

    async def test_get_asset_with_empty_description(self):
        """Test getting an asset with empty description."""
        asset_data = self._get_test_asset_data(description="")
        asset_id = await self._create_test_asset_and_return_id(
            description=""
        )

        response = self.client.get(
            f"/assets/{asset_id}",
            headers=self._get_auth_headers()
        )

        await self._verify_response(response)
        await self._verify_get_asset_response(response.json(), asset_data)

    async def test_get_asset_with_max_decimal_precision(self):
        """Test getting an asset with maximum decimal precision value."""
        asset_data = self._get_test_asset_data(value="1234.12345678")
        asset_id = await self._create_test_asset_and_return_id(
            value="1234.12345678"
        )

        response = self.client.get(
            f"/assets/{asset_id}",
            headers=self._get_auth_headers()
        )

        await self._verify_response(response)
        await self._verify_get_asset_response(response.json(), asset_data)
        
@pytest.mark.asyncio
class TestReadAllAssetsRoutePositive(TestAssetRoutesSetup):
    """Happy path tests for reading all assets"""

    async def _create_test_assets_batch(self) -> list[str]:
        """Helper method to create a batch of test assets"""
        assets_data = [
            ("Asset One", "1000.00"),
            ("Asset Two", "2000.00"),
            ("Asset Three", "3000.00"),
        ]
        asset_ids = []
        for name, value in assets_data:
            asset = Asset(
                user_id=self.test_user,
                currency_id=self.test_currency,
                name=name,
                description="Test asset description",
                value=Decimal(value)
            )
            asset.save()
            asset_ids.append(str(asset.id))
        return asset_ids

    async def _verify_read_all_response(
        self, response_data: dict, expected_count: int, expected_names: list[str]
    ):
        """Helper method to verify read all assets response"""
        assets = response_data["data"]["assets"]
        assert len(assets) == expected_count
        actual_names = [asset["name"] for asset in assets]
        assert sorted(actual_names) == sorted(expected_names)
        assert response_data["message"] == "Assets retrieved successfully"

    async def test_read_all_assets_empty(self):
        """Test reading all assets when no assets exist."""
        response = self.client.get(
            "/assets",
            headers=self._get_auth_headers()
        )

        await self._verify_response(response)
        await self._verify_read_all_response(response.json(), 0, [])

    async def test_read_all_assets_multiple(self):
        """Test reading all assets with multiple assets."""
        await self._create_test_assets_batch()

        response = self.client.get(
            "/assets",
            headers=self._get_auth_headers()
        )

        await self._verify_response(response)
        await self._verify_read_all_response(
            response.json(),
            3,
            ["Asset One", "Asset Two", "Asset Three"]
        )

    async def test_read_all_assets_with_asset_type(self):
        """Test reading all assets including one with asset type."""
        test_asset_type = await self._create_test_asset_type()
        
        asset = Asset(
            user_id=self.test_user,
            currency_id=self.test_currency,
            name="Asset With Type",
            description="Test asset description",
            value=Decimal("1000.00"),
            asset_type_id=test_asset_type
        )
        asset.save()

        response = self.client.get(
            "/assets",
            headers=self._get_auth_headers()
        )

        await self._verify_response(response)
        await self._verify_read_all_response(
            response.json(),
            1,
            ["Asset With Type"]
        )
        await self._delete_test_asset_type(str(test_asset_type.id))

    async def test_read_all_assets_with_different_currencies(self):
        """Test reading all assets with different currencies."""
        # First asset with default test currency
        asset1 = Asset(
            user_id=self.test_user,
            currency_id=self.test_currency,
            name="USD Asset",
            description="Test asset description",
            value=Decimal("1000.00")
        )
        asset1.save()

        # Create and use a different currency for second asset
        eur_currency = await CurrencyCRUD.get_one_by_user_and_code_optional(
            code="EUR", user_id=None
        )
        if eur_currency:
            asset2 = Asset(
                user_id=self.test_user,
                currency_id=eur_currency,
                name="EUR Asset",
                description="Test asset description",
                value=Decimal("1000.00")
            )
            asset2.save()

            response = self.client.get(
                "/assets",
                headers=self._get_auth_headers()
            )

            await self._verify_response(response)
            await self._verify_read_all_response(
                response.json(),
                2,
                ["USD Asset", "EUR Asset"]
            )

@pytest.mark.asyncio
class TestUpdateAssetRoutePositive(TestAssetRoutesSetup):
    """Happy path tests for updating assets"""

    def _create_test_asset_and_return_id(self, **overrides) -> str:
        """Helper method to create a test asset and return its ID"""
        asset_data = self._get_test_asset_data(**overrides)
        asset = Asset(
            user_id=self.test_user,
            currency_id=self.test_currency,
            name=asset_data["name"],
            description=asset_data["description"],
            value=Decimal(asset_data["value"])
        )
        asset.save()
        return str(asset.id)

    async def _verify_update_asset_response(
        self, response_data: dict, expected_data: dict
    ):
        """Helper method to verify update asset response"""
        updated_asset = response_data["data"]["asset"]
        assert updated_asset["name"] == expected_data["name"]
        assert updated_asset["description"] == expected_data["description"]
        assert Decimal(str(updated_asset["value"])) == Decimal(expected_data["value"])
        assert updated_asset["currency_id"] == expected_data["currency_id"]
        if "asset_type_id" in expected_data:
            assert updated_asset["asset_type_id"] == expected_data["asset_type_id"]
        assert response_data["message"] == "Asset updated successfully"

    async def test_update_asset_name(self):
        """Test updating asset name."""
        asset_id = self._create_test_asset_and_return_id(name="Original Name")
        update_data = {"name": "Updated Name"}

        response = self.client.put(
            f"/assets/{asset_id}",
            json=update_data,
            headers=self._get_auth_headers()
        )

        await self._verify_response(response)
        expected_data = self._get_test_asset_data(name="Updated Name")
        await self._verify_update_asset_response(response.json(), expected_data)

    async def test_update_asset_description(self):
        """Test updating asset description."""
        asset_id = self._create_test_asset_and_return_id()
        update_data = {"description": "Updated description"}

        response = self.client.put(
            f"/assets/{asset_id}",
            json=update_data,
            headers=self._get_auth_headers()
        )

        await self._verify_response(response)
        expected_data = self._get_test_asset_data(description="Updated description")
        await self._verify_update_asset_response(response.json(), expected_data)

    async def test_update_asset_value(self):
        """Test updating asset value."""
        asset_id = self._create_test_asset_and_return_id()
        update_data = {"value": "2000.00"}

        response = self.client.put(
            f"/assets/{asset_id}",
            json=update_data,
            headers=self._get_auth_headers()
        )

        await self._verify_response(response)
        expected_data = self._get_test_asset_data(value="2000.00")
        await self._verify_update_asset_response(response.json(), expected_data)

    async def test_update_asset_with_asset_type(self):
        """Test updating asset with asset type."""
        asset_id = self._create_test_asset_and_return_id()
        test_asset_type = await self._create_test_asset_type()
        update_data = {"asset_type_id": str(test_asset_type.id)}

        response = self.client.put(
            f"/assets/{asset_id}",
            json=update_data,
            headers=self._get_auth_headers()
        )

        await self._verify_response(response)
        expected_data = self._get_test_asset_data(asset_type_id=str(test_asset_type.id))
        await self._verify_update_asset_response(response.json(), expected_data)
        await self._delete_test_asset_type(str(test_asset_type.id))

    async def test_update_asset_remove_asset_type(self):
        """Test removing asset type from asset."""
        test_asset_type = await self._create_test_asset_type()
        asset_id = self._create_test_asset_and_return_id(
            asset_type_id=str(test_asset_type.id)
        )
        update_data = {"asset_type_id": None}

        response = self.client.put(
            f"/assets/{asset_id}",
            json=update_data,
            headers=self._get_auth_headers()
        )

        await self._verify_response(response)
        expected_data = self._get_test_asset_data()
        await self._verify_update_asset_response(response.json(), expected_data)
        await self._delete_test_asset_type(str(test_asset_type.id))

    async def test_update_asset_multiple_fields(self):
        """Test updating multiple asset fields."""
        asset_id = self._create_test_asset_and_return_id()
        update_data = {
            "name": "Updated Name",
            "description": "Updated description",
            "value": "3000.00"
        }

        response = self.client.put(
            f"/assets/{asset_id}",
            json=update_data,
            headers=self._get_auth_headers()
        )

        await self._verify_response(response)
        expected_data = self._get_test_asset_data(**update_data)
        await self._verify_update_asset_response(response.json(), expected_data)

@pytest.mark.asyncio
class TestDeleteAssetRoutePositive(TestAssetRoutesSetup):
    """Happy path tests for deleting assets"""

    async def _create_test_asset_and_return_id(self, **overrides) -> str:
        """Helper method to create a test asset and return its ID"""
        asset_data = self._get_test_asset_data(**overrides)
        asset = Asset(
            user_id=self.test_user,
            currency_id=self.test_currency,
            name=asset_data["name"],
            description=asset_data["description"],
            value=Decimal(asset_data["value"])
        )
        asset.save()

        # Update UserAppData
        self.test_user_app_data.assets_value += Decimal(asset_data["value"])
        self.test_user_app_data.net_worth += Decimal(asset_data["value"])
        self.test_user_app_data.save()

        return str(asset.id)

    async def _verify_delete_asset_response(self, response_data: dict):
        """Helper method to verify delete asset response"""
        assert response_data["message"] == "Asset deleted successfully"
        assert response_data["data"] is None

    async def _verify_asset_deleted(self, asset_id: str):
        """Helper method to verify asset is deleted from database"""
        with pytest.raises(DoesNotExist):
            Asset.objects.get(id=asset_id)

    async def _verify_user_app_data_decreased_assets_value(self, asset_value: str):
        """Helper method to verify user app data values are decreased"""
        # Refresh user app data from database
        self.test_user_app_data.reload()
        updated_user_app_data = await UserAppDataCRUD.get_one_by_user_id(
            str(self.test_user.id)
        )
        
        expected_assets_value = max(Decimal("0"), 
            self.test_user_app_data.assets_value - Decimal(asset_value)
        )
        expected_net_worth = max(Decimal("0"), 
            self.test_user_app_data.net_worth - Decimal(asset_value)
        )

        assert updated_user_app_data.assets_value == expected_assets_value
        assert updated_user_app_data.net_worth == expected_net_worth

    async def test_delete_last_asset(self):
        """Test deleting the last remaining asset."""
        asset_id = await self._create_test_asset_and_return_id(
            name="Last Asset"
        )
        asset = Asset.objects.get(id=asset_id)
        asset_value = str(asset.value)

        response = self.client.delete(
            f"/assets/{asset_id}",
            headers=self._get_auth_headers()
        )

        await self._verify_response(response)
        await self._verify_delete_asset_response(response.json())
        await self._verify_asset_deleted(asset_id)
        await self._verify_user_app_data_decreased_assets_value(asset_value)
        
        # Verify no assets remain
        assert Asset.objects(user_id=self.test_user).count() == 0