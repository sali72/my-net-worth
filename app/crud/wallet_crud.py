from datetime import datetime
from fastapi import HTTPException, status
from mongoengine import DoesNotExist, QuerySet

from models.models import Wallet, CurrencyBalance


class WalletCRUD:

    @classmethod
    async def create_one(cls, user: Wallet) -> Wallet:
        user.save()
        return user

    @classmethod
    async def get_one_by_user_optional(cls, wallet_id: str, user_id: str) -> Wallet:
        return Wallet.objects(id=wallet_id, user_id=user_id).first()

    @classmethod
    async def get_one_by_user(cls, wallet_id: str, user_id: str) -> Wallet:
        return Wallet.objects.get(id=wallet_id, user_id=user_id)

    @classmethod
    async def get_all_by_user_id_optional(cls, user_id: str) -> QuerySet:
        wallets = Wallet.objects(user_id=user_id)
        return wallets

    @classmethod
    async def get_one_by_id(cls, wallet_id: str) -> Wallet:
        return Wallet.objects.get(id=wallet_id)

    @classmethod
    async def update_one_by_user(
        cls, user_id: str, wallet_id: str, updated_wallet: Wallet
    ):
        wallet = await cls.get_one_by_user(wallet_id, user_id)
        cls.__update_wallet_fields(wallet, updated_wallet)
        cls.__update_currency_balances(wallet, updated_wallet)
        cls.__update_timestamp(wallet)
        wallet.save()

    @staticmethod
    def __update_wallet_fields(wallet: Wallet, updated_wallet: Wallet):
        if updated_wallet.name is not None:
            wallet.name = updated_wallet.name
        if updated_wallet.type is not None:
            wallet.type = updated_wallet.type

    @staticmethod
    def __update_currency_balances(wallet: Wallet, updated_wallet: Wallet):
        # it does not add or remove a currency balance
        if updated_wallet.currency_balances is not None:
            for updated_balance in updated_wallet.currency_balances:
                match_found = False
                for existing_balance in wallet.currency_balances:
                    if (
                        existing_balance.currency_id.pk
                        == updated_balance.currency_id.pk
                    ):
                        existing_balance.balance = updated_balance.balance
                        match_found = True
                if not match_found:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Currency ids provided are not related to this user",
                    )

    @staticmethod
    def __update_timestamp(wallet: Wallet):
        wallet.updated_at = datetime.utcnow()

    @classmethod
    async def delete_one_by_user(cls, user_id: str, wallet_id: str) -> bool:
        result = Wallet.objects(id=wallet_id, user_id=user_id).delete()
        if result == 0:
            raise DoesNotExist(
                f"Wallet with id {wallet_id} for user {user_id} does not exist"
            )
        return result > 0

    @classmethod
    async def add_currency_balance_to_wallet(
        cls, user_id: str, wallet_id: str, currency_balance: CurrencyBalance
    ) -> Wallet:
        wallet = await cls.get_one_by_user(wallet_id, user_id)
        wallet.currency_balances.append(currency_balance)
        wallet.save()
        return wallet
    
    @classmethod
    async def remove_currency_balance_from_wallet(
        cls, user_id: str, wallet_id: str, currency_id: str
    ) -> Wallet:
        wallet = await cls.get_one_by_user(wallet_id, user_id)
        
        for existing_balance in wallet.currency_balances:
            if str(existing_balance.currency_id.pk) == currency_id:
                wallet.currency_balances.remove(existing_balance)
                wallet.save()
                return wallet

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Currency balance not found in the wallet",
        )
