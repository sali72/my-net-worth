from typing import List

import mongoengine
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

        with mongoengine.connection.get_connection().start_session() as session:
            with session.start_transaction():
                transaction_in_db: Transaction = await TransactionCRUD.create_one(
                    transaction
                )
                await cls._update_wallet_balances(transaction_in_db, user.id)
                return transaction_in_db.to_dict()

    @classmethod
    async def _validate_transaction_data(
        cls, transaction_schema: TransactionCreateSchema, user_id
    ) -> None:
        await CategoryCRUD.get_one_by_user(transaction_schema.category_id, user_id)
        await CurrencyCRUD.get_one_by_user(transaction_schema.currency_id, user_id)

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

    @staticmethod
    def _validate_currency_match(
        from_wallet: Wallet, to_wallet: Wallet, currency_id: str
    ) -> bool:
        from_currency_match = any(
            balance.currency_id.pk == currency_id
            for balance in from_wallet.currency_balances
        )
        to_currency_match = any(
            balance.currency_id.pk == currency_id
            for balance in to_wallet.currency_balances
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
    def _adjust_balance_amount(cls, currency_id, amount, add, wallet):
        for currency_balance in wallet.currency_balances:
            if currency_balance.currency_id.pk == currency_id:
                if add:
                    currency_balance.balance += amount
                else:
                    currency_balance.balance -= amount
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
        for currency_balance in wallet.currency_balances:
            if currency_balance.currency_id.pk == currency_id:
                return currency_balance.balance >= amount
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
        updated_transaction = cls._create_transaction_obj_for_update(
            transaction_update_schema
        )
        await TransactionCRUD.update_one_by_user(
            user_id, transaction_id, updated_transaction
        )
        transaction_from_db = await TransactionCRUD.get_one_by_id(transaction_id)
        return transaction_from_db.to_dict()

    @classmethod
    def _create_transaction_obj_for_update(
        cls, transaction_schema: TransactionUpdateSchema
    ) -> Transaction:
        return Transaction(
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
    async def delete_transaction(cls, transaction_id: str, user_id: str) -> bool:
        await TransactionCRUD.delete_one_by_user(user_id, transaction_id)
        return True
