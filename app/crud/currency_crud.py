from models.models import Currency
from typing import List
from mongoengine import DoesNotExist


class CurrencyCRUD:

    async def create_one(self, currency: Currency) -> Currency:
        currency.save()
        return currency

    async def find_by_currency_codes_optional(
        self,
        currency_codes_list: List[str],
    ) -> List[Currency]:
        return Currency.objects(code__in=currency_codes_list)

    async def find_by_currency_codes(
        self, currency_codes_list: List[str]
    ) -> List[Currency]:
        currencies = await self.find_by_currency_codes_optional(currency_codes_list)
        
        if not currencies:
            raise DoesNotExist(f"No currencies found for codes: {currency_codes_list}")

        if len(currencies) != len(currency_codes_list):
            missing_codes = set(currency_codes_list) - set(
                currency.code for currency in currencies
            )
            raise DoesNotExist(f"Missing currencies for codes: {missing_codes}")

        return list(currencies)
