from mongoengine import DoesNotExist, QuerySet
from models.models import Transaction
from datetime import datetime


class TransactionCRUD:

    @classmethod
    async def create_one(cls, transaction: Transaction) -> Transaction:
        transaction.clean()
        transaction.save()
        return transaction

    @classmethod
    async def get_one_by_user(cls, transaction_id: str, user_id: str) -> Transaction:
        try:
            return Transaction.objects.get(id=transaction_id, user_id=user_id)
        except DoesNotExist:
            raise DoesNotExist(
                f"Transaction with id {transaction_id} for user {user_id} does not exist"
            )

    @classmethod
    async def get_all_by_user_id(cls, user_id: str) -> QuerySet:
        transactions = Transaction.objects(user_id=user_id)
        return transactions

    @classmethod
    async def get_one_by_id(cls, transaction_id: str) -> Transaction:
        return Transaction.objects.get(id=transaction_id)

    @classmethod
    async def update_one_by_user(
        cls, user_id: str, transaction_id: str, updated_transaction: Transaction
    ):
        transaction = await cls.get_one_by_user(transaction_id, user_id)
        cls._update_transaction_fields(transaction, updated_transaction)
        cls._update_timestamp(transaction)
        transaction.clean()
        transaction.save()

    @staticmethod
    def _update_transaction_fields(
        transaction: Transaction, updated_transaction: Transaction
    ):
        if updated_transaction.from_wallet_id is not None:
            transaction.from_wallet_id = updated_transaction.from_wallet_id
        if updated_transaction.to_wallet_id is not None:
            transaction.to_wallet_id = updated_transaction.to_wallet_id
        if updated_transaction.category_id is not None:
            transaction.category_id = updated_transaction.category_id
        if updated_transaction.currency_id is not None:
            transaction.currency_id = updated_transaction.currency_id
        if updated_transaction.type is not None:
            transaction.type = updated_transaction.type
        if updated_transaction.amount is not None:
            transaction.amount = updated_transaction.amount
        if updated_transaction.date is not None:
            transaction.date = updated_transaction.date
        if updated_transaction.description is not None:
            transaction.description = updated_transaction.description

    @staticmethod
    def _update_timestamp(transaction: Transaction):
        transaction.updated_at = datetime.utcnow()

    @classmethod
    async def delete_one_by_user(cls, user_id: str, transaction_id: str) -> bool:
        result = Transaction.objects(id=transaction_id, user_id=user_id).delete()
        if result == 0:
            raise DoesNotExist(
                f"Transaction with id {transaction_id} for user {user_id} does not exist"
            )
        return result > 0
