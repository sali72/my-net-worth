from fastapi import HTTPException

from models.models import User

class UserCRUD:

    def __init__(self) -> None:
        pass

    async def create_one(self, user: User) -> User:
        user.save()
        return user

    async def get_all(self):
        return list(User.objects)

    async def get_one_by_username(self, username: str) -> User:
        return User.objects(username=username).first()

    async def get_one_by_username_optional(self, username: str) -> User:
        return User.objects(username=username).first()

    async def get_one_by_id(self, user_id: str) -> User:
        return User.objects(user_id=user_id).first()

    async def update_one(self, user_id: str, user: User) -> int:
        user = User.objects(user_id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.update(user)
        return user.save()

    async def delete_one(self, user_id: str) -> int:
        user = User.objects(user_id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user.delete()
