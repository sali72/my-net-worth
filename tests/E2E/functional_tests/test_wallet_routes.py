from datetime import datetime, timezone
from decimal import Decimal

import pytest
from app.api.controllers.wallet_controller import WalletController
from models.models import Balance, Currency, CurrencyExchange, User, Wallet
from models.schemas import WalletCreateSchema

@pytest.fixture(scope="module", autouse=True)
async def cleanup(db):
    Wallet.objects().delete()
    yield

@pytest.fixture(scope="function", autouse=True)
async def cleanup_balances(db):
    yield
    # First get all balances to delete
    balances_to_delete = []
    for wallet in Wallet.objects():
        if wallet.balances_ids:
            balances_to_delete.extend(wallet.balances_ids)
    
    # Then delete each balance individually
    for balance_id in balances_to_delete:
        Balance.objects(id=balance_id.id).delete()


@pytest.fixture(scope="function", autouse=True)
async def cleanup_wallets(db, cleanup_balances):
    yield
    Wallet.objects().delete()


@pytest.fixture(scope="function", autouse=True)
async def cleanup_currency_exchanges(db, cleanup_wallets):
    yield
    CurrencyExchange.objects().delete()


@pytest.fixture(scope="function", autouse=True)
async def cleanup_currency(db, cleanup_balances):
    yield
    Currency.objects(is_predefined=False).delete()

@pytest.mark.asyncio
class TestWalletRoutesSetup:
    async def _create_test_currency(
        self, test_user: User, code: str = "EUU", **overrides
    ) -> Currency:
        """Helper method to create a test currency with exchange rate"""
        currency_data = {
            "code": code,
            "name": f"Test {code}",
            "user_id": test_user.id,
            "currency_type": "fiat",
            "symbol": f"${code}",
        }
        currency_data.update(overrides)
        new_currency = Currency(**currency_data).save()

        # Create exchange rate from base currency to new currency
        base_currency = Currency.objects(code="USD").first()
        exchange_data = {
            "user_id": test_user.id,
            "from_currency_id": base_currency.id,
            "to_currency_id": new_currency.id,
            "rate": Decimal("2.0"),
            "date": datetime.now(timezone.utc),
        }
        CurrencyExchange(**exchange_data).save()

        return new_currency

    def _get_test_wallet_data(self, currency_id: str, **overrides) -> dict:
        """Helper method to get test wallet data"""
        wallet_data = {
            "name": "Test Wallet",
            "type": "fiat",
            "balances_ids": [{"currency_id": currency_id, "amount": float("1000")}],
        }
        wallet_data.update(overrides)
        return wallet_data


@pytest.mark.asyncio
class TestCreateWalletRoutePositive(TestWalletRoutesSetup):
    """Happy path tests for wallet creation"""

    async def test_create_wallet_success(self, client, auth_headers, test_currency):
        """Test creating a wallet with valid data."""
        wallet_data = self._get_test_wallet_data(currency_id=str(test_currency.id))

        response = client.post("/wallets", json=wallet_data, headers=auth_headers)

        assert response.status_code == 200
        response_data = response.json()
        assert "id" in response_data["data"]
        assert response_data["message"] == "Wallet created successfully"

    async def test_create_wallet_with_special_characters(
        self, client, auth_headers, test_currency
    ):
        """Test creating a wallet with special characters in name."""
        wallet_data = self._get_test_wallet_data(
            currency_id=str(test_currency.id), name="Test W@llet #1"
        )

        response = client.post("/wallets", json=wallet_data, headers=auth_headers)

        assert response.status_code == 200
        response_data = response.json()
        assert "id" in response_data["data"]
        assert response_data["message"] == "Wallet created successfully"

    async def test_create_wallet_with_multiple_balances(
        self, client, auth_headers, test_currency, test_user
    ):
        """Test creating a wallet with multiple currency balances."""
        second_currency = await self._create_test_currency(test_user, "GBB")

        wallet_data = self._get_test_wallet_data(
            currency_id=str(test_currency.id),
            balances_ids=[
                {"currency_id": str(test_currency.id), "amount": float("100.50")},
                {"currency_id": str(second_currency.id), "amount": float("200.75")},
            ],
        )

        response = client.post("/wallets", json=wallet_data, headers=auth_headers)

        assert response.status_code == 200
        response_data = response.json()
        assert "id" in response_data["data"]
        assert response_data["message"] == "Wallet created successfully"

    async def test_create_wallet_with_different_types(
        self, client, auth_headers, test_currency, test_user
    ):
        """Test creating wallets with different types."""
        # Create a crypto currency for crypto wallet test
        crypto_currency = await self._create_test_currency(
            test_user, code="ADA", currency_type="crypto", symbol="ADA", name="CARDANO"
        )

        type_currency_map = {"fiat": test_currency, "crypto": crypto_currency}

        for wallet_type, currency in type_currency_map.items():
            wallet_data = self._get_test_wallet_data(
                currency_id=str(currency.id),
                type=wallet_type,
                name=f"Test {wallet_type.capitalize()} Wallet",
            )

            response = client.post("/wallets", json=wallet_data, headers=auth_headers)

            assert response.status_code == 200
            response_data = response.json()
            assert "id" in response_data["data"]
            assert response_data["message"] == "Wallet created successfully"

@pytest.mark.asyncio
class TestGetWalletRoutePositive(TestWalletRoutesSetup):
    """Happy path tests for getting wallet details"""

    async def test_get_wallet_success(self, client, auth_headers, test_user_app_data, test_user):
        """Test getting a wallet's details."""
        # Create test wallet using WalletController
        wallet_data = self._get_test_wallet_data(
            currency_id=str(test_user_app_data.base_currency_id.id)
        )
        wallet_schema = WalletCreateSchema(**wallet_data)
        created_wallet = await WalletController.create_wallet(wallet_schema, test_user)
        wallet_id = created_wallet["_id"]

        # Get wallet details
        response = client.get(f"/wallets/{wallet_id}", headers=auth_headers)

        assert response.status_code == 200
        response_data = response.json()
        assert "wallet" in response_data["data"]
        assert response_data["data"]["wallet"]["name"] == wallet_data["name"]
        assert response_data["message"] == "Wallet retrieved successfully"


@pytest.mark.asyncio
class TestUpdateWalletRoutePositive(TestWalletRoutesSetup):
    """Happy path tests for updating wallets"""

    async def test_update_wallet_name(self, client, auth_headers, test_user_app_data, test_user):
        """Test updating wallet name."""
        # Create test wallet using WalletController
        wallet_data = self._get_test_wallet_data(
            currency_id=str(test_user_app_data.base_currency_id.id)
        )
        wallet_schema = WalletCreateSchema(**wallet_data)
        created_wallet = await WalletController.create_wallet(wallet_schema, test_user)
        wallet_id = created_wallet["_id"]

        # Update wallet
        update_data = {"name": "Updated Wallet Name"}
        response = client.put(
            f"/wallets/{wallet_id}", 
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "wallet" in response_data["data"]
        assert response_data["data"]["wallet"]["name"] == "Updated Wallet Name"
        assert response_data["message"] == "Wallet updated successfully"


@pytest.mark.asyncio
class TestListWalletsRoutePositive(TestWalletRoutesSetup):
    """Happy path tests for listing wallets"""

    async def test_list_wallets_success(self, client, auth_headers, test_user_app_data, test_user):
        """Test listing all wallets."""
        # Create multiple test wallets using WalletController
        wallet_names = ["Wallet 1", "Wallet 2", "Wallet 3"]
        for name in wallet_names:
            wallet_data = self._get_test_wallet_data(
                currency_id=str(test_user_app_data.base_currency_id.id),
                name=name
            )
            wallet_schema = WalletCreateSchema(**wallet_data)
            await WalletController.create_wallet(wallet_schema, test_user)

        # Get wallets list
        response = client.get("/wallets", headers=auth_headers)

        assert response.status_code == 200
        response_data = response.json()
        assert "wallets" in response_data["data"]
        assert len(response_data["data"]["wallets"]) >= len(wallet_names)


@pytest.mark.asyncio
class TestDeleteWalletRoutePositive(TestWalletRoutesSetup):
    """Happy path tests for deleting wallets"""

    async def test_delete_wallet_success(self, client, auth_headers, test_user_app_data, test_user):
        """Test deleting a wallet."""
        # Create test wallet using WalletController
        wallet_data = self._get_test_wallet_data(
            currency_id=str(test_user_app_data.base_currency_id.id)
        )
        wallet_schema = WalletCreateSchema(**wallet_data)
        created_wallet = await WalletController.create_wallet(wallet_schema, test_user)
        wallet_id = created_wallet["_id"]

        # Delete wallet
        response = client.delete(f"/wallets/{wallet_id}", headers=auth_headers)

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["message"] == "Wallet deleted successfully"

        # Verify wallet is deleted
        get_response = client.get(f"/wallets/{wallet_id}", headers=auth_headers)
        assert get_response.status_code == 404
        
@pytest.mark.asyncio
class TestAddBalanceRoutePositive(TestWalletRoutesSetup):
    """Happy path tests for adding balance to wallet"""

    async def test_add_balance_success(
        self, client, auth_headers, test_user_app_data, test_user
    ):
        """Test adding a balance to an existing wallet."""
        # Create test wallet using WalletController
        wallet_data = self._get_test_wallet_data(
            currency_id=str(test_user_app_data.base_currency_id.id)
        )
        wallet_schema = WalletCreateSchema(**wallet_data)
        created_wallet = await WalletController.create_wallet(wallet_schema, test_user)
        wallet_id = created_wallet["_id"]

        # Create a new currency for the new balance
        new_currency = await self._create_test_currency(test_user, "GBB")

        # Add new balance
        balance_data = {
            "currency_id": str(new_currency.id),
            "amount": float("500.75")
        }
        response = client.post(
            f"/wallets/{wallet_id}/balance",
            json=balance_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "wallet" in response_data["data"]
        assert len(response_data["data"]["wallet"]["balances_ids"]) == 2
        

    async def test_add_balance_with_different_currency_type(
        self, client, auth_headers, test_user_app_data, test_user
    ):
        """Test adding balances with matching currency types."""
        # Create crypto wallet
        crypto_currency = await self._create_test_currency(
            test_user,
            code="BTO",
            currency_type="crypto",
            symbol="₿T",
            name="Bitco"
        )
        wallet_data = self._get_test_wallet_data(
            currency_id=str(crypto_currency.id),
            type="crypto"
        )
        wallet_schema = WalletCreateSchema(**wallet_data)
        created_wallet = await WalletController.create_wallet(wallet_schema, test_user)
        wallet_id = created_wallet["_id"]

        # Create another crypto currency
        second_crypto = await self._create_test_currency(
            test_user,
            code="ETT",
            currency_type="crypto",
            symbol="ΞT",
            name="Ether"
        )

        # Add new crypto balance
        balance_data = {
            "currency_id": str(second_crypto.id),
            "amount": float("2.5")
        }
        response = client.post(
            f"/wallets/{wallet_id}/balance",
            json=balance_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "wallet" in response_data["data"]
        assert len(response_data["data"]["wallet"]["balances_ids"]) == 2


@pytest.mark.asyncio
class TestRemoveBalanceRoutePositive(TestWalletRoutesSetup):
    """Happy path tests for removing balance from wallet"""

    async def test_remove_balance_success(
        self, client, auth_headers, test_user_app_data, test_user
    ):
        """Test removing a balance from a wallet."""
        # Create test wallet with multiple balances
        first_currency = test_user_app_data.base_currency_id
        second_currency = await self._create_test_currency(test_user, "GBB")
        
        wallet_data = self._get_test_wallet_data(
            currency_id=str(first_currency.id),
            balances_ids=[
                {"currency_id": str(first_currency.id), "amount": float("100.50")},
                {"currency_id": str(second_currency.id), "amount": float("200.75")},
            ]
        )
        wallet_schema = WalletCreateSchema(**wallet_data)
        created_wallet = await WalletController.create_wallet(wallet_schema, test_user)
        wallet_id = created_wallet["_id"]

        # Remove one balance
        response = client.delete(
            f"/wallets/{wallet_id}/balance/{str(second_currency.id)}",
            headers=auth_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "wallet" in response_data["data"]
        assert len(response_data["data"]["wallet"]["balances_ids"]) == 1

    async def test_remove_last_balance(
        self, client, auth_headers, test_user_app_data, test_user
    ):
        """Test removing the last balance from a wallet."""
        # Create test wallet with single balance
        wallet_data = self._get_test_wallet_data(
            currency_id=str(test_user_app_data.base_currency_id.id)
        )
        wallet_schema = WalletCreateSchema(**wallet_data)
        created_wallet = await WalletController.create_wallet(wallet_schema, test_user)
        wallet_id = created_wallet["_id"]

        # Remove the balance
        response = client.delete(
            f"/wallets/{wallet_id}/balance/{str(test_user_app_data.base_currency_id.id)}",
            headers=auth_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "wallet" in response_data["data"]
        assert len(response_data["data"]["wallet"]["balances_ids"]) == 0
        
@pytest.mark.asyncio
class TestCalculateTotalWalletValueRoutePositive(TestWalletRoutesSetup):
    """Happy path tests for calculating total wallet value"""

    async def test_calculate_total_wallet_value_success(
        self, client, auth_headers, test_user_app_data, test_user
    ):
        """Test calculating total value of all wallets."""
        # Create first wallet with base currency balance
        first_wallet_data = self._get_test_wallet_data(
            currency_id=str(test_user_app_data.base_currency_id.id),
            name="First Wallet"
        )
        first_wallet_schema = WalletCreateSchema(**first_wallet_data)
        await WalletController.create_wallet(first_wallet_schema, test_user)

        # Create second wallet with different currency
        second_currency = await self._create_test_currency(test_user, "GBB")
        second_wallet_data = self._get_test_wallet_data(
            currency_id=str(second_currency.id),
            name="Second Wallet"
        )
        second_wallet_schema = WalletCreateSchema(**second_wallet_data)
        await WalletController.create_wallet(second_wallet_schema, test_user)

        # Calculate total value
        response = client.get("/wallets/total-value", headers=auth_headers)

        assert response.status_code == 200
        response_data = response.json()
        assert "total_value" in response_data["data"]
        # First wallet: 1000 USD
        # Second wallet: 1000 GBB = 500 USD (exchange rate is 2.0)
        assert Decimal(response_data["data"]["total_value"]) == Decimal("1500.00")
        assert response_data["message"] == "Total wallet value calculated successfully"
