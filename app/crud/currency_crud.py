from models.models import Currency
from typing import List
from mongoengine.queryset import QuerySet


class CurrencyCRUD:

    async def create_one(self, currency: Currency) -> Currency:
        currency.save()
        return currency

    async def find_by_currency_codes(
        currency_codes_list: List[str],
    ) -> QuerySet[Currency]:
        return Currency.objects(code__in=currency_codes_list)
