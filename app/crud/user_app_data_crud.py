from models.models import UserAppData


class UserAppDataCRUD:
    @classmethod
    async def create_one(cls, user_data: UserAppData) -> UserAppData:
        user_data.save()
        return user_data

    @classmethod
    async def delete_one(cls, user_data: UserAppData) -> int:
        return user_data.delete()
