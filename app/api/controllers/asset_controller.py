from decimal import Decimal
from typing import List

from app.crud.asset_crud import AssetCRUD
from app.crud.asset_type_crud import AssetTypeCRUD
from app.crud.currency_crud import CurrencyCRUD
from app.crud.currency_exchange_crud import CurrencyExchangeCRUD
from app.crud.user_app_data_crud import UserAppDataCRUD
from models.models import Asset, Currency, User
from models.schemas import AssetCreateSchema, AssetFilterSchema, AssetUpdateSchema


class AssetController:

    @classmethod
    async def create_asset(cls, asset_schema: AssetCreateSchema, user: User) -> Asset:
        await cls._validate_asset_data(asset_schema, user.id)
        asset = cls._create_asset_obj_to_create(asset_schema, user.id)
        asset_in_db = await AssetCRUD.create_one(asset)
        return asset_in_db

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
    async def delete_asset(cls, asset_id: str, user_id: str) -> Asset:
        asset_to_delete = await AssetCRUD.get_one_by_user(asset_id, user_id)
        await AssetCRUD.delete_one_by_user(asset_id, user_id)
        return asset_to_delete

    @classmethod
    async def calculate_total_asset_value(cls, user: User) -> Decimal:
        all_user_assets = await AssetCRUD.get_all_by_user_id(user.id)
        base_currency = await cls._get_base_currency(user.id)
        total_value = Decimal(0)
        for asset in all_user_assets:
            total_value += await cls._calculate_asset_value(
                asset, base_currency, user.id
            )
        await cls._update_user_app_data_assets_value(user.id, total_value)
        return total_value

    @classmethod
    async def filter_assets(
        cls, filters: AssetFilterSchema, user_id: str
    ) -> List[dict]:
        assets = await AssetCRUD.get_filtered_assets(filters, user_id)
        return [asset.to_dict() for asset in assets]

    @classmethod
    async def calculate_asset_value_difference_in_update(
        cls, user_id: str, asset_id: str, asset_schema: AssetUpdateSchema
    ) -> Decimal:
        asset = await AssetCRUD.get_one_by_user(asset_id, user_id)
        difference = asset_schema.value - asset.value
        return difference

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
            currency_id=asset_schema.currency_id,
            name=asset_schema.name,
            description=asset_schema.description,
            value=asset_schema.value,
        )

    @classmethod
    def _create_asset_obj_for_update(cls, asset_schema: AssetUpdateSchema) -> Asset:
        return Asset(
            asset_type_id=asset_schema.asset_type_id,
            currency_id=asset_schema.currency_id,
            name=asset_schema.name,
            description=asset_schema.description,
            value=(asset_schema.value if asset_schema.value is not None else None),
        )

    @classmethod
    async def _update_user_app_data_assets_value(cls, user_id: str, total_value: Decimal) -> None:
        user_app_data = await UserAppDataCRUD.get_one_by_user_id(user_id)
        user_app_data.assets_value = total_value
        await UserAppDataCRUD.update_one_by_id(user_app_data.id, user_app_data)

    @classmethod
    async def _get_base_currency(cls, user_id: str) -> Currency:
        user_app_data = await UserAppDataCRUD.get_one_by_user_id(user_id)
        base_currency_id = user_app_data.base_currency_id.pk
        base_currency = await CurrencyCRUD.get_one_by_user(base_currency_id, user_id)
        return base_currency

    @classmethod
    async def _calculate_asset_value(
        cls, asset: Asset, base_currency: Currency, user_id: str
    ) -> Decimal:
        if asset.currency_id.id == base_currency.id:
            return asset.value
        else:
            return await CurrencyExchangeCRUD.convert_value_to_base_currency(
                asset.value,
                asset.currency_id,
                base_currency.id,
                user_id,
            )