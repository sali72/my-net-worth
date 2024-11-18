from decimal import Decimal
from typing import List

from fastapi import HTTPException, status

from app.crud.currency_crud import CurrencyCRUD
from app.crud.currency_exchange_crud import CurrencyExchangeCRUD
from app.crud.wallet_crud import WalletCRUD
from app.crud.user_app_data_crud import UserAppDataCRUD
from models.models import Currency, CurrencyBalance, User, Wallet
from models.schemas import CurrencyBalanceSchema, WalletCreateSchema, WalletUpdateSchema


class WalletController:

    @classmethod
    async def create_wallet(cls, wallet_schema: WalletCreateSchema, user: User) -> str:
        wallet = await cls.__create_wallet_obj_to_create(wallet_schema, user.id)
        wallet_in_db: Wallet = await WalletCRUD.create_one(wallet)
        return wallet_in_db.to_dict()

    @classmethod
    async def __create_wallet_obj_to_create(
        cls, wallet_schema: WalletCreateSchema, user_id: str
    ) -> Wallet:
        currency_balances = await cls.__create_currency_balance_objs_list(
            wallet_schema.currency_balances, wallet_schema.type
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
        wallet_currency_type: str,
    ) -> List[CurrencyBalance]:
        currency_balances = []
        for cb in currency_balances_in_schema:
            await cls.__validate_currency(cb, wallet_currency_type)
            currency_balance = CurrencyBalance(
                currency_id=cb.currency_id,
                balance=Decimal(cb.balance),
            )
            currency_balances.append(currency_balance)
        return currency_balances

    @classmethod
    async def __validate_currency(cls, cb, wallet_currency_type):
        currency: Currency = await CurrencyCRUD.get_one_by_id(cb.currency_id)
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
        cls, wallet_id: str, wallet_update_schema: WalletUpdateSchema, user_id: str
    ) -> Wallet:
        updated_wallet = await cls.__create_wallet_obj_for_update(wallet_update_schema)
        await WalletCRUD.update_one_by_user(user_id, wallet_id, updated_wallet)
        wallet_from_db = await WalletCRUD.get_one_by_id(wallet_id)
        return wallet_from_db.to_dict()

    @classmethod
    async def __create_wallet_obj_for_update(
        cls, wallet_schema: WalletUpdateSchema
    ) -> Wallet:
        if wallet_schema.currency_balances:
            currency_balances = await cls.__create_currency_balance_objs_list(
                wallet_schema.currency_balances, wallet_schema.type
            )
        else:
            currency_balances = None

        updated_wallet = Wallet(
            name=wallet_schema.name,
            type=wallet_schema.type,
            currency_balances=currency_balances,
        )
        return updated_wallet

    @classmethod
    async def delete_wallet(cls, wallet_id: str, user_id: str) -> bool:
        await WalletCRUD.delete_one_by_user(user_id, wallet_id)
        return True

    @classmethod
    async def calculate_total_wallet_value(cls, user: User) -> Decimal:
        wallets = await cls._get_user_wallets(user.id)

        base_currency_id = await UserAppDataCRUD.get_base_currency_id(
            user.user_app_data.id
        )
        
        total_value = Decimal(0)
        for wallet in wallets:
            total_value += await cls._calculate_wallet_value(
                wallet, base_currency_id, user.id
            )

        return total_value

    @classmethod
    async def _get_user_wallets(cls, user_id: str) -> List[Wallet]:
        return await WalletCRUD.get_all_by_user_id_optional(user_id)

    @classmethod
    async def _calculate_wallet_value(
        cls, wallet: Wallet, base_currency_id: str, user_id: str
    ) -> Decimal:
        total_value = Decimal(0)
        for balance in wallet.currency_balances:
            total_value += await cls._calculate_balance_value(
                balance, base_currency_id, user_id
            )
        return total_value

    @classmethod
    async def _calculate_balance_value(
        cls, balance, base_currency_id: str, user_id: str
    ) -> Decimal:
        currency = await CurrencyCRUD.get_one_by_id(balance.currency_id.id)
        return await cls._convert_to_base_currency(
            balance, currency, base_currency_id, user_id
        )

    @classmethod
    async def _convert_to_base_currency(
        cls, balance, currency: Currency, base_currency_id: str, user_id: str
    ) -> Decimal:
        if currency.id == base_currency_id:
            return balance.balance

        exchange_rate = await CurrencyExchangeCRUD.get_exchange_rate(
            user_id, currency.id, base_currency_id
        )
        return balance.balance * exchange_rate
