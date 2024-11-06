from mongoengine import DoesNotExist, QuerySet
from models.models import Wallet


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
        try:
            return Wallet.objects.get(id=wallet_id, user_id=user_id)
        except DoesNotExist:
            raise DoesNotExist(
                f"Wallet with id {wallet_id} for user {user_id} does not exist"
            )

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
        result = Wallet.objects(id=wallet_id, user_id=user_id).update_one(
            set__name=updated_wallet.name,
            set__type=updated_wallet.type,
            set__currency_ids=updated_wallet.currency_ids,
        )
        if result == 0:
            raise DoesNotExist(
                f"Wallet with id {wallet_id} for user {user_id} does not exist or update failed"
            )

    @classmethod
    async def delete_one_by_user(cls, user_id: str, wallet_id: str) -> bool:
        result = Wallet.objects(id=wallet_id, user_id=user_id).delete()
        if result == 0:
            raise DoesNotExist(
                f"Wallet with id {wallet_id} for user {user_id} does not exist"
            )
        return result > 0
