from typing import List
from app.crud.asset_type_crud import AssetTypeCRUD
from models.models import AssetType, User
from models.schemas import AssetTypeCreateSchema, AssetTypeUpdateSchema


class AssetTypeController:

    @classmethod
    async def create_asset_type(
        cls, asset_type_schema: AssetTypeCreateSchema, user: User
    ) -> dict:
        asset_type = cls._create_asset_type_obj_to_create(asset_type_schema, user.id)
        asset_type_in_db: AssetType = await AssetTypeCRUD.create_one(asset_type)
        return asset_type_in_db.to_dict()

    @classmethod
    def _create_asset_type_obj_to_create(
        cls, asset_type_schema: AssetTypeCreateSchema, user_id: str
    ) -> AssetType:
        return AssetType(
            user_id=user_id,
            name=asset_type_schema.name,
            description=asset_type_schema.description,
        )

    @classmethod
    async def get_asset_type(cls, asset_type_id: str, user_id: str) -> dict:
        asset_type = await AssetTypeCRUD.get_one_by_user(asset_type_id, user_id)
        return asset_type.to_dict()

    @classmethod
    async def get_all_asset_types(cls, user_id: str) -> List[dict]:
        asset_types: List[AssetType] = await AssetTypeCRUD.get_all_by_user_id(user_id)
        return [asset_type.to_dict() for asset_type in asset_types]

    @classmethod
    async def update_asset_type(
        cls,
        asset_type_id: str,
        asset_type_update_schema: AssetTypeUpdateSchema,
        user_id: str,
    ) -> dict:
        updated_asset_type = cls._create_asset_type_obj_for_update(
            asset_type_update_schema
        )

        await AssetTypeCRUD.update_one_by_user(
            user_id, asset_type_id, updated_asset_type
        )

        asset_type_from_db = await AssetTypeCRUD.get_one_by_user(asset_type_id, user_id)
        return asset_type_from_db.to_dict()

    @classmethod
    def _create_asset_type_obj_for_update(
        cls, asset_type_schema: AssetTypeUpdateSchema
    ) -> AssetType:
        return AssetType(
            name=asset_type_schema.name,
            description=asset_type_schema.description,
        )

    @classmethod
    async def delete_asset_type(cls, asset_type_id: str, user_id: str) -> bool:
        await AssetTypeCRUD.get_one_by_user(asset_type_id, user_id)
        await AssetTypeCRUD.delete_one_by_user(asset_type_id, user_id)
        return True
