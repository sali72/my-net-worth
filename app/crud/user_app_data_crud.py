from models.models import UserAppData
from bson import ObjectId
from pymongo.errors import DoesNotExist


class UserAppDataCRUD:
    @classmethod
    async def create_one(cls, user_data: UserAppData) -> UserAppData:
        user_data.save()
        return user_data

    @classmethod
    async def get_one_by_id(cls, _id: str) -> UserAppData:
        return UserAppData.objects.get(pk=ObjectId(_id))

    @classmethod
    async def get_base_currency_id(cls, _id: str) -> str:
        user_app_data = await cls.get_one_by_id(_id)
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
