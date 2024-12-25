import pytest
from mongoengine import DoesNotExist

from models.models import AssetType, User


@pytest.fixture(scope="function", autouse=True)
async def cleanup_non_predefined_asset_types(db):
    yield
    if AssetType.objects(is_predefined=False).count() > 0:
        AssetType.objects(is_predefined=False).delete()


@pytest.mark.asyncio
class TestAssetTypeRoutesSetup:

    async def _create_test_asset_type(self, test_user: User) -> AssetType:
        """Helper method to create a test asset type"""
        asset_type = AssetType(
            user_id=test_user.id,
            name="Test Asset Type",
            description="Test asset type description",
            is_predefined=False,
        ).save()
        return asset_type

    def _get_test_asset_type_data(self, **overrides) -> dict:
        asset_type_data = {
            "name": "Test Asset Type",
            "description": "Test asset type description",
        }
        asset_type_data.update(overrides)
        return asset_type_data


@pytest.mark.asyncio
class TestCreateAssetTypeRoutePositive(TestAssetTypeRoutesSetup):
    """Happy path tests for asset type creation"""

    async def test_create_asset_type_success(self, client, auth_headers):
        """Test creating an asset type with valid data."""
        asset_type_data = self._get_test_asset_type_data()

        response = client.post(
            "/asset-types", json=asset_type_data, headers=auth_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "id" in response_data["data"]
        assert response_data["message"] == "Asset type created successfully"

    async def test_create_asset_type_with_special_characters(
        self, client, auth_headers
    ):
        """Test creating an asset type with special characters in name."""
        asset_type_data = self._get_test_asset_type_data(name="Test @$$et Type #1")
        response = client.post(
            "/asset-types", json=asset_type_data, headers=auth_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "id" in response_data["data"]
        assert response_data["message"] == "Asset type created successfully"

    async def test_create_asset_type_with_empty_description(self, client, auth_headers):
        """Test creating an asset type with empty description."""
        asset_type_data = self._get_test_asset_type_data(description="")
        response = client.post(
            "/asset-types", json=asset_type_data, headers=auth_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "id" in response_data["data"]
        assert response_data["message"] == "Asset type created successfully"


@pytest.mark.asyncio
class TestReadAllAssetTypesRoutePositive(TestAssetTypeRoutesSetup):
    """Happy path tests for reading all asset types"""

    async def test_read_user_asset_types(self, client, auth_headers, test_user):
        """Test reading user-created asset types."""
        await self._create_test_asset_type(test_user)

        response = client.get("/asset-types", headers=auth_headers)

        assert response.status_code == 200
        response_data = response.json()
        assert "asset_types" in response_data["data"]
        assert response_data["message"] == "Asset types retrieved successfully"


@pytest.mark.asyncio
class TestUpdateAssetTypeRoutePositive(TestAssetTypeRoutesSetup):
    """Happy path tests for updating asset types"""

    async def test_update_asset_type_name(self, client, auth_headers, test_user):
        """Test updating asset type name."""
        asset_type = await self._create_test_asset_type(test_user)
        asset_type_id = str(asset_type.id)
        update_data = {"name": "Updated Name"}

        response = client.put(
            f"/asset-types/{asset_type_id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "asset_type" in response_data["data"]
        assert response_data["message"] == "Asset type updated successfully"


@pytest.mark.asyncio
class TestDeleteAssetTypeRoutePositive(TestAssetTypeRoutesSetup):
    """Happy path tests for deleting asset types"""

    async def test_delete_asset_type(self, client, auth_headers, test_user):
        """Test deleting an asset type."""
        asset_type = await self._create_test_asset_type(test_user)
        asset_type_id = str(asset_type.id)

        response = client.delete(f"/asset-types/{asset_type_id}", headers=auth_headers)

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["message"] == "Asset type deleted successfully"

        # Verify deletion
        with pytest.raises(DoesNotExist):
            AssetType.objects.get(id=asset_type_id)
