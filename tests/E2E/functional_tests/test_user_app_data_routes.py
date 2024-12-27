from decimal import Decimal

import pytest

from app.api.controllers.wallet_controller import WalletController
from app.crud.user_app_data_crud import UserAppDataCRUD
from models.models import Asset, Currency, CurrencyExchange, User, UserAppData
from models.schemas import BalanceSchema, WalletCreateSchema


@pytest.mark.asyncio
class TestUserAppDataRoutesSetup:

    async def _get_user_app_data_state(self, test_user_id: str) -> UserAppData:
        """Get current user app data state."""
        return await UserAppDataCRUD.get_one_by_user_id(test_user_id)

    async def _create_test_currency(
        self, code: str, name: str, test_user: User
    ) -> Currency:
        """Helper method to create a test currency"""
        currency_data = {
            "code": code,
            "name": name,
            "user_id": test_user.id,
            "currency_type": "fiat",
            "symbol": "$",
        }
        return Currency(**currency_data).save()

    async def _create_test_exchange(
        self,
        test_user: User,
        from_currency: Currency,
        to_currency: Currency,
        rate: Decimal,
    ) -> CurrencyExchange:
        """Helper method to create a test currency exchange"""
        exchange_data = {
            "user_id": test_user.id,
            "from_currency_id": from_currency.id,
            "to_currency_id": to_currency.id,
            "rate": rate,
        }
        return CurrencyExchange(**exchange_data).save()

    async def _create_test_asset(
        self, test_user: User, currency: Currency, value: Decimal
    ) -> Asset:
        """Helper method to create a test asset"""
        asset_data = {
            "name": "Test Asset",
            "user_id": test_user.id,
            "currency_id": currency.id,
            "value": value,
            "asset_type_id": None,
        }
        return Asset(**asset_data).save()


@pytest.mark.asyncio
class TestChangeBaseCurrencyRoutePositive(TestUserAppDataRoutesSetup):
    """Happy path tests for changing base currency"""

    async def test_change_base_currency_with_existing_values(
        self, client, auth_headers, test_user, test_user_app_data
    ):
        """Test changing base currency with existing wallet and asset values"""
        # Create new currency (UDD)
        udd_currency = await self._create_test_currency("UDD", "Test Dollar", test_user)

        # Get current base currency
        current_base_currency = Currency.objects(
            id=test_user_app_data.base_currency_id.id
        ).first()

        # Create exchange rate from current base to UDD (rate: 2)
        exchange_rate = Decimal("2")
        await self._create_test_exchange(
            test_user, current_base_currency, udd_currency, exchange_rate
        )

        # Create wallet with 1000 current base currency using WalletController
        wallet_schema = WalletCreateSchema(
            name="Test Wallet",
            type="fiat",
            balances_ids=[
                BalanceSchema(
                    currency_id=str(current_base_currency.id), amount=Decimal("1000")
                )
            ],
        )
        await WalletController.create_wallet(wallet_schema, test_user)

        # Create asset worth 1000 current base currency
        asset_value = Decimal("1000")
        created_asset = await self._create_test_asset(
            test_user, current_base_currency, asset_value
        )

        # Call API to change base currency
        response = client.post(
            f"/user-app-data/change-base-currency/{str(udd_currency.id)}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        response_data = response.json()

        # Check if base currency was changed
        assert response_data["data"]["base_currency_id"] == str(udd_currency.id)

        # Get updated user app data
        updated_data_response = client.get(
            "/user-app-data/user-data", headers=auth_headers
        )
        updated_data = updated_data_response.json()["data"]

        # Values should be multiplied by 2 since new currency is worth twice as much
        expected_value = Decimal("4000")  # (1000 + 1000) * 2
        assert Decimal(str(updated_data["net_worth"])) == expected_value
        assert Decimal(str(updated_data["wallets_value"])) == Decimal("2000")
        assert Decimal(str(updated_data["assets_value"])) == Decimal("2000")
        
        # put the base currency back to the original
        response = client.post(
            f"/user-app-data/change-base-currency/{str(current_base_currency.id)}",
            headers=auth_headers,
        )


@pytest.mark.asyncio
class TestCalculateNetWorthRoutePositive(TestUserAppDataRoutesSetup):
    """Happy path tests for calculating net worth"""

    async def test_calculate_net_worth_success(
        self, client, auth_headers, test_user_app_data
    ):
        """Test calculating net worth."""
        response = client.get("/user-app-data/net-worth", headers=auth_headers)

        assert response.status_code == 200
        response_data = response.json()
        assert "net_worth" in response_data["data"]
        assert response_data["message"] == "Net worth calculated successfully"


@pytest.mark.asyncio
class TestGetUserAppDataRoutePositive(TestUserAppDataRoutesSetup):
    """Happy path tests for getting user app data"""

    async def test_get_user_app_data_success(
        self, client, auth_headers, test_user_app_data
    ):
        """Test retrieving user app data."""
        response = client.get("/user-app-data/user-data", headers=auth_headers)

        assert response.status_code == 200
        response_data = response.json()
        assert "base_currency_id" in response_data["data"]
        assert "net_worth" in response_data["data"]
        assert "wallets_value" in response_data["data"]
        assert "assets_value" in response_data["data"]
        assert response_data["message"] == "User app data retrieved successfully"
