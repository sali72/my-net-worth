from models.models import Currency
from typing import List
from mongoengine import DoesNotExist
from bson import ObjectId


class CurrencyCRUD:

    @classmethod
    async def create_one(cls, currency: Currency) -> Currency:
        currency.save()
        return currency

    @classmethod
    async def get_one_by_id(cls, currency_id: str) -> Currency:
        return Currency.objects.get(pk=ObjectId(currency_id))
    
    @classmethod
    async def get_one_by_user(cls, currency_id: str, user_id: str) -> Currency:
        return Currency.objects.get(id=currency_id, user_id=user_id)

    @classmethod
    async def find_by_currency_codes_optional(
        cls,
        currency_codes_list: List[str],
    ) -> List[Currency]:
        return Currency.objects(code__in=currency_codes_list)

    @classmethod
    async def find_by_currency_codes(
        cls, currency_codes_list: List[str]
    ) -> List[Currency]:
        currencies = await cls.find_by_currency_codes_optional(currency_codes_list)

        if not currencies:
            raise DoesNotExist(f"No currencies found for codes: {currency_codes_list}")

        if len(currencies) != len(currency_codes_list):
            missing_codes = set(currency_codes_list) - set(
                currency.code for currency in currencies
            )
            raise DoesNotExist(f"Missing currencies for codes: {missing_codes}")

        return list(currencies)

    @classmethod
    async def find_by_currency_ids_optional(
        cls,
        currency_ids_list: List[str],
    ) -> List[Currency]:
        return Currency.objects(currency_id__in=currency_ids_list)

    @classmethod
    async def find_by_currency_ids(cls, currency_ids_list: List[str]) -> List[Currency]:
        currencies = await cls.find_by_currency_ids_optional(currency_ids_list)

        if not currencies:
            raise DoesNotExist(f"No currencies found for IDs: {currency_ids_list}")

        if len(currencies) != len(currency_ids_list):
            missing_ids = set(currency_ids_list) - set(
                currency.currency_id for currency in currencies
            )
            raise DoesNotExist(f"Missing currencies for IDs: {missing_ids}")

        return list(currencies)

    @classmethod
    async def get_base_currency(cls, user_id: str) -> Currency:
        return Currency.objects.get(user_id=user_id, is_base_currency=True)
