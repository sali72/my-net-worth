from typing import List
from app.crud.category_crud import CategoryCRUD
from models.models import Category
from models.schemas import CategoryCreateSchema, CategoryUpdateSchema


class CategoryController:

    @classmethod
    async def create_category(
        cls, category_schema: CategoryCreateSchema, user_id: str
    ) -> dict:
        category = cls._create_category_obj_to_create(category_schema, user_id)
        category_in_db: Category = await CategoryCRUD.create_one(category)
        return category_in_db.to_dict()

    @classmethod
    async def get_category(cls, category_id: str, user_id: str) -> dict:
        category = await CategoryCRUD.get_one_by_user(category_id, user_id)
        return category.to_dict()

    @classmethod
    async def get_all_categories(cls, user_id: str) -> List[dict]:
        categories: List[Category] = await CategoryCRUD.get_all_by_user_id(user_id)
        return [category.to_dict() for category in categories]

    @classmethod
    async def update_category(
        cls,
        category_id: str,
        category_update_schema: CategoryUpdateSchema,
        user_id: str,
    ) -> dict:
        updated_category = cls._create_category_obj_for_update(category_update_schema)

        await CategoryCRUD.update_one_by_user(user_id, category_id, updated_category)

        category_from_db = await CategoryCRUD.get_one_by_user(category_id, user_id)
        return category_from_db.to_dict()

    @classmethod
    async def delete_category(cls, category_id: str, user_id: str) -> bool:
        await CategoryCRUD.delete_one_by_user(category_id, user_id)
        return True

    @classmethod
    def _create_category_obj_to_create(
        cls, category_schema: CategoryCreateSchema, user_id: str
    ) -> Category:
        return Category(
            user_id=user_id,
            name=category_schema.name,
            type=category_schema.type,
            description=category_schema.description,
        )

    @classmethod
    def _create_category_obj_for_update(
        cls, category_schema: CategoryUpdateSchema
    ) -> Category:
        return Category(
            name=category_schema.name,
            type=category_schema.type,
            description=category_schema.description,
        )
