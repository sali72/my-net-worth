from typing import List

from bson import ObjectId
from mongoengine import DoesNotExist, QuerySet, Q

from models.models import Currency


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
        return Currency.objects.get(
            (Q(id=currency_id) & Q(user_id=user_id))
            | Q(id=currency_id, is_predefined=True)
        )

    @classmethod
    async def get_all_by_user_id(cls, user_id: str) -> QuerySet:
        return Currency.objects(user_id=user_id)

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
    async def update_one_by_user(
        cls, user_id: str, currency_id: str, updated_currency: Currency
    ):
        currency = await cls.get_one_by_user(currency_id, user_id)
        cls.__update_currency_fields(currency, updated_currency)
        currency.save()

    @classmethod
    def __update_currency_fields(cls, currency: Currency, updated_currency: Currency):
        if updated_currency.code is not None:
            currency.code = updated_currency.code
        if updated_currency.name is not None:
            currency.name = updated_currency.name
        if updated_currency.symbol is not None:
            currency.symbol = updated_currency.symbol
        if updated_currency.currency_type is not None:
            currency.currency_type = updated_currency.currency_type

    @classmethod
    async def delete_one_by_user(cls, currency_id: str, user_id: str) -> bool:
        result = Currency.objects(id=currency_id, user_id=user_id).delete()
        if result == 0:
            raise DoesNotExist(
                f"Currency with id {currency_id} for user {user_id} does not exist"
            )
        return result > 0
