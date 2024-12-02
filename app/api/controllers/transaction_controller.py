from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from mongoengine import ValidationError

from app.crud.category_crud import CategoryCRUD
from app.crud.transaction_crud import TransactionCRUD
from app.crud.wallet_crud import WalletCRUD
from models.models import Transaction, User, Wallet
from models.schemas import TransactionCreateSchema, TransactionUpdateSchema


class TransactionController:
    @classmethod
    async def create_transaction(
        cls, transaction_schema: TransactionCreateSchema, user: User
    ) -> Transaction:
        await cls._validate_transaction_data(transaction_schema, user.id)
        transaction = cls._create_transaction_obj_to_create(transaction_schema, user.id)
        transaction_in_db: Transaction = await TransactionCRUD.create_one(transaction)
        try:
            await cls._adjust_wallet_balances(transaction_in_db, user.id)
            return transaction_in_db
        except Exception as e:
            await TransactionCRUD.delete_one_by_user(transaction_in_db.id, user.id)
            raise e

    @classmethod
    async def get_transaction(cls, transaction_id: str, user_id: str) -> Dict:
        transaction = await TransactionCRUD.get_one_by_user(transaction_id, user_id)
        return transaction.to_dict()

    @classmethod
    async def get_all_transactions(cls, user_id: str) -> List[Dict]:
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
    ) -> Dict:
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
            await cls._handle_amount_update(
                existing_transaction,
                updated_transaction.amount,
                user_id,
                transaction_id,
            )

        transaction_from_db = await TransactionCRUD.get_one_by_id(transaction_id)
        return transaction_from_db.to_dict()

    @classmethod
    async def delete_transaction(cls, transaction_id: str, user_id: str) -> Transaction:
        transaction = await TransactionCRUD.get_one_by_user(transaction_id, user_id)
        await TransactionCRUD.delete_one_by_user(transaction_id, user_id)
        try:
            await cls._adjust_wallet_balances(transaction, user_id, multiplier=-1)
            return transaction
        except Exception as e:
            await TransactionCRUD.create_one(transaction)
            raise e

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
    ) -> List[Dict]:
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
        total_income, total_expense = cls._calculate_income_expense(transactions)
        net_balance = total_income - total_expense
        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "net_balance": net_balance,
        }

    @classmethod
    async def _validate_transaction_data(
        cls, transaction_schema: TransactionCreateSchema, user_id: str
    ) -> None:
        if transaction_schema.category_id:
            await CategoryCRUD.get_one_by_user(transaction_schema.category_id, user_id)
        await cls._check_currency_in_wallets(transaction_schema, user_id)

    @classmethod
    async def _check_currency_in_wallets(
        cls, transaction_schema: TransactionCreateSchema, user_id: str
    ) -> None:
        wallets = await cls._get_wallets_for_transaction(transaction_schema, user_id)
        currency_id = transaction_schema.currency_id

        for wallet in wallets:
            if not cls._currency_exists_in_wallet(wallet, currency_id):
                raise ValidationError(
                    f"Currency does not exist in the wallet {wallet.id} for transaction type '{transaction_schema.type}'."
                )

    @classmethod
    async def _get_wallets_for_transaction(
        cls, transaction_schema: TransactionCreateSchema, user_id: str
    ) -> List[Wallet]:
        wallets = []
        if transaction_schema.type in ["expense", "transfer"]:
            from_wallet = await WalletCRUD.get_one_by_user(
                transaction_schema.from_wallet_id, user_id
            )
            wallets.append(from_wallet)
        if transaction_schema.type in ["income", "transfer"]:
            to_wallet = await WalletCRUD.get_one_by_user(
                transaction_schema.to_wallet_id, user_id
            )
            wallets.append(to_wallet)
        return wallets

    @staticmethod
    def _currency_exists_in_wallet(wallet: Wallet, currency_id: str) -> bool:
        return any(
            str(balance.currency_id.pk) == currency_id
            for balance in wallet.balances_ids
        )

    @classmethod
    async def _adjust_wallet_balances(
        cls,
        transaction: Transaction,
        user_id: str,
        amount: Decimal = None,
        multiplier: int = 1,
    ) -> None:
        if amount is None:
            amount = transaction.amount
        amount *= multiplier

        adjustments = cls._get_balance_adjustments(transaction, amount)
        for wallet_id, currency_id, amt in adjustments:
            await cls._adjust_wallet_balance(wallet_id, currency_id, amt, user_id)

    @classmethod
    def _get_balance_adjustments(
        cls, transaction: Transaction, amount: Decimal
    ) -> List[tuple]:
        adjustments = []
        if transaction.type == "income":
            adjustments.append(
                (transaction.to_wallet_id.id, transaction.currency_id.id, amount)
            )
        elif transaction.type == "expense":
            adjustments.append(
                (transaction.from_wallet_id.id, transaction.currency_id.id, -amount)
            )
        elif transaction.type == "transfer":
            adjustments.append(
                (transaction.from_wallet_id.id, transaction.currency_id.id, -amount)
            )
            adjustments.append(
                (transaction.to_wallet_id.id, transaction.currency_id.id, amount)
            )
        return adjustments

    @classmethod
    async def _adjust_wallet_balance(
        cls, wallet_id: str, currency_id: str, amount: Decimal, user_id: str
    ) -> None:
        wallet = await WalletCRUD.get_one_by_user(wallet_id, user_id)
        cls._adjust_balance(wallet, currency_id, amount)
        await WalletCRUD.update_one_by_user(user_id, wallet_id, wallet)

    @classmethod
    def _adjust_balance(cls, wallet: Wallet, currency_id: str, amount: Decimal) -> None:
        for balance in wallet.balances_ids:
            if balance.currency_id.pk == currency_id:
                balance.amount += amount
                if balance.amount < 0:
                    raise ValidationError("Insufficient balance in the wallet.")
                return
        raise ValidationError("Currency does not exist in the wallet.")

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
    async def _handle_amount_update(
        cls,
        existing_transaction: Transaction,
        new_amount: Decimal,
        user_id: str,
        transaction_id: str,
    ) -> None:
        amount_difference = new_amount - existing_transaction.amount
        if amount_difference != 0:
            try:
                await cls._adjust_wallet_balances(
                    existing_transaction, user_id, amount=amount_difference
                )
            except Exception as e:
                await cls._rollback_transaction_update(
                    user_id, transaction_id, existing_transaction
                )
                raise e

    @classmethod
    async def _rollback_transaction_update(
        cls, user_id: str, transaction_id: str, existing_transaction: Transaction
    ) -> None:
        await TransactionCRUD.update_one_by_user(
            user_id, transaction_id, existing_transaction
        )

    @staticmethod
    def _calculate_income_expense(
        transactions: List[Transaction],
    ) -> Tuple[Decimal, Decimal]:
        total_income = Decimal(0)
        total_expense = Decimal(0)
        for transaction in transactions:
            if transaction.type == "income":
                total_income += transaction.amount
            elif transaction.type == "expense":
                total_expense += transaction.amount
        return total_income, total_expense
