from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from mongoengine import ValidationError

from app.crud.category_crud import CategoryCRUD
from app.crud.currency_crud import CurrencyCRUD
from app.crud.transaction_crud import TransactionCRUD
from app.crud.wallet_crud import WalletCRUD
from models.models import Transaction, User, Wallet
from models.schemas import TransactionCreateSchema, TransactionUpdateSchema


class TransactionController:

    @classmethod
    async def create_transaction(
        cls, transaction_schema: TransactionCreateSchema, user: User
    ) -> dict:
        await cls._validate_transaction_data(transaction_schema, user.id)
        transaction = cls._create_transaction_obj_to_create(transaction_schema, user.id)

        transaction_in_db: Transaction = await TransactionCRUD.create_one(transaction)
        # make sure updating balances occur if transaction is created
        try:
            await cls._update_wallet_balances(transaction_in_db, user.id)
            return transaction_in_db.to_dict()
        except Exception as e:
            await TransactionCRUD.delete_one_by_user(transaction_in_db.id, user.id)
            raise e

    @classmethod
    async def _validate_transaction_data(
        cls, transaction_schema: TransactionCreateSchema, user_id: str
    ) -> None:
        if transaction_schema.category_id:
            await CategoryCRUD.get_one_by_user(transaction_schema.category_id, user_id)

        await cls._check_currency_existence_in_wallets(transaction_schema, user_id)

    @classmethod
    async def _check_currency_existence_in_wallets(
        cls, transaction_schema: TransactionCreateSchema, user_id: str
    ) -> None:
        if transaction_schema.type == "income":
            to_wallet = await WalletCRUD.get_one_by_user(
                transaction_schema.to_wallet_id, user_id
            )
            if not cls._currency_exists_in_wallet(
                to_wallet, transaction_schema.currency_id
            ):
                raise ValidationError(
                    "Currency does not exist in the destination wallet for income transactions."
                )

        elif transaction_schema.type == "expense":
            from_wallet = await WalletCRUD.get_one_by_user(
                transaction_schema.from_wallet_id, user_id
            )
            if not cls._currency_exists_in_wallet(
                from_wallet, transaction_schema.currency_id
            ):
                raise ValidationError(
                    "Currency does not exist in the source wallet for expense transactions."
                )

        elif transaction_schema.type == "transfer":
            from_wallet = await WalletCRUD.get_one_by_user(
                transaction_schema.from_wallet_id, user_id
            )
            to_wallet = await WalletCRUD.get_one_by_user(
                transaction_schema.to_wallet_id, user_id
            )
            if not cls._currency_exists_in_wallet(
                from_wallet, transaction_schema.currency_id
            ) or not cls._currency_exists_in_wallet(
                to_wallet, transaction_schema.currency_id
            ):
                raise ValidationError(
                    "Currency must exist in both source and destination wallets for transfer transactions."
                )

    @staticmethod
    def _currency_exists_in_wallet(wallet: Wallet, currency_id: str) -> bool:
        return any(
            str(balance.currency_id.pk) == currency_id
            for balance in wallet.balances_ids
        )

    @classmethod
    async def _update_wallet_balances(
        cls, transaction: Transaction, user_id: str
    ) -> None:
        if transaction.type == "income":
            await cls._get_wallet_and_update_balance(
                transaction.to_wallet_id.id,
                transaction.currency_id.id,
                transaction.amount,
                user_id,
                add=True,
            )
        elif transaction.type == "expense":
            await cls._get_wallet_and_update_balance(
                transaction.from_wallet_id.id,
                transaction.currency_id.id,
                transaction.amount,
                user_id,
                add=False,
            )
        elif transaction.type == "transfer":
            await cls._update_wallet_balance_transfer(transaction, user_id)

    @classmethod
    async def _update_wallet_balance_transfer(cls, transaction, user_id):
        from_wallet, to_wallet = await cls._fetch_and_validate_wallets_for_transaction(
            transaction, user_id
        )

        await cls._update_wallet_balance(
            from_wallet,
            transaction.from_wallet_id.id,
            transaction.currency_id.id,
            transaction.amount,
            user_id,
            add=False,
        )
        await cls._update_wallet_balance(
            to_wallet,
            transaction.to_wallet_id.id,
            transaction.currency_id.id,
            transaction.amount,
            user_id,
            add=True,
        )

    @classmethod
    async def _fetch_and_validate_wallets_for_transaction(
        cls, transaction, user_id: str
    ) -> Tuple[Wallet, Wallet]:
        from_wallet = await WalletCRUD.get_one_by_user(
            transaction.from_wallet_id.id, user_id
        )
        to_wallet = await WalletCRUD.get_one_by_user(
            transaction.to_wallet_id.id, user_id
        )

        if not cls._validate_currency_match(
            from_wallet, to_wallet, transaction.currency_id.id
        ):
            raise ValidationError(
                "Currency of the source wallet must match the destination wallet for transfers."
            )

        return from_wallet, to_wallet

    @staticmethod
    def _validate_currency_match(
        from_wallet: Wallet, to_wallet: Wallet, currency_id: str
    ) -> bool:
        from_currency_match = any(
            balance.currency_id.pk == currency_id
            for balance in from_wallet.balances_ids
        )
        to_currency_match = any(
            balance.currency_id.pk == currency_id for balance in to_wallet.balances_ids
        )
        return from_currency_match and to_currency_match

    @classmethod
    async def _get_wallet_and_update_balance(
        cls, wallet_id: str, currency_id: str, amount: float, user_id: str, add: bool
    ) -> None:
        wallet = await WalletCRUD.get_one_by_user(wallet_id, user_id)

        await cls._update_wallet_balance(
            wallet,
            wallet_id,
            currency_id,
            amount,
            user_id,
            add,
        )

    @classmethod
    async def _update_wallet_balance(
        cls,
        wallet: Wallet,
        wallet_id: str,
        currency_id: str,
        amount: float,
        user_id: str,
        add: bool,
    ) -> None:

        if not add:
            await cls._validate_balance_sufficiency(wallet, currency_id, amount)

        cls._adjust_balance_amount(currency_id, amount, add, wallet)

        await WalletCRUD.update_one_by_user(user_id, wallet_id, wallet)

    @classmethod
    def _adjust_balance_amount(cls, currency_id, amount, add, wallet: Wallet):
        for balance in wallet.balances_ids:
            if balance.currency_id.pk == currency_id:
                if add:
                    balance.amount += amount
                else:
                    balance.amount -= amount
                break

    @classmethod
    async def _validate_balance_sufficiency(
        cls,
        wallet: Wallet,
        currency_id: str,
        amount: float,
    ):
        if not await cls._has_sufficient_balance(wallet, currency_id, amount):
            raise ValidationError(
                "Insufficient balance in the wallet for this transaction."
            )

    @classmethod
    async def _has_sufficient_balance(
        cls, wallet: Wallet, currency_id: str, amount: float
    ) -> bool:
        for balance in wallet.balances_ids:
            if balance.currency_id.pk == currency_id:
                return balance.amount >= amount
        return False

    @classmethod
    def _create_transaction_obj_to_create(
        cls, transaction_schema: TransactionCreateSchema, user_id: str
    ) -> Transaction:
        return Transaction(
            user_id=user_id,
            from_wallet_id=transaction_schema.from_wallet_id,
            to_wallet_id=transaction_schema.to_wallet_id,
            category_id=transaction_schema.category_id,
            currency_id=transaction_schema.currency_id,
            type=transaction_schema.type,
            amount=transaction_schema.amount,
            date=transaction_schema.date,
            description=transaction_schema.description,
        )

    @classmethod
    async def get_transaction(cls, transaction_id: str, user_id: str) -> dict:
        transaction = await TransactionCRUD.get_one_by_user(transaction_id, user_id)
        return transaction.to_dict()

    @classmethod
    async def get_all_transactions(cls, user_id: str) -> List[dict]:
        transactions: List[Transaction] = await TransactionCRUD.get_all_by_user_id(
            user_id
        )
        return [transaction.to_dict() for transaction in transactions]

    @classmethod
    async def update_transaction(
        cls,
        transaction_id: str,
        transaction_update_schema: TransactionUpdateSchema,
        user_id: str,
    ) -> dict:

        existing_transaction = await TransactionCRUD.get_one_by_user(
            transaction_id, user_id
        )
        updated_transaction = cls._create_transaction_obj_for_update(
            transaction_update_schema
        )

        await TransactionCRUD.update_one_by_user(
            user_id, transaction_id, updated_transaction
        )

        if updated_transaction.amount:
            await cls._update_wallet_amount_differences(
                transaction_id, user_id, existing_transaction, updated_transaction
            )

        transaction_from_db = await TransactionCRUD.get_one_by_id(transaction_id)
        return transaction_from_db.to_dict()

    @classmethod
    async def _update_wallet_amount_differences(
        cls, transaction_id, user_id, existing_transaction, updated_transaction
    ):
        amount_difference = updated_transaction.amount - existing_transaction.amount

        if amount_difference != 0:
            try:
                await cls._adjust_wallet_balances_for_update(
                    existing_transaction,
                    user_id,
                    amount_difference,
                )
            except Exception as e:
                await TransactionCRUD.update_one_by_user(
                    user_id, transaction_id, existing_transaction
                )
                raise e

    @classmethod
    def _create_transaction_obj_for_update(
        cls, transaction_schema: TransactionUpdateSchema
    ) -> Transaction:
        return Transaction(
            category_id=transaction_schema.category_id,
            amount=transaction_schema.amount,
            date=transaction_schema.date,
            description=transaction_schema.description,
        )

    @classmethod
    async def _adjust_wallet_balances_for_update(
        cls,
        existing_transaction: Transaction,
        user_id: str,
        amount_difference: float,
    ) -> None:
        if existing_transaction.type == "income":
            await cls._get_wallet_and_update_balance(
                existing_transaction.to_wallet_id.id,
                existing_transaction.currency_id.id,
                abs(amount_difference),
                user_id,
                add=(amount_difference > 0),
            )
        elif existing_transaction.type == "expense":
            await cls._get_wallet_and_update_balance(
                existing_transaction.from_wallet_id.id,
                existing_transaction.currency_id.id,
                abs(amount_difference),
                user_id,
                add=(amount_difference < 0),
            )
        elif existing_transaction.type == "transfer":
            await cls._adjust_transfer_wallet_balances_for_update(
                existing_transaction, user_id, amount_difference
            )

    @classmethod
    async def _adjust_transfer_wallet_balances_for_update(
        cls,
        existing_transaction: Transaction,
        user_id: str,
        amount_difference: float,
    ) -> None:
        await cls._get_wallet_and_update_balance(
            existing_transaction.from_wallet_id.id,
            existing_transaction.currency_id.id,
            abs(amount_difference),
            user_id,
            add=(amount_difference < 0),
        )
        await cls._get_wallet_and_update_balance(
            existing_transaction.to_wallet_id.id,
            existing_transaction.currency_id.id,
            abs(amount_difference),
            user_id,
            add=(amount_difference > 0),
        )

    @classmethod
    async def delete_transaction(cls, transaction_id: str, user_id: str) -> bool:
        transaction = await TransactionCRUD.get_one_by_user(transaction_id, user_id)
        await TransactionCRUD.delete_one_by_user(transaction_id, user_id)
        try:
            await cls._reverse_transaction_effects(transaction, user_id)
            return True
        except Exception as e:
            await TransactionCRUD.create_one(transaction)
            raise e

    @classmethod
    async def _reverse_transaction_effects(
        cls, transaction: Transaction, user_id: str
    ) -> None:
        if transaction.type == "income":
            await cls._reverse_income_effect(transaction, user_id)
        elif transaction.type == "expense":
            await cls._reverse_expense_effect(transaction, user_id)
        elif transaction.type == "transfer":
            await cls._reverse_wallet_balance_transfer(transaction, user_id)

    @classmethod
    async def _reverse_income_effect(
        cls, transaction: Transaction, user_id: str
    ) -> None:
        await cls._get_wallet_and_update_balance(
            transaction.to_wallet_id.id,
            transaction.currency_id.id,
            transaction.amount,
            user_id,
            add=False,  # Reverse the addition
        )

    @classmethod
    async def _reverse_expense_effect(
        cls, transaction: Transaction, user_id: str
    ) -> None:
        await cls._get_wallet_and_update_balance(
            transaction.from_wallet_id.id,
            transaction.currency_id.id,
            transaction.amount,
            user_id,
            add=True,  # Reverse the subtraction
        )

    @classmethod
    async def _reverse_wallet_balance_transfer(cls, transaction, user_id):
        from_wallet, to_wallet = await cls._fetch_and_validate_wallets_for_transaction(
            transaction, user_id
        )

        # Reverse the transfer: add back to the source and subtract from the destination
        await cls._update_wallet_balance(
            from_wallet,
            transaction.from_wallet_id.id,
            transaction.currency_id.id,
            transaction.amount,
            user_id,
            add=True,  # Reverse the subtraction
        )
        await cls._update_wallet_balance(
            to_wallet,
            transaction.to_wallet_id.id,
            transaction.currency_id.id,
            transaction.amount,
            user_id,
            add=False,  # Reverse the addition
        )

    @classmethod
    async def filter_transactions(
        cls,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        transaction_type: Optional[str] = None,
        category_id: Optional[str] = None,
        from_wallet_id: Optional[str] = None,
        to_wallet_id: Optional[str] = None,
    ) -> List[dict]:
        transactions: List[Transaction] = await TransactionCRUD.filter_transactions(
            user_id,
            start_date,
            end_date,
            transaction_type,
            category_id,
            from_wallet_id,
            to_wallet_id,
        )

        return [transaction.to_dict() for transaction in transactions]

    @classmethod
    async def calculate_statistics(
        cls, user_id: str, start_date: Optional[datetime], end_date: Optional[datetime]
    ) -> Dict[str, Decimal]:
        transactions = await TransactionCRUD.filter_transactions(
            user_id, start_date, end_date
        )

        total_income = Decimal(0)
        total_expense = Decimal(0)

        for transaction in transactions:
            if transaction.type == "income":
                total_income += transaction.amount
            elif transaction.type == "expense":
                total_expense += transaction.amount

        net_balance = total_income - total_expense

        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "net_balance": net_balance,
        }
