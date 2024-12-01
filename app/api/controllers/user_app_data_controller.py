from decimal import Decimal

from mongoengine import ValidationError

from app.crud.currency_crud import CurrencyCRUD
from app.crud.currency_exchange_crud import CurrencyExchangeCRUD
from app.crud.user_app_data_crud import UserAppDataCRUD
from app.crud.wallet_crud import WalletCRUD
from models.models import Currency, User, UserAppData


class UserAppDataController:
    @classmethod
    async def change_base_currency_by_id(
        cls, user: User, new_base_currency_id: str
    ) -> dict:
        current_base_currency = await cls._get_base_currency(user)

        if str(current_base_currency.id) == new_base_currency_id:
            raise ValidationError("This currency is already set as base currency")

        currency_to_set = await cls._retrieve_currency_to_set(
            user.id, new_base_currency_id
        )

        # Check for necessary exchange rates
        await cls._validate_exchange_rates(
            user.id, current_base_currency, currency_to_set
        )

        user_app_data = await UserAppDataCRUD.get_one_by_user_id(user.id)
        updated_currency = await cls._set_new_base_currency(
            user_app_data, currency_to_set
        )

        return updated_currency.to_dict()

    @classmethod
    async def _get_base_currency(cls, user):
        user_app_data = await UserAppDataCRUD.get_one_by_user_id(user.id)
        current_base_currency_id = user_app_data.base_currency_id.pk
        current_base_currency = await CurrencyCRUD.get_one_by_user(
            current_base_currency_id, user.id
        )

        return current_base_currency

    @classmethod
    async def _retrieve_currency_to_set(
        cls, user_id: str, currency_id: str
    ) -> Currency:
        return await CurrencyCRUD.get_one_by_user(currency_id, user_id)

    @classmethod
    async def _validate_exchange_rates(
        cls, user_id: str, current_base_currency: Currency, new_base_currency: Currency
    ) -> None:

        wallets = await WalletCRUD.get_all_by_user_id_optional(user_id)
        held_currency_ids = {
            balance.currency_id.id
            for wallet in wallets
            for balance in wallet.balances_ids
        }

        # Check for exchange rates between held currencies and the new base currency
        for currency_id in held_currency_ids:
            if currency_id == new_base_currency.id:
                continue
            if not await CurrencyExchangeCRUD.exchange_rate_exists(
                user_id, currency_id, new_base_currency.id
            ):
                raise ValidationError(
                    f"Missing exchange rate for currency\
                        {currency_id} to new base currency {new_base_currency.id}"
                )

        # Check for exchange rates between the current and new base currencies
        if (
            current_base_currency
            and not await CurrencyExchangeCRUD.exchange_rate_exists(
                user_id, current_base_currency.id, new_base_currency.id
            )
        ):
            raise ValidationError(
                f"Missing exchange rate between current base currency\
                    {current_base_currency.id} and new base currency {new_base_currency.id}"
            )

    @classmethod
    async def _set_new_base_currency(
        cls, user_app_data: UserAppData, currency: Currency
    ) -> Currency:
        return await UserAppDataCRUD.set_base_currency(user_app_data, currency.id)

    @classmethod
    async def update_user_app_data_net_worth(cls, user, net_worth):
        user_app_data = await UserAppDataCRUD.get_one_by_user_id(user.id)
        user_app_data.net_worth = net_worth
        updated_data = await UserAppDataCRUD.update_one_by_id(
            user_app_data.id, user_app_data
        )
        return updated_data.to_dict()

    @classmethod
    async def get_user_app_data(cls, user: User) -> dict:
        user_app_data = await UserAppDataCRUD.get_one_by_user_id(user.id)
        return user_app_data.to_dict()

    @classmethod
    async def _convert_to_base_currency(
        cls, user_id: str, amount: Decimal, currency_id: str
    ) -> Decimal:
        base_currency_id = await UserAppDataCRUD.get_base_currency_id_by_user_id(
            user_id
        )
        return await CurrencyExchangeCRUD.convert_value_to_base_currency(
            amount, currency_id, base_currency_id, user_id
        )

    @classmethod
    async def add_value_to_user_app_data_wallets_value(
        cls, user: User, amount: Decimal, currency_id: str
    ):
        converted_amount = await cls._convert_to_base_currency(
            user.id, amount, currency_id
        )

        await UserAppDataCRUD.add_amount_to_user_app_data_wallets_value(
            user.id, converted_amount
        )

    @classmethod
    async def reduce_value_from_user_app_data_wallets_value(
        cls, user: User, amount: Decimal, currency_id: str
    ):
        converted_amount = await cls._convert_to_base_currency(
            user.id, amount, currency_id
        )

        await UserAppDataCRUD.reduce_amount_from_user_app_data_wallets_value(
            user.id, converted_amount
        )

    @classmethod
    async def add_value_to_user_app_data_assets_value(
        cls, user: User, amount: Decimal, currency_id: str
    ):
        converted_amount = await cls._convert_to_base_currency(
            user.id, amount, currency_id
        )

        await UserAppDataCRUD.add_amount_to_user_app_data_assets_value(
            user.id, converted_amount
        )

    @classmethod
    async def reduce_value_from_user_app_data_assets_value(
        cls, user: User, amount: Decimal, currency_id: str
    ):
        converted_amount = await cls._convert_to_base_currency(
            user.id, amount, currency_id
        )

        await UserAppDataCRUD.reduce_amount_from_user_app_data_assets_value(
            user.id, converted_amount
        )
