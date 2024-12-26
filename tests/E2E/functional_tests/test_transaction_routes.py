from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
import asyncio
import pytest

from app.api.controllers.category_controller import CategoryController
from app.api.controllers.transaction_controller import TransactionController
from app.api.controllers.user_app_data_controller import UserAppDataController
from app.api.controllers.wallet_controller import WalletController
from app.crud.user_app_data_crud import UserAppDataCRUD
from app.crud.wallet_crud import WalletCRUD
from models.enums import TransactionTypeEnum as T
from models.models import Transaction, User, UserAppData, Wallet
from models.schemas import (
    BalanceSchema,
    CategoryCreateSchema,
    TransactionCreateSchema,
    WalletCreateSchema,
)


@pytest.fixture(scope="function", autouse=True)
async def cleanup_transactions(db):
    yield
    Transaction.objects().delete()


@pytest.fixture(scope="function", autouse=True)
async def cleanup_wallets(db):
    yield
    Wallet.objects().delete()


@pytest.fixture(scope="function", autouse=True)
async def cleanup_user_app_data(db, test_user):
    test_user_app_data = await UserAppDataCRUD.get_one_by_user_id(test_user.id)
    test_user_app_data.assets_value = Decimal(0)
    test_user_app_data.wallets_value = Decimal(0)
    test_user_app_data.net_worth = Decimal(0)
    test_user_app_data.save()
    yield test_user_app_data


@pytest.mark.asyncio
class TestTransactionRoutesSetup:
    async def _create_test_transaction_and_wallet(
        self, test_user: User, **overrides
    ) -> Transaction:
        """Helper method to create a test transaction with optional overrides.

        Args:
            test_user (User): The user creating the transaction.
            **overrides: Optional overrides for transaction fields.

        Returns:
            Transaction: The created transaction object.
        """
        user_app_data = await UserAppDataCRUD.get_one_by_user_id(test_user.id)
        wallet_dict = await self._create_test_wallet(test_user, user_app_data)
        category_dict = await self._create_test_category(test_user)

        # Get the actual model instances using the IDs from the dictionaries
        wallet = await WalletController.get_wallet(wallet_dict["_id"], test_user.id)
        category = await CategoryController.get_category(
            category_dict["_id"], test_user.id
        )

        # Default transaction data
        transaction_data = {
            "amount": Decimal("100.00"),
            "type": T.INCOME.value,
            "date": datetime.utcnow(),
            "description": "Test transaction",
            "to_wallet_id": wallet["_id"],
            "category_id": category["_id"],
            "currency_id": str(user_app_data.base_currency_id.id),
        }

        # Handle different transaction types
        if overrides.get("type") == T.EXPENSE.value:
            transaction_data["from_wallet_id"] = transaction_data.pop("to_wallet_id")
        elif overrides.get("type") == T.TRANSFER.value:
            transaction_data["from_wallet_id"] = transaction_data.pop("to_wallet_id")
            # Expect to_wallet_id in overrides for transfer

        # Update with any overrides
        transaction_data.update(overrides)

        test_transaction_schema = TransactionCreateSchema(**transaction_data)
        transaction = await TransactionController.create_transaction(
            test_transaction_schema, test_user
        )
        await UserAppDataController.add_value_to_user_app_data_wallets_value(
            test_user, transaction.amount, transaction.currency_id.id
        )
        return transaction

    def _get_test_transaction_data(
        self, test_wallet: dict, test_category: dict, **overrides
    ) -> dict:
        """Helper method to create test transaction data"""
        transaction_data = {
            "amount": "100.00",
            "type": T.EXPENSE.value,
            "date": datetime.utcnow().isoformat(),
            "description": "Test transaction",
            "from_wallet_id": str(test_wallet["_id"]),
            "category_id": str(test_category["_id"]),
            "currency_id": str(test_wallet["balances_ids"][0]["currency_id"]),
        }

        # Handle different transaction types
        if overrides.get("type") == T.INCOME.value:
            transaction_data["to_wallet_id"] = transaction_data.pop("from_wallet_id")
        elif overrides.get("type") == T.TRANSFER.value:
            # Keep from_wallet_id and add to_wallet_id from overrides
            pass

        transaction_data.update(overrides)
        return transaction_data

    async def _create_test_wallet(
        self, test_user: User, user_app_data: UserAppData, name_suffix: str = ""
    ) -> dict:
        """Helper method to create a test wallet with a unique name"""
        # Generate a unique timestamp-based suffix if none provided
        suffix = name_suffix or f"_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        balance_schema = BalanceSchema(
            currency_id=str(user_app_data.base_currency_id.id), amount="1000.00"
        )

        wallet_schema = WalletCreateSchema(
            name=f"Test Wallet{suffix}", type="fiat", balances_ids=[balance_schema]
        )

        return await WalletController.create_wallet(wallet_schema, test_user)

    async def _create_test_category(
        self, test_user: User, name_suffix: str = ""
    ) -> dict:
        """Helper method to create a test category with a unique name"""
        # Generate a unique timestamp-based suffix if none provided
        suffix = name_suffix or f"_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        category_schema = CategoryCreateSchema(
            name=f"Test Category{suffix}",
            type=T.EXPENSE.value,
            description="Test category description",
        )

        return await CategoryController.create_category(category_schema, test_user)

    async def _verify_response(self, response, status_code: int = 200) -> None:
        """Helper method to verify API response"""
        assert response.status_code == status_code
        response_data = response.json()
        assert "data" in response_data
        assert "message" in response_data

    async def _verify_transaction_impacts_on_wallet(
        self,
        test_user: User,
        wallet_id: str,
        transaction_currency_id: str,
        initial_wallet_total: Decimal,
        initial_wallet_balance: Decimal,
        expected_change: Decimal,
    ) -> None:
        """Verify transaction impacts on wallet and it's balance."""
        # Get updated wallet state
        wallet = await WalletCRUD.get_one_by_user(wallet_id, test_user.id)
        wallet_dict = wallet.to_dict()

        # Get updated values
        updated_wallet_total = self._get_wallet_total_value(wallet_dict)
        updated_wallet_balance = self._get_balance_amount(
            wallet_dict, transaction_currency_id
        )

        # Verify wallet updates
        await self._verify_wallet_updates(
            initial_wallet_total,
            initial_wallet_balance,
            updated_wallet_total,
            updated_wallet_balance,
            expected_change,
        )

    async def _verify_transaction_impacts_on_user_app_data(
        self,
        test_user_id: str,
        base_app_data_wallets_value: Decimal,
        base_app_data_net_worth: Decimal,
        expected_change: Decimal,
    ) -> None:
        """Verify user app data updates after transaction modification."""
        updated_state = await self._get_user_app_data_state(test_user_id)
        assert (
            updated_state.wallets_value == base_app_data_wallets_value + expected_change
        )
        assert updated_state.net_worth == base_app_data_net_worth + expected_change

    def _get_wallet_total_value(self, wallet: dict) -> Decimal:
        """Get wallet's total value."""
        return Decimal(str(wallet["total_value"]))

    def _get_balance_amount(self, wallet: dict, currency_id: str) -> Optional[Decimal]:
        """Get specific balance amount for given currency."""
        for balance in wallet["balances_ids"]:
            if str(balance["currency_id"]) == str(currency_id):
                return Decimal(str(balance["amount"]))
        return None

    async def _verify_wallet_updates(
        self,
        initial_total: Decimal,
        initial_balance: Decimal,
        updated_total: Decimal,
        updated_balance: Decimal,
        expected_change: Decimal,
    ) -> None:
        """Verify wallet and balance amounts are updated correctly."""
        assert updated_total == initial_total + expected_change
        assert updated_balance == initial_balance + expected_change

    async def _get_user_app_data_state(self, test_user_id: str) -> UserAppData:
        """Get current user app data state."""
        return await UserAppDataCRUD.get_one_by_user_id(test_user_id)


@pytest.mark.asyncio
class TestCreateTransactionRoutePositive(TestTransactionRoutesSetup):
    """Happy path tests for transaction creation"""

    async def test_create_expense_transaction(self, client, auth_headers, test_user):
        """Test creating an expense transaction."""
        user_app_data = await UserAppDataCRUD.get_one_by_user_id(test_user.id)
        wallet = await self._create_test_wallet(test_user, user_app_data)
        category = await self._create_test_category(test_user)
        transaction_data = self._get_test_transaction_data(wallet, category)

        response = client.post(
            "/transactions", json=transaction_data, headers=auth_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "result" in response_data["data"]
        assert response_data["message"] == "Transaction created successfully"

        await self._verify_transaction_impacts_on_wallet(
            test_user=test_user,
            wallet_id=transaction_data["from_wallet_id"],
            transaction_currency_id=transaction_data["currency_id"],
            initial_wallet_total=Decimal(wallet["total_value"]),
            initial_wallet_balance=Decimal(1000),
            expected_change=-Decimal(transaction_data["amount"]),
        )
        await self._verify_transaction_impacts_on_user_app_data(
            test_user_id=test_user.id,
            base_app_data_wallets_value=Decimal(1000),
            base_app_data_net_worth=Decimal(1000),
            expected_change=-Decimal(transaction_data["amount"]),
        )

    async def test_create_income_transaction(self, client, auth_headers, test_user):
        """Test creating an income transaction."""
        user_app_data = await UserAppDataCRUD.get_one_by_user_id(test_user.id)
        wallet = await self._create_test_wallet(test_user, user_app_data)
        category = await self._create_test_category(test_user)
        transaction_data = self._get_test_transaction_data(
            wallet, category, type=T.INCOME.value
        )

        response = client.post(
            "/transactions", json=transaction_data, headers=auth_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "result" in response_data["data"]
        assert response_data["message"] == "Transaction created successfully"

        await self._verify_transaction_impacts_on_wallet(
            test_user=test_user,
            wallet_id=transaction_data["to_wallet_id"],
            transaction_currency_id=transaction_data["currency_id"],
            initial_wallet_total=Decimal(wallet["total_value"]),
            initial_wallet_balance=Decimal(1000),
            expected_change=Decimal(transaction_data["amount"]),
        )
        await self._verify_transaction_impacts_on_user_app_data(
            test_user_id=test_user.id,
            base_app_data_wallets_value=Decimal(1000),
            base_app_data_net_worth=Decimal(1000),
            expected_change=Decimal(transaction_data["amount"]),
        )

    async def test_create_transfer_transaction(self, client, auth_headers, test_user):
        """Test creating a transfer transaction."""
        user_app_data = await UserAppDataCRUD.get_one_by_user_id(test_user.id)
        from_wallet = await self._create_test_wallet(test_user, user_app_data)
        to_wallet = await self._create_test_wallet(test_user, user_app_data)
        category = await self._create_test_category(test_user)

        transaction_data = self._get_test_transaction_data(
            from_wallet,
            category,
            type=T.TRANSFER.value,
            to_wallet_id=str(to_wallet["_id"]),
        )
        response = client.post(
            "/transactions", json=transaction_data, headers=auth_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "result" in response_data["data"]
        assert response_data["message"] == "Transaction created successfully"

        await self._verify_transaction_impacts_on_wallet(
            test_user=test_user,
            wallet_id=transaction_data["from_wallet_id"],
            transaction_currency_id=transaction_data["currency_id"],
            initial_wallet_total=Decimal(from_wallet["total_value"]),
            initial_wallet_balance=Decimal(1000),
            expected_change=-Decimal(transaction_data["amount"]),
        )
        await self._verify_transaction_impacts_on_wallet(
            test_user=test_user,
            wallet_id=transaction_data["to_wallet_id"],
            transaction_currency_id=transaction_data["currency_id"],
            initial_wallet_total=Decimal(to_wallet["total_value"]),
            initial_wallet_balance=Decimal(1000),
            expected_change=Decimal(transaction_data["amount"]),
        )
        await self._verify_transaction_impacts_on_user_app_data(
            test_user_id=test_user.id,
            base_app_data_wallets_value=Decimal(2000),
            base_app_data_net_worth=Decimal(2000),
            expected_change=Decimal(0),
        )


@pytest.mark.asyncio
class TestReadTransactionRoutePositive(TestTransactionRoutesSetup):
    """Happy path tests for reading a single transaction"""

    async def test_read_transaction(self, client, auth_headers, test_user):
        """Test reading a specific transaction."""
        transaction = await self._create_test_transaction_and_wallet(test_user)

        response = client.get(
            f"/transactions/{str(transaction.id)}", headers=auth_headers
        )

        await self._verify_response(response)
        response_data = response.json()
        assert "transaction" in response_data["data"]
        assert response_data["message"] == "Transaction retrieved successfully"


@pytest.mark.asyncio
class TestReadAllTransactionsRoutePositive(TestTransactionRoutesSetup):
    """Happy path tests for reading all transactions"""

    async def test_read_all_transactions(self, client, auth_headers, test_user):
        """Test reading all transactions."""
        transactions = [
            await self._create_test_transaction_and_wallet(test_user),
            await self._create_test_transaction_and_wallet(test_user),
        ]

        response = client.get("/transactions", headers=auth_headers)

        await self._verify_response(response)
        response_data = response.json()
        assert "transactions" in response_data["data"]
        assert len(response_data["data"]["transactions"]) == len(transactions)
        assert response_data["message"] == "Transactions retrieved successfully"


@pytest.mark.asyncio
class TestFilterTransactionsRoutePositive(TestTransactionRoutesSetup):
    """Happy path tests for filtering transactions"""

    async def test_filter_transactions_by_date(self, client, auth_headers, test_user):
        """Test filtering transactions by date range."""
        transaction = await self._create_test_transaction_and_wallet(test_user)
        start_date = (transaction.date - timedelta(days=1)).isoformat()
        end_date = (transaction.date + timedelta(days=1)).isoformat()

        response = client.get(
            "/transactions/filter",
            params={"start_date": start_date, "end_date": end_date},
            headers=auth_headers,
        )

        await self._verify_response(response)
        response_data = response.json()
        assert "transactions" in response_data["data"]
        assert (
            response_data["message"] == "Filtered transactions retrieved successfully"
        )


@pytest.mark.asyncio
class TestTransactionStatisticsRoutePositive(TestTransactionRoutesSetup):
    """Happy path tests for transaction statistics"""

    async def test_get_transaction_statistics(self, client, auth_headers, test_user):
        """Test getting transaction statistics."""
        transaction = await self._create_test_transaction_and_wallet(test_user)
        start_date = (transaction.date - timedelta(days=1)).isoformat()
        end_date = (transaction.date + timedelta(days=1)).isoformat()

        response = client.get(
            "/transactions/statistics",
            params={"start_date": start_date, "end_date": end_date},
            headers=auth_headers,
        )

        await self._verify_response(response)
        response_data = response.json()
        assert "statistics" in response_data["data"]
        assert (
            response_data["message"] == "Transaction statistics retrieved successfully"
        )


@pytest.mark.asyncio
class TestUpdateTransactionRoutePositive(TestTransactionRoutesSetup):
    """Happy path tests for updating transactions"""

    async def _update_transaction_amount(
        self, transaction_id: str, new_amount: str, auth_headers: dict
    ) -> dict:
        """Send request to update transaction amount."""
        response = self.client.put(
            f"/transactions/{transaction_id}",
            json={"amount": new_amount},
            headers=auth_headers,
        )
        await self._verify_response(response)
        return response.json()

    def _calculate_balance_change(
        self, initial_amount: Decimal, new_amount: Decimal, transaction_type: str
    ) -> Decimal:
        """Calculate expected balance change based on transaction type."""
        amount_difference = new_amount - initial_amount
        # For expense transactions, increasing amount means decreasing wallet balance
        return (
            -amount_difference
            if transaction_type == T.EXPENSE.value
            else amount_difference
        )

    async def test_update_transaction_amount(self, client, auth_headers, test_user):
        """Test updating transaction amount and verifying all related updates."""
        # Create transaction
        transaction = await self._create_test_transaction_and_wallet(test_user)

        # Get initial states after creation
        initial_user_app_data_state = await self._get_user_app_data_state(test_user.id)
        wallet = await WalletCRUD.get_one_by_user(
            str(transaction.to_wallet_id.id), test_user.id
        )
        initial_wallet_total = self._get_wallet_total_value(wallet.to_dict())
        initial_wallet_balance = self._get_balance_amount(
            wallet.to_dict(), transaction.currency_id.id
        )

        # Update transaction
        new_amount = Decimal("200.00")
        response = client.put(
            f"/transactions/{str(transaction.id)}",
            json={"amount": str(new_amount)},
            headers=auth_headers,
        )

        # Verify response
        await self._verify_response(response)
        response_data = response.json()
        assert "transaction" in response_data["data"]
        assert response_data["message"] == "Transaction updated successfully"
        assert Decimal(response_data["data"]["transaction"]["amount"]) == new_amount

        # Calculate expected change
        expected_change = self._calculate_balance_change(
            transaction.amount, new_amount, transaction.type
        )

        await self._verify_transaction_impacts_on_wallet(
            test_user=test_user,
            wallet_id=str(transaction.to_wallet_id.id),
            transaction_currency_id=str(transaction.currency_id.id),
            initial_wallet_total=initial_wallet_total,
            initial_wallet_balance=initial_wallet_balance,
            expected_change=expected_change,
        )
        await self._verify_transaction_impacts_on_user_app_data(
            test_user_id=test_user.id,
            base_app_data_wallets_value=initial_user_app_data_state.wallets_value,
            base_app_data_net_worth=initial_user_app_data_state.net_worth,
            expected_change=expected_change,
        )

    async def test_update_transaction_description(
        self, client, auth_headers, test_user
    ):
        """Test updating transaction description."""
        transaction = await self._create_test_transaction_and_wallet(test_user)
        update_data = {"description": "Updated description"}

        response = client.put(
            f"/transactions/{str(transaction.id)}",
            json=update_data,
            headers=auth_headers,
        )

        await self._verify_response(response)
        response_data = response.json()
        assert (
            response_data["data"]["transaction"]["description"] == "Updated description"
        )

    async def test_update_transaction_date(self, client, auth_headers, test_user):
        """Test updating transaction date."""
        transaction = await self._create_test_transaction_and_wallet(test_user)
        new_date = datetime.utcnow() + timedelta(days=1)
        update_data = {"date": new_date.isoformat()}

        response = client.put(
            f"/transactions/{str(transaction.id)}",
            json=update_data,
            headers=auth_headers,
        )

        await self._verify_response(response)
        response_data = response.json()
        assert "transaction" in response_data["data"]

    async def test_update_transaction_category(self, client, auth_headers, test_user):
        """Test updating transaction category."""
        transaction = await self._create_test_transaction_and_wallet(test_user)
        new_category = await self._create_test_category(test_user)
        update_data = {"category_id": str(new_category["_id"])}

        response = client.put(
            f"/transactions/{str(transaction.id)}",
            json=update_data,
            headers=auth_headers,
        )

        await self._verify_response(response)
        response_data = response.json()
        assert response_data["data"]["transaction"]["category_id"] == str(
            new_category["_id"]
        )

    async def test_update_transaction_multiple_fields(
        self, client, auth_headers, test_user
    ):
        """Test updating multiple transaction fields."""
        transaction = await self._create_test_transaction_and_wallet(test_user)
        update_data = {
            "amount": "300.00",
            "description": "Updated description",
            "date": datetime.utcnow().isoformat(),
        }

        response = client.put(
            f"/transactions/{str(transaction.id)}",
            json=update_data,
            headers=auth_headers,
        )

        await self._verify_response(response)
        response_data = response.json()
        transaction_data = response_data["data"]["transaction"]
        assert Decimal(transaction_data["amount"]) == Decimal("300.00")
        assert transaction_data["description"] == "Updated description"

        wallet = Wallet.objects.first()
        await self._verify_transaction_impacts_on_wallet(
            test_user=test_user,
            wallet_id=wallet.id,
            transaction_currency_id=transaction_data["currency_id"],
            initial_wallet_total=Decimal(1000),
            initial_wallet_balance=Decimal(1000),
            expected_change=Decimal(transaction_data["amount"]),
        )
        await self._verify_transaction_impacts_on_user_app_data(
            test_user_id=test_user.id,
            base_app_data_wallets_value=Decimal(1000),
            base_app_data_net_worth=Decimal(1000),
            expected_change=Decimal(transaction_data["amount"]),
        )


@pytest.mark.asyncio
class TestDeleteTransactionRoutePositive(TestTransactionRoutesSetup):
    """Happy path tests for deleting transactions"""

    async def test_delete_transaction(self, client, auth_headers, test_user):
        """Test deleting a transaction and verifying all related updates."""
        # Create transaction
        transaction = await self._create_test_transaction_and_wallet(test_user)

        # Get initial states before deletion
        initial_user_app_data_state = await self._get_user_app_data_state(test_user.id)
        wallet = await WalletCRUD.get_one_by_user(
            str(transaction.to_wallet_id.id), test_user.id
        )
        initial_wallet_total = self._get_wallet_total_value(wallet.to_dict())
        initial_wallet_balance = self._get_balance_amount(
            wallet.to_dict(), transaction.currency_id.id
        )

        # Delete transaction
        response = client.delete(
            f"/transactions/{str(transaction.id)}", headers=auth_headers
        )

        # Verify response
        await self._verify_response(response)
        response_data = response.json()
        assert response_data["message"] == "Transaction deleted successfully"

        # Calculate expected change (reverse of the transaction amount)
        expected_change = (
            -transaction.amount
            if transaction.type == T.INCOME.value
            else transaction.amount
        )

        # Verify wallet and user app data updates
        await self._verify_transaction_impacts_on_wallet(
            test_user=test_user,
            wallet_id=str(transaction.to_wallet_id.id),
            transaction_currency_id=str(transaction.currency_id.id),
            initial_wallet_total=initial_wallet_total,
            initial_wallet_balance=initial_wallet_balance,
            expected_change=expected_change,
        )
        await self._verify_transaction_impacts_on_user_app_data(
            test_user_id=test_user.id,
            base_app_data_wallets_value=initial_user_app_data_state.wallets_value,
            base_app_data_net_worth=initial_user_app_data_state.net_worth,
            expected_change=expected_change,
        )

    async def test_delete_transfer_transaction(self, client, auth_headers, test_user):
        """Test deleting a transfer transaction."""
        # Create transfer transaction
        user_app_data = await UserAppDataCRUD.get_one_by_user_id(test_user.id)
        from_wallet = await self._create_test_wallet(test_user, user_app_data)
        to_wallet = await self._create_test_wallet(test_user, user_app_data)
        category = await self._create_test_category(test_user)

        transaction_data = self._get_test_transaction_data(
            from_wallet,
            category,
            type=T.TRANSFER.value,
            to_wallet_id=str(to_wallet["_id"]),
        )

        # Create transaction through API
        response = client.post(
            "/transactions", json=transaction_data, headers=auth_headers
        )
        created_transaction = response.json()["data"]["result"]
        await asyncio.sleep(1.0) 
        # Get initial states
        initial_from_wallet = await WalletCRUD.get_one_by_user(
            transaction_data["from_wallet_id"], test_user.id
        )
        initial_to_wallet = await WalletCRUD.get_one_by_user(
            transaction_data["to_wallet_id"], test_user.id
        )
        # Delete transaction
        response = client.delete(
            f"/transactions/{created_transaction['_id']}", headers=auth_headers
        )

        # Verify response
        await self._verify_response(response)
        response_data = response.json()
        assert response_data["message"] == "Transaction deleted successfully"

        # Verify impacts on both wallets
        await self._verify_transaction_impacts_on_wallet(
            test_user=test_user,
            wallet_id=transaction_data["from_wallet_id"],
            transaction_currency_id=transaction_data["currency_id"],
            initial_wallet_total=self._get_wallet_total_value(
                initial_from_wallet.to_dict()
            ),
            initial_wallet_balance=Decimal("900.00"),
            expected_change=Decimal(transaction_data["amount"]),
        )
        await self._verify_transaction_impacts_on_wallet(
            test_user=test_user,
            wallet_id=transaction_data["to_wallet_id"],
            transaction_currency_id=transaction_data["currency_id"],
            initial_wallet_total=self._get_wallet_total_value(
                initial_to_wallet.to_dict()
            ),
            initial_wallet_balance=Decimal("1100.00"),
            expected_change=-Decimal(transaction_data["amount"]),
        )

        await self._verify_transaction_impacts_on_user_app_data(
            test_user_id=test_user.id,
            base_app_data_wallets_value=Decimal("2000.00"),
            base_app_data_net_worth=Decimal("2000.00"),
            expected_change=Decimal(0),
        )
