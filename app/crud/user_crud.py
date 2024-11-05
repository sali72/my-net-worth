from models.models import User


class UserCRUD:

    async def create_one(self, user: User) -> User:
        user.save()
        return user

    async def get_all(self):
        return list(User.objects)

    async def get_one_by_username(self, username: str) -> User:
        return User.objects.get(username=username)

    async def get_one_by_username_optional(self, username: str) -> User:
        return User.objects(username=username).first()

    async def get_one_by_id(self, user_id: str) -> User:
        return User.objects.get(user_id=user_id)

    async def update_one(self, username: str, updated_user: User) -> int:
        user = await self.get_one_by_username(username=username)
        user.update(updated_user)
        return user.save()

    async def delete_one(self, username: str) -> int:
        user = await self.get_one_by_username(username=username)
        return user.delete()
