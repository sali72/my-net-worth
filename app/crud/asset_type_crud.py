from datetime import datetime, timezone
from typing import Optional

from mongoengine import DoesNotExist, Q, QuerySet

from models.models import AssetType


class AssetTypeCRUD:

    @classmethod
    async def create_one(cls, asset_type: AssetType) -> AssetType:
        asset_type.clean()
        asset_type.save()
        return asset_type

    @classmethod
    async def get_one_by_user(cls, asset_type_id: str, user_id: str) -> AssetType:
        return AssetType.objects.get(
            (Q(id=asset_type_id) & Q(user_id=user_id))
            | Q(id=asset_type_id, is_predefined=True)
        )

    @staticmethod
    async def get_one_by_user_and_name_optional(
        name: str, user_id: str
    ) -> Optional[AssetType]:
        return AssetType.objects(
            (Q(name=name) & Q(user_id=user_id)) | Q(name=name, is_predefined=True)
        ).first()

    @classmethod
    async def get_all_by_user_id(cls, user_id: str) -> QuerySet:
        return AssetType.objects(Q(is_predefined=True) | Q(user_id=user_id))

    @classmethod
    async def update_one_by_user(
        cls, user_id: str, asset_type_id: str, updated_asset_type: AssetType
    ) -> None:
        asset_type = await cls.get_one_by_user(asset_type_id, user_id)
        cls._update_asset_type_fields(asset_type, updated_asset_type)
        cls._update_timestamp(asset_type)
        asset_type.clean()
        asset_type.save()

    @classmethod
    async def delete_one_by_user(cls, asset_type_id: str, user_id: str) -> bool:
        result = AssetType.objects(id=asset_type_id, user_id=user_id).delete()
        if result == 0:
            raise DoesNotExist(
                f"AssetType with id {asset_type_id} for user {user_id} does not exist"
            )
        return result > 0

    @staticmethod
    def _update_asset_type_fields(
        asset_type: AssetType, updated_asset_type: AssetType
    ) -> None:
        if updated_asset_type.name is not None:
            asset_type.name = updated_asset_type.name
        if updated_asset_type.description is not None:
            asset_type.description = updated_asset_type.description
        if updated_asset_type.is_predefined is not None:
            asset_type.is_predefined = updated_asset_type.is_predefined

    @staticmethod
    def _update_timestamp(asset_type: AssetType) -> None:
        asset_type.updated_at = datetime.now(timezone.utc)
