from typing import List
from app.crud.asset_crud import AssetCRUD
from app.crud.asset_type_crud import AssetTypeCRUD
from models.models import Asset, User
from models.schemas import AssetCreateSchema, AssetUpdateSchema


class AssetController:

    @classmethod
    async def create_asset(cls, asset_schema: AssetCreateSchema, user: User) -> dict:
        await cls._validate_asset_data(asset_schema, user.id)
        asset = cls._create_asset_obj_to_create(asset_schema, user.id)

        asset_in_db: Asset = await AssetCRUD.create_one(asset)
        return asset_in_db.to_dict()

    @classmethod
    async def _validate_asset_data(
        cls, asset_schema: AssetCreateSchema, user_id: str
    ) -> None:
        if asset_schema.asset_type_id:
            await AssetTypeCRUD.get_one_by_user(asset_schema.asset_type_id, user_id)

    @classmethod
    def _create_asset_obj_to_create(
        cls, asset_schema: AssetCreateSchema, user_id: str
    ) -> Asset:
        return Asset(
            user_id=user_id,
            asset_type_id=asset_schema.asset_type_id,
            name=asset_schema.name,
            description=asset_schema.description,
            value=asset_schema.value,
        )

    @classmethod
    async def get_asset(cls, asset_id: str, user_id: str) -> dict:
        asset = await AssetCRUD.get_one_by_user(asset_id, user_id)
        return asset.to_dict()

    @classmethod
    async def get_all_assets(cls, user_id: str) -> List[dict]:
        assets: List[Asset] = await AssetCRUD.get_all_by_user_id(user_id)
        return [asset.to_dict() for asset in assets]

    @classmethod
    async def update_asset(
        cls, asset_id: str, asset_update_schema: AssetUpdateSchema, user_id: str
    ) -> dict:
        updated_asset = cls._create_asset_obj_for_update(asset_update_schema)

        await AssetCRUD.update_one_by_user(user_id, asset_id, updated_asset)

        asset_from_db = await AssetCRUD.get_one_by_user(asset_id, user_id)
        return asset_from_db.to_dict()

    @classmethod
    def _create_asset_obj_for_update(cls, asset_schema: AssetUpdateSchema) -> Asset:
        return Asset(
            asset_type_id=asset_schema.asset_type_id,
            name=asset_schema.name,
            description=asset_schema.description,
            value=asset_schema.value,
        )

    @classmethod
    async def delete_asset(cls, asset_id: str, user_id: str) -> bool:
        asset = await AssetCRUD.get_one_by_user(asset_id, user_id)
        await AssetCRUD.delete_one_by_user(asset_id, user_id)
        return True

    @classmethod
    async def calculate_total_asset_value(cls, user_id: str) -> float:
        assets: List[Asset] = await AssetCRUD.get_all_by_user_id(user_id)
        total_value = sum(asset.value for asset in assets)
        return total_value
