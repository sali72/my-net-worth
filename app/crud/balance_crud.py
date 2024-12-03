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
        if not update_data:
            raise ValueError("No update parameters provided")

        existing_balance: Balance = Balance.objects.get(id=balance.id)

        # Update the fields of the existing balance
        for key, value in update_data.items():
            setattr(existing_balance, key, value)

        existing_balance.save()

        # Return the updated balance
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
