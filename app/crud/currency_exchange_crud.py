from decimal import Decimal
from typing import Optional

from bson import ObjectId
from mongoengine import DoesNotExist, QuerySet

from models.models import CurrencyExchange


class CurrencyExchangeCRUD:

    @classmethod
    async def create_one(cls, exchange: CurrencyExchange) -> CurrencyExchange:
        exchange.save()
        return exchange

    @classmethod
    async def get_one_by_user(cls, exchange_id: str, user_id: str) -> CurrencyExchange:
        return CurrencyExchange.objects.get(id=exchange_id, user_id=user_id)

    @classmethod
    async def get_all_by_user_id(cls, user_id: str) -> QuerySet:
        return CurrencyExchange.objects(user_id=user_id)

    @classmethod
    async def update_one_by_user(
        cls, user_id: str, exchange_id: str, updated_exchange: CurrencyExchange
    ) -> None:
        exchange = await cls.get_one_by_user(exchange_id, user_id)
        cls.__update_exchange_fields(exchange, updated_exchange)
        exchange.save()

    @classmethod
    async def delete_one_by_user(cls, exchange_id: str, user_id: str) -> bool:
        result = CurrencyExchange.objects(id=exchange_id, user_id=user_id).delete()
        if result == 0:
            raise DoesNotExist(
                f"CurrencyExchange with id {exchange_id} for user {user_id} does not exist"
            )
        return result > 0

    @classmethod
    async def get_exchange_rate(
        cls, user_id: str, from_currency_id: ObjectId, to_currency_id: ObjectId
    ) -> Decimal:
        direct_rate = await cls._get_direct_exchange_rate(
            user_id, from_currency_id, to_currency_id
        )
        if direct_rate is not None:
            return direct_rate

        reverse_rate = await cls._get_reverse_exchange_rate(
            user_id, from_currency_id, to_currency_id
        )
        if reverse_rate is not None:
            return reverse_rate

        if from_currency_id == to_currency_id:
            return Decimal("1")

        raise DoesNotExist(
            f"No exchange rate found for currencies {from_currency_id} and {to_currency_id} for user {user_id}."
        )

    @classmethod
    async def exchange_rate_exists(
        cls, user_id: str, from_currency_id: str, to_currency_id: str
    ) -> bool:
        return (
            CurrencyExchange.objects(
                user_id=user_id,
                from_currency_id=from_currency_id,
                to_currency_id=to_currency_id,
            ).first()
            or CurrencyExchange.objects(
                user_id=user_id,
                from_currency_id=to_currency_id,
                to_currency_id=from_currency_id,
            ).first()
        ) is not None

    @classmethod
    async def convert_value_to_base_currency(
        cls,
        amount: Decimal,
        currency_id: ObjectId,
        base_currency_id: ObjectId,
        user_id: str,
    ) -> Decimal:
        if currency_id == base_currency_id:
            return amount
        exchange_rate = await cls.get_exchange_rate(
            user_id, currency_id, base_currency_id
        )
        return amount * exchange_rate

    @classmethod
    async def get_direct_exchange_optional(
        cls, user_id: str, from_currency_id: ObjectId, to_currency_id: ObjectId
    ) -> Optional[CurrencyExchange]:
        return CurrencyExchange.objects(
            user_id=user_id,
            from_currency_id=from_currency_id,
            to_currency_id=to_currency_id,
        ).first()

    @classmethod
    async def _get_direct_exchange_rate(
        cls, user_id: str, from_currency_id: ObjectId, to_currency_id: ObjectId
    ) -> Optional[Decimal]:
        direct_exchange = await cls.get_direct_exchange_optional(
            user_id, from_currency_id, to_currency_id
        )
        if direct_exchange:
            return Decimal(direct_exchange.rate)
        return None

    @classmethod
    async def _get_reverse_exchange_rate(
        cls, user_id: str, from_currency_id: str, to_currency_id: str
    ) -> Optional[Decimal]:
        reverse_exchange = await cls.get_direct_exchange_optional(
            user_id, to_currency_id, from_currency_id
        )
        if reverse_exchange:
            return Decimal("1") / Decimal(reverse_exchange.rate)
        return None

    @staticmethod
    def __update_exchange_fields(
        exchange: CurrencyExchange, updated_exchange: CurrencyExchange
    ) -> None:
        if updated_exchange.from_currency_id is not None:
            exchange.from_currency_id = updated_exchange.from_currency_id
        if updated_exchange.to_currency_id is not None:
            exchange.to_currency_id = updated_exchange.to_currency_id
        if updated_exchange.rate is not None:
            exchange.rate = updated_exchange.rate
        if updated_exchange.date is not None:
            exchange.date = updated_exchange.date
