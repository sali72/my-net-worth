from models.models import CurrencyExchange


class CurrencyExchangeCRUD:

    @classmethod
    async def get_one_by_currencies(
        cls, from_currency_id: str, to_currency_id: str
    ) -> CurrencyExchange:
        return CurrencyExchange.objects.get(
            from_currency_id=from_currency_id, to_currency_id=to_currency_id
        )
