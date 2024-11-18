from mongoengine import ValidationError

from app.crud.currency_crud import CurrencyCRUD
from app.crud.currency_exchange_crud import CurrencyExchangeCRUD
from app.crud.wallet_crud import WalletCRUD
from app.crud.user_app_data_crud import UserAppDataCRUD
from models.models import Currency, User, UserAppData


class UserAppDataController:
    @classmethod
    async def change_base_currency_by_id(cls, user: User, currency_id: str) -> dict:
        current_base_currency = await cls._get_base_currency(user)

        currency_to_set = await cls._retrieve_currency_to_set(user.id, currency_id)

        # Check for necessary exchange rates
        await cls._validate_exchange_rates(
            user.id, current_base_currency, currency_to_set
        )

        updated_currency = await cls._set_new_base_currency(
            user.user_app_data, currency_to_set
        )

        return updated_currency.to_dict()

    @classmethod
    async def _get_base_currency(cls, user):
        current_base_currency_id = user.user_app_data.base_currency_id.pk
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
        # Get all wallets for the user
        wallets = await WalletCRUD.get_all_by_user_id_optional(user_id)
        held_currency_ids = {
            balance.currency_id.id
            for wallet in wallets
            for balance in wallet.currency_balances
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
        return await UserAppDataCRUD.set_base_currency(user_app_data, currency)

    @classmethod
    async def update_user_app_data_net_worth(cls, user, net_worth):
        user_app_data: UserAppData = user.user_app_data
        user_app_data.net_worth = net_worth
        await UserAppDataCRUD.update_one_by_id(user.user_app_data.id, user_app_data)