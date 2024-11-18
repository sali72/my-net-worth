from bson import ObjectId
from mongoengine import DoesNotExist, Q, QuerySet

from models.models import Currency


class CurrencyCRUD:

    @classmethod
    async def create_one(cls, currency: Currency) -> Currency:
        currency.clean()
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

    @staticmethod
    async def get_one_by_user_and_code_optional(code: str, user_id: str) -> Currency:
        return Currency.objects(
            (Q(code=code) & Q(user_id=user_id)) | Q(code=code, is_predefined=True)
        ).first()

    @classmethod
    async def get_all_by_user_id(cls, user_id: str) -> QuerySet:
        return Currency.objects(Q(is_predefined=True) | Q(user_id=user_id))

    @classmethod
    async def get_all_predefined(cls) -> QuerySet:
        return Currency.objects(is_predefined=True)

    @classmethod
    async def update_one_by_user(
        cls, user_id: str, currency_id: str, updated_currency: Currency
    ):
        currency = await cls.get_one_by_user(currency_id, user_id)
        cls.__update_currency_fields(currency, updated_currency)
        currency.clean()
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
