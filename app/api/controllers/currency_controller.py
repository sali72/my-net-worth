from typing import List

from mongoengine import DoesNotExist, ValidationError

from app.api.controllers.asset_controller import AssetController
from app.crud.currency_crud import CurrencyCRUD
from app.crud.currency_exchange_crud import CurrencyExchangeCRUD
from app.crud.wallet_crud import WalletCRUD
from models.models import Currency, User
from models.schemas import CurrencyCreateSchema, CurrencyUpdateSchema


class CurrencyController:

    @classmethod
    async def create_currency(
        cls, currency_schema: CurrencyCreateSchema, user: User
    ) -> dict:
        currency = cls._create_currency_obj_to_create(currency_schema, user.id)
        currency_in_db: Currency = await CurrencyCRUD.create_one(currency)
        return currency_in_db.to_dict()

    @classmethod
    def _create_currency_obj_to_create(
        cls, currency_schema: CurrencyCreateSchema, user_id: str
    ) -> Currency:
        return Currency(
            user_id=user_id,
            code=currency_schema.code,
            name=currency_schema.name,
            symbol=currency_schema.symbol,
            currency_type=currency_schema.currency_type,
        )

    @classmethod
    async def get_currency(cls, currency_id: str, user_id: str) -> dict:
        currency = await CurrencyCRUD.get_one_by_user(currency_id, user_id)
        return currency.to_dict()

    @classmethod
    async def get_all_currencies(cls, user_id: str) -> List[dict]:
        currencies: List[Currency] = await CurrencyCRUD.get_all_by_user_id(user_id)
        return [currency.to_dict() for currency in currencies]

    @classmethod
    async def update_currency(
        cls,
        currency_id: str,
        currency_update_schema: CurrencyUpdateSchema,
        user_id: str,
    ) -> dict:
        await cls._validate_currency_for_update(currency_id, user_id)

        updated_currency = cls._create_currency_obj_for_update(currency_update_schema)

        await CurrencyCRUD.update_one_by_user(user_id, currency_id, updated_currency)

        currency_from_db = await CurrencyCRUD.get_one_by_user(currency_id, user_id)
        return currency_from_db.to_dict()

    @classmethod
    async def _validate_currency_for_update(cls, currency_id, user_id):
        existing_currency: Currency = await CurrencyCRUD.get_one_by_user(
            currency_id, user_id
        )
        if existing_currency.is_predefined:
            raise ValidationError("Predefined currencies cannot be modified.")

    @classmethod
    def _create_currency_obj_for_update(
        cls, currency_schema: CurrencyUpdateSchema
    ) -> Currency:
        return Currency(
            code=currency_schema.code,
            name=currency_schema.name,
            symbol=currency_schema.symbol,
            currency_type=currency_schema.currency_type,
        )

    @classmethod
    async def delete_currency(cls, currency_id: str, user_id: str) -> bool:
        await CurrencyCRUD.delete_one_by_user(currency_id, user_id)
        return True

    @classmethod
    async def set_base_currency_by_id(cls, user_id: str, currency_id: str) -> dict:
        current_base_currency = await cls._get_current_base_currency(user_id)
        currency_to_set = await cls._retrieve_currency_to_set(user_id, currency_id)

        # # Check for necessary exchange rates
        # await cls._validate_exchange_rates(
        #     user_id, current_base_currency, currency_to_set
        # )

        # Unset the current base currency
        if current_base_currency:
            await CurrencyCRUD.unset_base_currency(current_base_currency)

        # Set the new base currency
        updated_currency = await cls._set_new_base_currency(currency_to_set)

        # # Update asset values if the user wants to
        # await AssetController.update_asset_values(
        #     user_id, current_base_currency, currency_to_set
        # )

        return updated_currency.to_dict()

    @classmethod
    async def _get_current_base_currency(cls, user_id: str) -> Currency:
        try:
            return await CurrencyCRUD.get_base_currency(user_id)
        except DoesNotExist:
            return None

    @classmethod
    async def _retrieve_currency_to_set(
        cls, user_id: str, currency_id: str
    ) -> Currency:
        return await CurrencyCRUD.get_one_by_user(currency_id, user_id)

    # @classmethod
    # async def _validate_exchange_rates(
    #     cls, user_id: str, current_base_currency: Currency, new_base_currency: Currency
    # ) -> None:
    #     # Get all wallets for the user
    #     wallets = await WalletCRUD.get_all_by_user_id_optional(user_id)
    #     held_currency_ids = {
    #         balance.currency_id.id
    #         for wallet in wallets
    #         for balance in wallet.currency_balances
    #     }

    #     # Check for exchange rates between held currencies and the new base currency
    #     for currency_id in held_currency_ids:
    #         if currency_id == new_base_currency.id:
    #             continue
    #         if not await CurrencyExchangeCRUD.exchange_rate_exists(
    #             user_id, currency_id, new_base_currency.id
    #         ):
    #             raise ValidationError(
    #                 f"Missing exchange rate for currency {currency_id} to new base currency {new_base_currency.id}"
    #             )

    #     # Check for exchange rates between the current and new base currencies
    #     if (
    #         current_base_currency
    #         and not await CurrencyExchangeCRUD.exchange_rate_exists(
    #             user_id, current_base_currency.id, new_base_currency.id
    #         )
    #     ):
    #         raise ValidationError(
    #             f"Missing exchange rate between current base currency {current_base_currency.id} and new base currency {new_base_currency.id}"
    #         )

    @classmethod
    async def _set_new_base_currency(cls, currency: Currency) -> Currency:
        return await CurrencyCRUD.set_base_currency(currency)
