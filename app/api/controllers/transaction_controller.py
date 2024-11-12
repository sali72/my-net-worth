from typing import List

import mongoengine

from app.crud.category_crud import CategoryCRUD
from app.crud.currency_crud import CurrencyCRUD
from app.crud.transaction_crud import TransactionCRUD
from app.crud.wallet_crud import WalletCRUD
from models.models import Transaction, User
from models.schemas import TransactionCreateSchema, TransactionUpdateSchema


class TransactionController:

    @classmethod
    async def create_transaction(
        cls, transaction_schema: TransactionCreateSchema, user: User
    ) -> dict:
        await cls._validate_transaction_data(transaction_schema, user.id)
        transaction = cls._create_transaction_obj_to_create(transaction_schema, user.id)

        # Start a session using mongoengine
        with mongoengine.connection.get_connection().start_session() as session:
            with session.start_transaction():
                transaction_in_db: Transaction = await TransactionCRUD.create_one(
                    transaction
                )
                print(">>: ", user.id)
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
            await cls._update_wallet_balance(
                transaction.to_wallet_id.id,
                transaction.currency_id.id,
                transaction.amount,
                user_id,
                add=True,
            )
        elif transaction.type == "expense":
            await cls._update_wallet_balance(
                transaction.from_wallet_id.id,
                transaction.currency_id.id,
                transaction.amount,
                user_id,
                add=False,
            )
        elif transaction.type == "transfer":
            await cls._update_wallet_balance(
                transaction.from_wallet_id.id,
                transaction.currency_id.id,
                transaction.amount,
                user_id,
                add=False,
            )
            await cls._update_wallet_balance(
                transaction.to_wallet_id.id,
                transaction.currency_id.id,
                transaction.amount,
                user_id,
                add=True,
            )

    @classmethod
    async def _update_wallet_balance(
        cls, wallet_id: str, currency_id: str, amount: float, user_id: str, add: bool
    ) -> None:
        wallet = await WalletCRUD.get_one_by_user(wallet_id, user_id)
        print("userid: ", user_id)
        for currency_balance in wallet.currency_balances:
            if currency_balance.currency_id.pk == currency_id:
                if add:
                    currency_balance.balance += amount
                else:
                    currency_balance.balance -= amount
                break
        await WalletCRUD.update_one_by_user(user_id, wallet_id, wallet)

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