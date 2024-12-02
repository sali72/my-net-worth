from typing import Optional

from mongoengine import DoesNotExist

from models.models import Balance


class BalanceCRUD:

    @classmethod
    async def create_one(cls, balance: Balance) -> Balance:
        balance.clean()
        balance.save()
        return balance

    @classmethod
    async def update_one(cls, balance: Balance, update_data: dict) -> Balance:
        balance.clean()
        if not update_data:
            raise ValueError("No update parameters provided")

        Balance.objects(id=balance.id).update(**update_data)
        return Balance.objects.get(id=balance.id)

    @classmethod
    async def get_one_by_wallet_and_currency_id_optional(
        cls, wallet_id: str, currency_id: str
    ) -> Optional[Balance]:
        return Balance.objects(wallet_id=wallet_id, currency_id=currency_id).first()

    @classmethod
    async def delete_one_by_wallet_and_currency_id(
        cls, wallet_id: str, currency_id: str
    ) -> bool:
        result = Balance.objects(wallet_id=wallet_id, currency_id=currency_id).delete()
        if result == 0:
            raise DoesNotExist(
                f"Balance with wallet_id of {wallet_id} and currency_id of {currency_id} does not exist"
            )
        return result > 0
