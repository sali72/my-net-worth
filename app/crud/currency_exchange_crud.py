from mongoengine import DoesNotExist, QuerySet

from models.models import CurrencyExchange


class CurrencyExchangeCRUD:

    @classmethod
    async def get_one_by_currencies_and_user(
        cls, user_id: str, from_currency_id: str, to_currency_id: str
    ) -> CurrencyExchange:
        return CurrencyExchange.objects.get(
            user_id=user_id,
            from_currency_id=from_currency_id,
            to_currency_id=to_currency_id,
        )

    @classmethod
    async def get_one_by_currencies(
        cls, from_currency_id: str, to_currency_id: str
    ) -> CurrencyExchange:
        return CurrencyExchange.objects.get(
            from_currency_id=from_currency_id, to_currency_id=to_currency_id
        )

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
    ):
        exchange = await cls.get_one_by_user(exchange_id, user_id)
        cls.__update_exchange_fields(exchange, updated_exchange)
        exchange.save()

    @staticmethod
    def __update_exchange_fields(
        exchange: CurrencyExchange, updated_exchange: CurrencyExchange
    ):
        if updated_exchange.from_currency_id is not None:
            exchange.from_currency_id = updated_exchange.from_currency_id
        if updated_exchange.to_currency_id is not None:
            exchange.to_currency_id = updated_exchange.to_currency_id
        if updated_exchange.rate is not None:
            exchange.rate = updated_exchange.rate
        if updated_exchange.date is not None:
            exchange.date = updated_exchange.date

    @classmethod
    async def delete_one_by_user(cls, exchange_id: str, user_id: str) -> bool:
        result = CurrencyExchange.objects(id=exchange_id, user_id=user_id).delete()
        if result == 0:
            raise DoesNotExist(
                f"CurrencyExchange with id {exchange_id} for user {user_id} does not exist"
            )
        return result > 0

    @classmethod
    async def exchange_rate_exists(
        cls, user_id: str, from_currency_id: str, to_currency_id: str
    ) -> bool:
        # Check if an exchange rate exists in either direction
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
        )
