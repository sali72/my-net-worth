from typing import List
from app.crud.currency_exchange_crud import CurrencyExchangeCRUD
from models.models import CurrencyExchange, User
from models.schemas import CurrencyExchangeCreateSchema, CurrencyExchangeUpdateSchema


class CurrencyExchangeController:

    @classmethod
    async def create_currency_exchange(
        cls, exchange_schema: CurrencyExchangeCreateSchema, user: User
    ) -> dict:
        exchange = cls._create_exchange_obj_to_create(exchange_schema, user.id)
        exchange_in_db: CurrencyExchange = await CurrencyExchangeCRUD.create_one(
            exchange
        )
        return exchange_in_db.to_dict()

    @classmethod
    def _create_exchange_obj_to_create(
        cls, exchange_schema: CurrencyExchangeCreateSchema, user_id: str
    ) -> CurrencyExchange:
        return CurrencyExchange(
            user_id=user_id,
            from_currency_id=exchange_schema.from_currency_id,
            to_currency_id=exchange_schema.to_currency_id,
            rate=exchange_schema.rate,
            date=exchange_schema.date,
        )

    @classmethod
    async def get_currency_exchange(cls, exchange_id: str, user_id: str) -> dict:
        exchange = await CurrencyExchangeCRUD.get_one_by_user(exchange_id, user_id)
        return exchange.to_dict()

    @classmethod
    async def get_all_currency_exchanges(cls, user_id: str) -> List[dict]:
        exchanges: List[CurrencyExchange] = (
            await CurrencyExchangeCRUD.get_all_by_user_id(user_id)
        )
        return [exchange.to_dict() for exchange in exchanges]

    @classmethod
    async def update_currency_exchange(
        cls,
        exchange_id: str,
        exchange_update_schema: CurrencyExchangeUpdateSchema,
        user_id: str,
    ) -> dict:
        updated_exchange = cls._create_exchange_obj_for_update(exchange_update_schema)

        await CurrencyExchangeCRUD.update_one_by_user(
            user_id, exchange_id, updated_exchange
        )

        exchange_from_db = await CurrencyExchangeCRUD.get_one_by_user(
            exchange_id, user_id
        )
        return exchange_from_db.to_dict()

    @classmethod
    def _create_exchange_obj_for_update(
        cls, exchange_schema: CurrencyExchangeUpdateSchema
    ) -> CurrencyExchange:
        return CurrencyExchange(
            from_currency_id=exchange_schema.from_currency_id,
            to_currency_id=exchange_schema.to_currency_id,
            rate=exchange_schema.rate,
            date=exchange_schema.date,
        )

    @classmethod
    async def delete_currency_exchange(cls, exchange_id: str, user_id: str) -> bool:
        await CurrencyExchangeCRUD.delete_one_by_user(exchange_id, user_id)
        return True
