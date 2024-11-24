from datetime import datetime
from typing import List

from mongoengine import DoesNotExist, Q, QuerySet

from models.models import Asset
from models.schemas import AssetFilterSchema


class AssetCRUD:

    @classmethod
    async def create_one(cls, asset: Asset) -> Asset:
        asset.clean()
        asset.save()
        return asset

    @classmethod
    async def get_one_by_user(cls, asset_id: str, user_id: str) -> Asset:
        return Asset.objects.get(id=asset_id, user_id=user_id)

    @classmethod
    async def get_all_by_user_id(cls, user_id: str) -> QuerySet:
        assets = Asset.objects(user_id=user_id)
        return assets

    @classmethod
    async def update_one_by_user(
        cls, user_id: str, asset_id: str, updated_asset: Asset
    ):
        asset = await cls.get_one_by_user(asset_id, user_id)
        cls._update_asset_fields(asset, updated_asset)
        cls._update_timestamp(asset)
        asset.clean()
        asset.save()

    @staticmethod
    def _update_asset_fields(asset: Asset, updated_asset: Asset):
        if updated_asset.asset_type_id is not None:
            asset.asset_type_id = updated_asset.asset_type_id
        if updated_asset.currency_id is not None:
            asset.currency_id = updated_asset.currency_id
        if updated_asset.name is not None:
            asset.name = updated_asset.name
        if updated_asset.description is not None:
            asset.description = updated_asset.description
        if updated_asset.value is not None:
            asset.value = updated_asset.value

    @staticmethod
    def _update_timestamp(asset: Asset):
        asset.updated_at = datetime.utcnow()

    @classmethod
    async def delete_one_by_user(cls, asset_id: str, user_id: str) -> bool:
        result = Asset.objects(id=asset_id, user_id=user_id).delete()
        if result == 0:
            raise DoesNotExist(
                f"Asset with id {asset_id} for user {user_id} does not exist"
            )
        return result > 0

    @classmethod
    async def update_asset_value_with_exchange_rate(
        cls, asset: Asset, exchange_rate: float
    ) -> None:
        asset.value *= exchange_rate
        asset.save()

    @classmethod
    async def get_filtered_assets(
        cls, filters: AssetFilterSchema, user_id: str
    ) -> List[Asset]:
        query = Q(user_id=user_id)

        if filters.name:
            query &= Q(name__icontains=filters.name)
        if filters.asset_type_id:
            query &= Q(asset_type_id=filters.asset_type_id)
        if filters.currency_id:
            query &= Q(currency_id=filters.currency_id)
        if filters.created_at_start:
            query &= Q(created_at__gte=filters.created_at_start)
        if filters.created_at_end:
            query &= Q(created_at__lte=filters.created_at_end)
        if filters.updated_at_start:
            query &= Q(updated_at__gte=filters.updated_at_start)
        if filters.updated_at_end:
            query &= Q(updated_at__lte=filters.updated_at_end)

        return Asset.objects(query)