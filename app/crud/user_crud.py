from typing import Optional

from models.models import User


class UserCRUD:

    @classmethod
    async def create_one(cls, user: User) -> User:
        user.save()
        return user

    @classmethod
    async def get_one_by_username(cls, username: str) -> User:
        return User.objects.get(username=username)

    @classmethod
    async def get_one_by_username_optional(cls, username: str) -> Optional[User]:
        return User.objects(username=username).first()

    @classmethod
    async def update_one(cls, username: str, updated_user: User) -> int:
        user = await cls.get_one_by_username(username=username)
        user.update(**updated_user)
        return user.save()

    @classmethod
    async def delete_one(cls, username: str) -> int:
        user = await cls.get_one_by_username(username=username)
        return user.delete()
