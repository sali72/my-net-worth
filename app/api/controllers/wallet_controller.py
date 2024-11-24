from decimal import Decimal
from typing import List

from fastapi import HTTPException, status

from app.crud.currency_crud import CurrencyCRUD
from app.crud.currency_exchange_crud import CurrencyExchangeCRUD
from app.crud.wallet_crud import WalletCRUD
from app.crud.user_app_data_crud import UserAppDataCRUD
from models.models import Currency, CurrencyBalance, User, Wallet, UserAppData
from models.schemas import CurrencyBalanceSchema, WalletCreateSchema, WalletUpdateSchema


class WalletController:

    @classmethod
    async def create_wallet(cls, wallet_schema: WalletCreateSchema, user: User) -> str:
        wallet = await cls.__create_wallet_obj_to_create(wallet_schema, user.id)

        for cb in wallet.currency_balances:
            await cls.__validate_currency_and_wallet_type_match(cb, wallet.type)

        wallet_in_db: Wallet = await WalletCRUD.create_one(wallet)
        return wallet_in_db.to_dict()

    @classmethod
    async def __create_wallet_obj_to_create(
        cls, wallet_schema: WalletCreateSchema, user_id: str
    ) -> Wallet:
        currency_balances = await cls.__create_currency_balance_objs_list(
            wallet_schema.currency_balances
        )
        return Wallet(
            user_id=user_id,
            name=wallet_schema.name,
            type=wallet_schema.type,
            currency_balances=currency_balances,
        )

    @classmethod
    async def __create_currency_balance_objs_list(
        cls,
        currency_balances_in_schema: List[CurrencyBalanceSchema],
    ) -> List[CurrencyBalance]:
        currency_balances = []
        for cb in currency_balances_in_schema:
            currency_balance = CurrencyBalance(
                currency_id=cb.currency_id,
                balance=Decimal(cb.balance),
            )
            currency_balances.append(currency_balance)
        return currency_balances

    @classmethod
    async def __validate_currency_and_wallet_type_match(
        cls, cb: CurrencyBalance, wallet_currency_type: str
    ):
        currency: Currency = await CurrencyCRUD.get_one_by_id(cb.currency_id.pk)
        if currency.currency_type != wallet_currency_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="wallet type and currency type mismatch",
            )

    @classmethod
    async def get_wallet(cls, wallet_id: str, user_id: str) -> Wallet:
        wallet = await WalletCRUD.get_one_by_user(wallet_id, user_id)
        return wallet.to_dict()

    @classmethod
    async def get_all_wallets(cls, user_id: str) -> List[dict]:
        wallets: List[Wallet] = await WalletCRUD.get_all_by_user_id_optional(user_id)
        wallets_list = [wallet.to_dict() for wallet in wallets]
        return wallets_list

    @classmethod
    async def update_wallet(
        cls, wallet_id: str, wallet_update_schema: WalletUpdateSchema, user: User
    ) -> Wallet:
        updated_wallet = await cls.__create_wallet_obj_for_update(wallet_update_schema)

        current_wallet = await WalletCRUD.get_one_by_user(wallet_id, user.id)

        if updated_wallet.currency_balances:
            for cb in updated_wallet.currency_balances:
                await cls.__validate_currency_and_wallet_type_match(
                    cb, current_wallet.type
                )

        await WalletCRUD.update_one_by_user(user.id, wallet_id, updated_wallet)

        if updated_wallet.currency_balances:
            await cls.calculate_total_wallet_value(user)

        wallet_from_db = await WalletCRUD.get_one_by_id(wallet_id)
        return wallet_from_db.to_dict()

    @classmethod
    async def __create_wallet_obj_for_update(
        cls, wallet_schema: WalletUpdateSchema
    ) -> Wallet:
        if wallet_schema.currency_balances:
            currency_balances = await cls.__create_currency_balance_objs_list(
                wallet_schema.currency_balances
            )
        else:
            currency_balances = None

        updated_wallet = Wallet(
            name=wallet_schema.name,
            currency_balances=currency_balances,
        )
        return updated_wallet

    @classmethod
    async def delete_wallet(cls, wallet_id: str, user_id: str) -> bool:
        await WalletCRUD.delete_one_by_user(user_id, wallet_id)
        return True

    @classmethod
    async def calculate_total_wallet_value(cls, user: User) -> Decimal:
        wallets = await WalletCRUD.get_all_by_user_id_optional(user.id)

        base_currency_id = await UserAppDataCRUD.get_base_currency_id(
            user.user_app_data.id
        )

        total_value = Decimal(0)
        for wallet in wallets:
            total_value += await cls._calculate_wallet_value(
                wallet, base_currency_id, user.id
            )

        await cls._update_user_app_data_wallets_value(user, total_value)

        return total_value

    @classmethod
    async def _update_user_app_data_wallets_value(cls, user, total_value):
        user_app_data: UserAppData = user.user_app_data
        user_app_data.wallets_value = total_value
        user_app_data.net_worth = user_app_data.assets_value + total_value
        await UserAppDataCRUD.update_one_by_id(user.user_app_data.id, user_app_data)

    @classmethod
    async def _calculate_wallet_value(
        cls, wallet: Wallet, base_currency_id: str, user_id: str
    ) -> Decimal:
        total_value = Decimal(0)
        for balance in wallet.currency_balances:
            total_value += await cls._convert_balance_value_to_base_currency(
                balance.balance, balance.currency_id.id, base_currency_id, user_id
            )
        return total_value

    @classmethod
    async def _convert_balance_value_to_base_currency(
        cls, balance: Decimal, currency_id: str, base_currency_id: str, user_id: str
    ) -> Decimal:
        if currency_id == base_currency_id:
            return balance

        exchange_rate = await CurrencyExchangeCRUD.get_exchange_rate(
            user_id, currency_id, base_currency_id
        )
        return balance * exchange_rate

    @classmethod
    async def add_currency_balance(
        cls, wallet_id: str, currency_balance: CurrencyBalanceSchema, user: User
    ) -> dict:
        wallet = await WalletCRUD.get_one_by_user(wallet_id, user.id)
        await cls.__validate_currency_and_wallet_type_match(
            currency_balance, wallet.type
        )
        cls._check_existing_currency_balance(wallet, currency_balance)
        new_balance = cls._create_currency_balance(currency_balance)

        # TODO: should make this atomic
        updated_wallet = await cls._update_wallet_with_new_balance(
            user.id, wallet_id, new_balance
        )
        balance_value_to_add = await cls._calculate_balance_value(new_balance, user)
        await cls._add_balance_to_user_app_data(
            user.user_app_data.id, balance_value_to_add
        )

        return updated_wallet.to_dict()

    @classmethod
    def _check_existing_currency_balance(cls, wallet, currency_balance):
        if any(
            str(balance.currency_id.pk) == currency_balance.currency_id
            for balance in wallet.currency_balances
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Currency balance already exists in the wallet",
            )

    @classmethod
    def _create_currency_balance(cls, currency_balance):
        return CurrencyBalance(
            currency_id=currency_balance.currency_id,
            balance=Decimal(currency_balance.balance),
        )

    @classmethod
    async def _add_balance_to_user_app_data(
        cls, user_app_data_id: str, balance_value: Decimal
    ):
        user_app_data = await UserAppDataCRUD.get_one_by_id(user_app_data_id)
        user_app_data.wallets_value += balance_value
        user_app_data.net_worth += balance_value
        await UserAppDataCRUD.update_one_by_id(user_app_data_id, user_app_data)

    @classmethod
    async def _update_wallet_with_new_balance(cls, user_id, wallet_id, new_balance):
        return await WalletCRUD.add_currency_balance_to_wallet(
            user_id, wallet_id, new_balance
        )

    @classmethod
    async def remove_currency_balance(
        cls, wallet_id: str, currency_id: str, user: User
    ) -> dict:
        currency_balance_to_remove = await WalletCRUD.get_currency_balance(
            user.id, wallet_id, currency_id
        )

        # TODO: should make this atomic
        balance_value_to_remove = await cls._calculate_balance_value(
            currency_balance_to_remove, user
        )
        await cls._reduce_balance_from_user_app_data(
            user.user_app_data.id, balance_value_to_remove
        )
        updated_wallet = await WalletCRUD.remove_currency_balance_from_wallet(
            user.id, wallet_id, currency_id
        )

        return updated_wallet.to_dict()

    @classmethod
    async def _calculate_balance_value(
        cls, currency_balance: CurrencyBalance, user: User
    ) -> Decimal:
        base_currency_id = await UserAppDataCRUD.get_base_currency_id(
            user.user_app_data.id
        )
        return await cls._convert_balance_value_to_base_currency(
            currency_balance.balance,
            currency_balance.currency_id,
            base_currency_id,
            user.id,
        )

    @classmethod
    async def _reduce_balance_from_user_app_data(
        cls, user_app_data_id: str, balance_value: Decimal
    ):
        user_app_data = await UserAppDataCRUD.get_one_by_id(user_app_data_id)
        user_app_data.wallets_value -= balance_value
        user_app_data.net_worth -= balance_value
        await UserAppDataCRUD.update_one_by_id(user_app_data_id, user_app_data)
