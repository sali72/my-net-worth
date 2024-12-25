import pytest
from mongoengine import DoesNotExist
from models.enums import TransactionTypeEnum as T
from models.models import Category, User


@pytest.fixture(scope="function", autouse=True)
async def cleanup_non_predefined_categories(db):
    yield
    if Category.objects(is_predefined=False).count() > 0:
        Category.objects(is_predefined=False).delete()


@pytest.mark.asyncio
class TestCategoryRoutesSetup:
    async def _create_test_category(self, test_user: User, **overrides) -> Category:
        """Helper method to create a test category"""
        category_data = {
            "user_id": test_user.id,
            "name": "Test Category",
            "type": T.EXPENSE.value,
            "description": "Test category description",
            "is_predefined": False,
        }
        category_data.update(overrides)
        category = Category(**category_data).save()
        return category

    def _get_test_category_data(self, **overrides) -> dict:
        category_data = {
            "name": "Test Category",
            "type": T.EXPENSE.value,
            "description": "Test category description",
        }
        category_data.update(overrides)
        return category_data


@pytest.mark.asyncio
class TestCreateCategoryRoutePositive(TestCategoryRoutesSetup):
    """Happy path tests for category creation"""

    async def test_create_category_success(self, client, auth_headers):
        """Test creating a category with valid data."""
        category_data = self._get_test_category_data()

        response = client.post("/categories", json=category_data, headers=auth_headers)

        assert response.status_code == 200
        response_data = response.json()
        assert "id" in response_data["data"]
        assert response_data["message"] == "Category created successfully"

    async def test_create_category_with_special_characters(self, client, auth_headers):
        """Test creating a category with special characters in name."""
        category_data = self._get_test_category_data(name="Test C@tegory #1")
        response = client.post("/categories", json=category_data, headers=auth_headers)

        assert response.status_code == 200
        response_data = response.json()
        assert "id" in response_data["data"]
        assert response_data["message"] == "Category created successfully"

    async def test_create_category_with_empty_description(self, client, auth_headers):
        """Test creating a category with empty description."""
        category_data = self._get_test_category_data(description="")
        response = client.post("/categories", json=category_data, headers=auth_headers)

        assert response.status_code == 200
        response_data = response.json()
        assert "id" in response_data["data"]
        assert response_data["message"] == "Category created successfully"

    async def test_create_category_with_different_types(self, client, auth_headers):
        """Test creating categories with different transaction types."""
        type_names = {
            T.INCOME.value: "Income Category",
            T.EXPENSE.value: "Expense Category",
            T.TRANSFER.value: "Transfer Category"
        }
        
        for type_value, name in type_names.items():
            category_data = self._get_test_category_data(
                type=type_value,
                name=name
            )
            response = client.post(
                "/categories", json=category_data, headers=auth_headers
            )

            assert response.status_code == 200
            response_data = response.json()
            assert "id" in response_data["data"]
            assert response_data["message"] == "Category created successfully"

@pytest.mark.asyncio
class TestReadCategoryRoutePositive(TestCategoryRoutesSetup):
    """Happy path tests for reading a single category"""

    async def test_read_category(self, client, auth_headers, test_user):
        """Test reading a specific category."""
        category = await self._create_test_category(test_user)
        
        response = client.get(f"/categories/{str(category.id)}", headers=auth_headers)
        
        assert response.status_code == 200
        response_data = response.json()
        assert "category" in response_data["data"]
        assert response_data["data"]["category"]["name"] == "Test Category"
        assert response_data["message"] == "Category retrieved successfully"


@pytest.mark.asyncio
class TestReadAllCategoriesRoutePositive(TestCategoryRoutesSetup):
    """Happy path tests for reading all categories"""

    async def test_read_all_categories(self, client, auth_headers, test_user):
        """Test reading all user categories."""
        # Create multiple test categories
        categories = [
            await self._create_test_category(test_user),
            await self._create_test_category(
                test_user,
                name="Second Category",
                type=T.INCOME.value
            )
        ]
        
        response = client.get("/categories", headers=auth_headers)
        
        assert response.status_code == 200
        response_data = response.json()
        assert "categories" in response_data["data"]
        assert len(response_data["data"]["categories"]) >= len(categories)
        assert response_data["message"] == "Categories retrieved successfully"


@pytest.mark.asyncio
class TestUpdateCategoryRoutePositive(TestCategoryRoutesSetup):
    """Happy path tests for updating categories"""

    async def test_update_category_name(self, client, auth_headers, test_user):
        """Test updating category name."""
        category = await self._create_test_category(test_user)
        update_data = {"name": "Updated Category Name"}

        response = client.put(
            f"/categories/{str(category.id)}", 
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "category" in response_data["data"]
        assert response_data["data"]["category"]["name"] == "Updated Category Name"
        assert response_data["message"] == "Category updated successfully"

    async def test_update_category_description(self, client, auth_headers, test_user):
        """Test updating category description."""
        category = await self._create_test_category(test_user)
        update_data = {"description": "Updated description"}

        response = client.put(
            f"/categories/{str(category.id)}", 
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "category" in response_data["data"]
        assert response_data["data"]["category"]["description"] == "Updated description"
        assert response_data["message"] == "Category updated successfully"

    async def test_update_category_multiple_fields(self, client, auth_headers, test_user):
        """Test updating multiple category fields."""
        category = await self._create_test_category(test_user)
        update_data = {
            "name": "Updated Name",
            "description": "Updated description"
        }

        response = client.put(
            f"/categories/{str(category.id)}", 
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "category" in response_data["data"]
        assert response_data["data"]["category"]["name"] == "Updated Name"
        assert response_data["data"]["category"]["description"] == "Updated description"
        assert response_data["message"] == "Category updated successfully"


@pytest.mark.asyncio
class TestDeleteCategoryRoutePositive(TestCategoryRoutesSetup):
    """Happy path tests for deleting categories"""

    async def test_delete_category(self, client, auth_headers, test_user):
        """Test deleting a category."""
        category = await self._create_test_category(test_user)
        
        response = client.delete(
            f"/categories/{str(category.id)}", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["message"] == "Category deleted successfully"
        
        # Verify category is deleted
        with pytest.raises(DoesNotExist):
            Category.objects.get(id=category.id)