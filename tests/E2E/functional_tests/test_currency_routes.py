from datetime import datetime, timezone

import pytest
from mongoengine import DoesNotExist

from app.api.controllers.currency_controller import CurrencyController
from models.models import Currency, User
from models.schemas import CurrencyCreateSchema


@pytest.fixture(scope="function", autouse=True)
async def cleanup_non_predefined_categories(db):
    yield
    if Currency.objects(is_predefined=False).count() > 0:
        Currency.objects(is_predefined=False).delete()


@pytest.mark.asyncio
class TestCurrencyRoutesSetup:
    async def _create_test_currency(self, test_user: User, **overrides) -> Currency:
        """Helper method to create a test currency"""
        currency_data = self._get_test_currency_data(**overrides)
        currency_schema = CurrencyCreateSchema(**currency_data)
        return await CurrencyController.create_currency(currency_schema, test_user)

    def _get_test_currency_data(self, **overrides) -> dict:
        """Get test currency data with optional overrides"""
        timestamp = datetime.now(timezone.utc).strftime("%S")
        currency_data = {
            "code": f"TST",
            "name": f"Test Currency {timestamp}",
            "symbol": "$",
            "currency_type": "fiat",
        }
        currency_data.update(overrides)
        return currency_data

    async def _verify_response(self, response, status_code: int = 200) -> None:
        """Verify API response format and status code"""
        assert response.status_code == status_code
        response_data = response.json()
        assert "message" in response_data
        assert "data" in response_data


@pytest.mark.asyncio
class TestCreateCurrencyRoutePositive(TestCurrencyRoutesSetup):
    """Happy path tests for currency creation"""

    async def test_create_currency_success(self, client, auth_headers):
        """Test creating a currency with valid data."""
        currency_data = {
            "code": "USD",
            "name": "United States Dollar",
            "symbol": "$",
            "currency_type": "fiat",
        }

        response = client.post("/currencies", json=currency_data, headers=auth_headers)

        await self._verify_response(response)
        response_data = response.json()

    async def test_create_currency_with_special_characters(self, client, auth_headers):
        """Test creating a currency with special characters in name."""
        currency_data = {
            "code": "BTC",
            "name": "Bitcoin $$$",
            "symbol": "₿",
            "currency_type": "crypto",
        }

        response = client.post("/currencies", json=currency_data, headers=auth_headers)

        await self._verify_response(response)
        response_data = response.json()
        assert "id" in response_data["data"]

    async def test_create_crypto_currency(self, client, auth_headers):
        """Test creating a cryptocurrency."""
        currency_data = {
            "code": "ADA",
            "name": "Cardano",
            "symbol": "ADA",
            "currency_type": "crypto",
        }

        response = client.post("/currencies", json=currency_data, headers=auth_headers)

        await self._verify_response(response)
        response_data = response.json()
        assert "id" in response_data["data"]


@pytest.mark.asyncio
class TestGetCurrencyRoutePositive(TestCurrencyRoutesSetup):
    """Happy path tests for getting currencies"""

    async def test_get_currency_by_id(self, client, auth_headers, test_user):
        """Test getting a specific currency by ID."""
        currency_dict = await self._create_test_currency(test_user)

        response = client.get(
            f"/currencies/{currency_dict['_id']}", headers=auth_headers
        )

        await self._verify_response(response)
        response_data = response.json()
        assert response_data["message"] == "Currency retrieved successfully"
        assert response_data["data"]["currency"]["_id"] == currency_dict["_id"]
        assert response_data["data"]["currency"]["code"] == currency_dict["code"]

    async def test_get_all_currencies(self, client, auth_headers, test_user):
        """Test getting all currencies for a user."""
        # Create multiple test currencies with unique values
        currency1 = await self._create_test_currency(test_user)
        currency2 = await self._create_test_currency(
            test_user,
            code=f"TTT",
            name=f"Another Test currency",
            symbol="€",
        )

        response = client.get("/currencies", headers=auth_headers)

        await self._verify_response(response)
        response_data = response.json()
        assert response_data["message"] == "Currencies retrieved successfully"
        assert len(response_data["data"]["currencies"]) >= 2
        currency_ids = [curr["_id"] for curr in response_data["data"]["currencies"]]
        assert currency1["_id"] in currency_ids
        assert currency2["_id"] in currency_ids


@pytest.mark.asyncio
class TestUpdateCurrencyRoutePositive(TestCurrencyRoutesSetup):
    """Happy path tests for updating currencies"""

    async def test_update_currency_name(self, client, auth_headers, test_user):
        """Test updating currency name."""
        currency_dict = await self._create_test_currency(test_user)
        update_data = {"name": "Updated Currency Name"}

        response = client.put(
            f"/currencies/{currency_dict['_id']}",
            json=update_data,
            headers=auth_headers,
        )

        await self._verify_response(response)
        response_data = response.json()
        assert response_data["data"]["currency"]["name"] == update_data["name"]

    async def test_update_currency_symbol(self, client, auth_headers, test_user):
        """Test updating currency symbol."""
        currency_dict = await self._create_test_currency(test_user)
        update_data = {"symbol": "¥"}

        response = client.put(
            f"/currencies/{currency_dict['_id']}",
            json=update_data,
            headers=auth_headers,
        )

        await self._verify_response(response)
        response_data = response.json()
        assert response_data["message"] == "Currency updated successfully"
        assert response_data["data"]["currency"]["symbol"] == update_data["symbol"]

    async def test_update_multiple_currency_fields(
        self, client, auth_headers, test_user
    ):
        """Test updating multiple currency fields at once."""
        currency_dict = await self._create_test_currency(test_user)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        update_data = {
            "name": f"New Currency Name {timestamp}",
            "symbol": "££!",
            "code": f"GBA",
        }

        response = client.put(
            f"/currencies/{currency_dict['_id']}",
            json=update_data,
            headers=auth_headers,
        )

        await self._verify_response(response)
        response_data = response.json()
        assert response_data["message"] == "Currency updated successfully"
        assert response_data["data"]["currency"]["name"] == update_data["name"]
        assert response_data["data"]["currency"]["symbol"] == update_data["symbol"]
        assert response_data["data"]["currency"]["code"] == update_data["code"]


@pytest.mark.asyncio
class TestDeleteCurrencyRoutePositive(TestCurrencyRoutesSetup):
    """Happy path tests for deleting currencies"""

    async def test_delete_currency(self, client, auth_headers, test_user):
        """Test deleting a currency."""
        currency_dict = await self._create_test_currency(test_user)

        response = client.delete(
            f"/currencies/{currency_dict['_id']}", headers=auth_headers
        )

        await self._verify_response(response)
        response_data = response.json()
        assert response_data["message"] == "Currency deleted successfully"

        # Verify currency is deleted
        with pytest.raises(DoesNotExist):
            client.get(f"/currencies/{currency_dict['_id']}", headers=auth_headers)
