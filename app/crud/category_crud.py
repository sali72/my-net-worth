from mongoengine import DoesNotExist, QuerySet

from models.models import Category


class CategoryCRUD:

    @classmethod
    async def create_one(cls, category: Category) -> Category:
        category.save()
        return category

    @classmethod
    async def get_one_by_user(cls, category_id: str, user_id: str) -> Category:
        return Category.objects.get(id=category_id, user_id=user_id)

    @classmethod
    async def get_all_by_user_id(cls, user_id: str) -> QuerySet:
        return Category.objects(user_id=user_id)

    @classmethod
    async def update_one_by_user(
        cls, user_id: str, category_id: str, updated_category: Category
    ):
        category = await cls.get_one_by_user(category_id, user_id)
        cls.__update_category_fields(category, updated_category)
        category.save()

    @staticmethod
    def __update_category_fields(category: Category, updated_category: Category):
        if updated_category.name is not None:
            category.name = updated_category.name
        if updated_category.is_predefined is not None:
            category.is_predefined = updated_category.is_predefined

    @classmethod
    async def delete_one_by_user(cls, user_id: str, category_id: str) -> bool:
        result = Category.objects(id=category_id, user_id=user_id).delete()
        if result == 0:
            raise DoesNotExist(
                f"Category with id {category_id} for user {user_id} does not exist"
            )
        return result > 0