from datetime import datetime
from decimal import Decimal
from bson import ObjectId

from models.models import UserAppData


class UserAppDataCRUD:
    @classmethod
    async def create_one(cls, user_data: UserAppData) -> UserAppData:
        user_data.save()
        return user_data

    @classmethod
    async def get_one_by_id(cls, _id: str) -> UserAppData:
        return UserAppData.objects.get(pk=ObjectId(_id))

    @classmethod
    async def get_one_by_user_id(cls, user_id: str) -> UserAppData:
        return UserAppData.objects.get(user_id=user_id)

    @classmethod
    async def get_base_currency_id_by_user_id(cls, user_id: str) -> str:
        user_app_data = await cls.get_one_by_user_id(user_id)
        return user_app_data.base_currency_id.pk

    @classmethod
    async def delete_one(cls, user_data: UserAppData) -> int:
        return user_data.delete()

    @classmethod
    async def set_base_currency_by_user_app_data_id(
        cls, user_app_data_id: str, currency_id: str
    ) -> UserAppData:
        user_app_data = await cls.get_one_by_id(user_app_data_id)
        return await cls.set_base_currency(user_app_data, currency_id)

    @classmethod
    async def set_base_currency(
        cls, user_app_data: UserAppData, currency_id: str
    ) -> UserAppData:
        user_app_data.base_currency_id = ObjectId(currency_id)
        user_app_data.save()
        return user_app_data

    @classmethod
    async def update_one_by_id(
        cls, current_user_app_data_id: str, updated_user_app_data: UserAppData
    ) -> UserAppData:
        user_app_data = await cls.get_one_by_id(current_user_app_data_id)
        return cls.update_one(updated_user_app_data, user_app_data)

    @classmethod
    def update_one(
        cls, current_user_app_data: UserAppData, updated_user_app_data: UserAppData
    ):
        cls.__update_user_app_data_fields(current_user_app_data, updated_user_app_data)
        cls.__update_timestamp(current_user_app_data)
        current_user_app_data.save()
        return current_user_app_data

    @staticmethod
    def __update_user_app_data_fields(
        user_app_data: UserAppData, updated_user_app_data: UserAppData
    ):
        if updated_user_app_data.base_currency_id is not None:
            user_app_data.base_currency_id = updated_user_app_data.base_currency_id
        if updated_user_app_data.net_worth is not None:
            user_app_data.net_worth = updated_user_app_data.net_worth
        if updated_user_app_data.assets_value is not None:
            user_app_data.assets_value = updated_user_app_data.assets_value
        if updated_user_app_data.wallets_value is not None:
            user_app_data.wallets_value = updated_user_app_data.wallets_value

    @staticmethod
    def __update_timestamp(user_app_data: UserAppData):
        user_app_data.updated_at = datetime.utcnow()

    @classmethod
    async def update_user_app_data_wallets_value(
        cls, user_id: str, total_value: Decimal
    ):
        user_app_data = await UserAppDataCRUD.get_one_by_user_id(user_id)
        user_app_data.wallets_value = total_value
        user_app_data.net_worth = user_app_data.assets_value + total_value
        user_app_data.clean()
        user_app_data.save()

    @classmethod
    async def add_amount_to_user_app_data_wallets_value(
        cls, user_id: str, amount: Decimal
    ):
        user_app_data = await cls.get_one_by_user_id(user_id)
        user_app_data.wallets_value += amount
        user_app_data.net_worth += amount
        user_app_data.clean()
        user_app_data.save()

    @classmethod
    async def reduce_amount_from_user_app_data_wallets_value(
        cls, user_id: str, amount: Decimal
    ):
        user_app_data = await cls.get_one_by_user_id(user_id)
        user_app_data.wallets_value -= amount
        user_app_data.net_worth -= amount
        user_app_data.clean()
        user_app_data.save()

    @classmethod
    async def add_amount_to_user_app_data_assets_value(
        cls, user_id: str, amount: Decimal
    ):
        user_app_data = await cls.get_one_by_user_id(user_id)
        user_app_data.assets_value += amount
        user_app_data.net_worth += amount
        user_app_data.clean()
        user_app_data.save()

    @classmethod
    async def reduce_amount_from_user_app_data_assets_value(
        cls, user_id: str, amount: Decimal
    ):
        user_app_data = await cls.get_one_by_user_id(user_id)
        user_app_data.assets_value -= amount
        user_app_data.net_worth -= amount
        user_app_data.clean()
        user_app_data.save()
