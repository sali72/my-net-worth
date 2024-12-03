from datetime import datetime
from decimal import Decimal
from typing import List

from fastapi import HTTPException, status
from mongoengine import DoesNotExist, QuerySet

from app.crud.balance_crud import BalanceCRUD
from models.models import Balance, Wallet


class WalletCRUD:

    @classmethod
    async def create_one(cls, wallet: Wallet) -> Wallet:
        wallet.clean()
        wallet.save()
        return wallet

    @classmethod
    async def get_one_by_user(cls, wallet_id: str, user_id: str) -> Wallet:
        try:
            return Wallet.objects.get(id=wallet_id, user_id=user_id)
        except DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wallet with id {wallet_id} for user {user_id} does not exist",
            )

    @classmethod
    async def get_all_by_user_id_optional(cls, user_id: str) -> QuerySet:
        return Wallet.objects(user_id=user_id)

    @classmethod
    async def get_one_by_id(cls, wallet_id: str) -> Wallet:
        try:
            return Wallet.objects.get(id=wallet_id)
        except DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wallet with id {wallet_id} does not exist",
            )

    @classmethod
    async def update_one_by_user(
        cls, user_id: str, wallet_id: str, updated_wallet: Wallet
    ) -> None:
        wallet = await cls.get_one_by_user(wallet_id, user_id)
        cls.__update_wallet_fields(wallet, updated_wallet)
        await cls.__update_balances(wallet, updated_wallet)
        cls.__update_timestamp(wallet)
        wallet.clean()
        wallet.save()

    @staticmethod
    def __update_wallet_fields(wallet: Wallet, updated_wallet: Wallet) -> None:
        if updated_wallet.name is not None:
            wallet.name = updated_wallet.name

    @staticmethod
    async def __update_balances(wallet: Wallet, updated_wallet: Wallet) -> None:
        if updated_wallet.balances_ids is not None:
            updated_balances: List[Balance] = updated_wallet.balances_ids
            for updated_balance in updated_balances:
                match_found = False
                balances: List[Balance] = wallet.balances_ids
                for existing_balance in balances:
                    if (
                        existing_balance.currency_id.pk
                        == updated_balance.currency_id.pk
                    ):
                        new_amount = updated_balance.amount
                        await BalanceCRUD.update_one(
                            existing_balance, {"amount": new_amount}
                        )
                        match_found = True
                if not match_found:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Currency ids provided are not related to this user",
                    )

    @staticmethod
    def __update_timestamp(wallet: Wallet) -> None:
        wallet.updated_at = datetime.utcnow()

    @classmethod
    async def delete_one_by_user(cls, user_id: str, wallet_id: str) -> bool:
        result = Wallet.objects(id=wallet_id, user_id=user_id).delete()
        if result == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wallet with id {wallet_id} for user {user_id} does not exist",
            )
        return result > 0

    @classmethod
    async def get_balance(
        cls, user_id: str, wallet_id: str, currency_id: str
    ) -> Balance:
        wallet = await cls.get_one_by_user(wallet_id, user_id)
        balances: List[Balance] = wallet.balances_ids
        for balance in balances:
            if str(balance.currency_id.id) == currency_id:
                return balance

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Balance not found in the wallet.",
        )
