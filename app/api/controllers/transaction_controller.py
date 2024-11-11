from typing import List

from fastapi import HTTPException, status

from app.crud.transaction_crud import TransactionCRUD
from models.models import Transaction, User
from models.schemas import TransactionCreateSchema, TransactionUpdateSchema


class TransactionController:

    @classmethod
    async def create_transaction(
        cls, transaction_schema: TransactionCreateSchema, user: User
    ) -> str:
        transaction = await cls.__create_transaction_obj_to_create(
            transaction_schema, user.id
        )
        transaction_in_db: Transaction = await TransactionCRUD.create_one(transaction)
        return transaction_in_db.to_dict()

    @classmethod
    async def __create_transaction_obj_to_create(
        cls, transaction_schema: TransactionCreateSchema, user_id: str
    ) -> Transaction:
        return Transaction(
            user_id=user_id,
            wallet_id=transaction_schema.wallet_id,
            category_id=transaction_schema.category_id,
            type=transaction_schema.type,
            amount=transaction_schema.amount,
            date=transaction_schema.date,
            description=transaction_schema.description,
        )

    @classmethod
    async def get_transaction(cls, transaction_id: str, user_id: str) -> Transaction:
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
    ) -> Transaction:
        updated_transaction = await cls.__create_transaction_obj_for_update(
            transaction_update_schema
        )
        await TransactionCRUD.update_one_by_user(
            user_id, transaction_id, updated_transaction
        )
        transaction_from_db = await TransactionCRUD.get_one_by_id(transaction_id)
        return transaction_from_db.to_dict()

    @classmethod
    async def __create_transaction_obj_for_update(
        cls, transaction_schema: TransactionUpdateSchema
    ) -> Transaction:
        return Transaction(
            wallet_id=transaction_schema.wallet_id,
            category_id=transaction_schema.category_id,
            type=transaction_schema.type,
            amount=transaction_schema.amount,
            date=transaction_schema.date,
            description=transaction_schema.description,
        )

    @classmethod
    async def delete_transaction(cls, transaction_id: str, user_id: str) -> bool:
        await TransactionCRUD.delete_one_by_user(user_id, transaction_id)
        return True

    @staticmethod
    def _raise_http_exception(detail: str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
