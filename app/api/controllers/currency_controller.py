from typing import List

from mongoengine import ValidationError

from app.crud.currency_crud import CurrencyCRUD
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
