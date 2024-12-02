from datetime import datetime
from typing import List, Optional

from mongoengine import DoesNotExist, QuerySet
from mongoengine.queryset.visitor import Q

from models.models import Transaction


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
        return Transaction.objects(user_id=user_id)

    @classmethod
    async def get_one_by_id(cls, transaction_id: str) -> Transaction:
        return Transaction.objects.get(id=transaction_id)

    @classmethod
    async def update_one_by_user(
        cls, user_id: str, transaction_id: str, updated_transaction: Transaction
    ) -> None:
        transaction = await cls.get_one_by_user(transaction_id, user_id)
        cls._update_transaction_fields(transaction, updated_transaction)
        cls._update_timestamp(transaction)
        transaction.clean()
        transaction.save()

    @classmethod
    async def delete_one_by_user(cls, transaction_id: str, user_id: str) -> bool:
        result = Transaction.objects(id=transaction_id, user_id=user_id).delete()
        if result == 0:
            raise DoesNotExist(
                f"Transaction with id {transaction_id} for user {user_id} does not exist"
            )
        return result > 0

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
    ) -> List[Transaction]:
        query = Q(user_id=user_id)
        if start_date:
            query &= Q(date__gte=start_date)
        if end_date:
            query &= Q(date__lte=end_date)
        if transaction_type:
            query &= Q(type=transaction_type)
        if category_id:
            query &= Q(category_id=category_id)
        if from_wallet_id:
            query &= Q(from_wallet_id=from_wallet_id)
        if to_wallet_id:
            query &= Q(to_wallet_id=to_wallet_id)

        return list(Transaction.objects(query))

    @staticmethod
    def _update_transaction_fields(
        transaction: Transaction, updated_transaction: Transaction
    ) -> None:
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
    def _update_timestamp(transaction: Transaction) -> None:
        transaction.updated_at = datetime.utcnow()
