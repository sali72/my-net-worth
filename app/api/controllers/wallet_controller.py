from decimal import Decimal
from typing import List

from fastapi import HTTPException, status

from app.crud.currency_crud import CurrencyCRUD
from app.crud.currency_exchange_crud import CurrencyExchangeCRUD
from app.crud.user_app_data_crud import UserAppDataCRUD
from app.crud.wallet_crud import WalletCRUD
from app.crud.balance_crud import BalanceCRUD
from models.models import Currency, Balance, User, UserAppData, Wallet
from models.schemas import BalanceSchema, WalletCreateSchema, WalletUpdateSchema


class WalletController:

    @classmethod
    async def create_wallet(cls, wallet_schema: WalletCreateSchema, user: User) -> str:
        wallet = await cls._create_wallet_obj_to_create(wallet_schema, user.id)

        balances = await cls._create_balance_objs_list(wallet_schema.balances_ids)
        for b in balances:
            await cls._validate_currency_and_wallet_type_match(
                b.currency_id.pk, wallet.type
            )

        wallet_in_db = await WalletCRUD.create_one(wallet)
        await cls._save_balances(wallet_in_db, balances)
        wallet_with_balances = await WalletCRUD.get_one_by_id(wallet_in_db.id)

        await cls._add_wallet_value_to_user_app_data(user, wallet_with_balances)

        return wallet_with_balances.to_dict()

    @classmethod
    async def _add_wallet_value_to_user_app_data(
        cls, user: User, wallet_with_balances: Wallet
    ):
        base_currency_id = await UserAppDataCRUD.get_base_currency_id_by_user_id(
            user.id
        )
        wallet_value = await cls._calculate_wallet_value(
            wallet_with_balances, base_currency_id, user.id
        )
        user_app_data = await UserAppDataCRUD.get_one_by_user_id(user.id)
        await cls._add_amount_to_user_app_data(user_app_data.id, wallet_value)

    @classmethod
    async def _create_wallet_obj_to_create(
        cls, wallet_schema: WalletCreateSchema, user_id: str
    ) -> Wallet:
        return Wallet(
            user_id=user_id,
            name=wallet_schema.name,
            type=wallet_schema.type,
        )

    @classmethod
    async def _save_balances(cls, wallet: Wallet, balances: List[Balance]):
        for balance in balances:
            balance.wallet_id = wallet.id
            await BalanceCRUD.create_one(balance)

    @classmethod
    async def _create_balance_objs_list(
        cls,
        balances_in_schema: List[BalanceSchema],
    ) -> List[Balance]:
        balances = []
        for b in balances_in_schema:
            balance = Balance(
                currency_id=b.currency_id,
                amount=Decimal(b.amount),
            )
            balances.append(balance)
        return balances

    @classmethod
    async def _validate_currency_and_wallet_type_match(
        cls, b_currency_id: str, wallet_currency_type: str
    ):
        currency: Currency = await CurrencyCRUD.get_one_by_id(b_currency_id)
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
        updated_wallet = await cls._create_wallet_obj_for_update(wallet_update_schema)

        current_wallet = await WalletCRUD.get_one_by_user(wallet_id, user.id)

        if updated_wallet.balances_ids:
            for b in updated_wallet.balances_ids:
                await cls._validate_currency_and_wallet_type_match(
                    b.currency_id.pk, current_wallet.type
                )

        await WalletCRUD.update_one_by_user(user.id, wallet_id, updated_wallet)

        if updated_wallet.balances_ids:
            await cls.calculate_total_wallet_value(user)

        wallet_from_db = await WalletCRUD.get_one_by_id(wallet_id)
        return wallet_from_db.to_dict()

    @classmethod
    async def _create_wallet_obj_for_update(
        cls, wallet_schema: WalletUpdateSchema
    ) -> Wallet:
        if wallet_schema.balances_ids:
            balances = await cls._create_balance_objs_list(wallet_schema.balances_ids)
        else:
            balances = None

        updated_wallet = Wallet(
            name=wallet_schema.name,
            balances_ids=balances,
        )
        return updated_wallet

    @classmethod
    async def delete_wallet(cls, wallet_id: str, user: User) -> bool:
        wallet_to_delete: Wallet = await WalletCRUD.get_one_by_user(wallet_id, user.id)
        await cls._reduce_wallet_value_from_user_app_data(user, wallet_to_delete)
        await WalletCRUD.delete_one_by_user(user.id, wallet_id)
        return True

    @classmethod
    async def _reduce_wallet_value_from_user_app_data(
        cls, user: User, wallet_with_balances: Wallet
    ):
        base_currency_id = await UserAppDataCRUD.get_base_currency_id_by_user_id(
            user.id
        )
        wallet_value = await cls._calculate_wallet_value(
            wallet_with_balances, base_currency_id, user.id
        )
        user_app_data = await UserAppDataCRUD.get_one_by_user_id(user.id)
        await cls._reduce_amount_from_user_app_data(user_app_data.id, wallet_value)

    @classmethod
    async def calculate_total_wallet_value(cls, user: User) -> Decimal:
        wallets = await WalletCRUD.get_all_by_user_id_optional(user.id)

        base_currency_id = await UserAppDataCRUD.get_base_currency_id_by_user_id(
            user.id
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
        user_app_data = await UserAppDataCRUD.get_one_by_user_id(user.id)
        user_app_data.wallets_value = total_value
        user_app_data.net_worth = user_app_data.assets_value + total_value
        await UserAppDataCRUD.update_one_by_id(user_app_data.id, user_app_data)

    @classmethod
    async def _calculate_wallet_value(
        cls, wallet: Wallet, base_currency_id: str, user_id: str
    ) -> Decimal:
        total_value = Decimal(0)
        balances: List[Balance] = wallet.balances_ids
        for balance in balances:
            total_value += await cls._convert_value_to_base_currency(
                balance.amount, balance.currency_id.id, base_currency_id, user_id
            )
        return total_value

    @classmethod
    async def _convert_value_to_base_currency(
        cls, amount: Decimal, currency_id: str, base_currency_id: str, user_id: str
    ) -> Decimal:
        if currency_id == base_currency_id:
            return amount

        exchange_rate = await CurrencyExchangeCRUD.get_exchange_rate(
            user_id, currency_id, base_currency_id
        )
        return amount * exchange_rate

    @classmethod
    async def add_balance(
        cls, wallet_id: str, balance_schema: BalanceSchema, user: User
    ) -> dict:
        wallet = await WalletCRUD.get_one_by_user(wallet_id, user.id)
        await cls._validate_currency_and_wallet_type_match(
            balance_schema.currency_id, wallet.type
        )
        cls._check_existing_balance(wallet, balance_schema)
        new_balance = cls._create_balance(balance_schema, wallet_id)

        # TODO: should make these atomic
        updated_wallet = await BalanceCRUD.create_one(new_balance)
        # updating user app data
        balance_value_to_add = await cls._calculate_balance_value(new_balance, user)
        user_app_data = await UserAppDataCRUD.get_one_by_user_id(user.id)
        await cls._add_amount_to_user_app_data(user_app_data.id, balance_value_to_add)

        return updated_wallet.to_dict()

    @classmethod
    def _check_existing_balance(cls, wallet: Wallet, new_balance: BalanceSchema):
        if any(
            str(balance.currency_id.pk) == new_balance.currency_id
            for balance in wallet.balances_ids
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Balance with same currency already exists in the wallet",
            )

    @classmethod
    def _create_balance(cls, balance: BalanceSchema, wallet_id: str):
        return Balance(
            wallet_id=wallet_id,
            currency_id=balance.currency_id,
            amount=Decimal(balance.amount),
        )

    @classmethod
    async def _add_amount_to_user_app_data(cls, user_app_data_id: str, amount: Decimal):
        user_app_data = await UserAppDataCRUD.get_one_by_id(user_app_data_id)
        user_app_data.wallets_value += amount
        user_app_data.net_worth += amount
        await UserAppDataCRUD.update_one_by_id(user_app_data_id, user_app_data)

    @classmethod
    async def remove_balance(cls, wallet_id: str, currency_id: str, user: User) -> dict:
        balance_to_remove = await WalletCRUD.get_balance(
            user.id, wallet_id, currency_id
        )

        # TODO: should make this atomic
        balance_value_to_remove = await cls._calculate_balance_value(
            balance_to_remove, user
        )
        user_app_data = await UserAppDataCRUD.get_one_by_user_id(user.id)
        await cls._reduce_amount_from_user_app_data(
            user_app_data.id, balance_value_to_remove
        )
        await BalanceCRUD.delete_one_by_wallet_and_currency_id(wallet_id, currency_id)
        updated_wallet = await WalletCRUD.get_one_by_user(wallet_id, user.id)

        return updated_wallet.to_dict()

    @classmethod
    async def _calculate_balance_value(cls, balance: Balance, user: User) -> Decimal:
        base_currency_id = await UserAppDataCRUD.get_base_currency_id_by_user_id(
            user.id
        )
        return await cls._convert_value_to_base_currency(
            balance.amount,
            balance.currency_id.pk,
            base_currency_id,
            user.id,
        )

    # TODO: refactor and move user app data related only methods to
    # relevant file
    @classmethod
    async def _reduce_amount_from_user_app_data(
        cls, user_app_data_id: str, amount: Decimal
    ):
        user_app_data = await UserAppDataCRUD.get_one_by_id(user_app_data_id)
        user_app_data.wallets_value -= amount
        user_app_data.net_worth -= amount
        await UserAppDataCRUD.update_one_by_id(user_app_data_id, user_app_data)

    # TODO: refactor and move user app data related only methods to
    # relevant file
    @classmethod
    async def add_value_to_user_app_data(
        cls, user: User, amount: Decimal, currency_id: str
    ):
        base_currency_id = await UserAppDataCRUD.get_base_currency_id_by_user_id(
            user.id
        )
        await cls._convert_value_to_base_currency(
            amount, currency_id, base_currency_id, user.id
        )
        user_app_data = await UserAppDataCRUD.get_one_by_user_id(user.id)
        await cls._add_amount_to_user_app_data(
            user_app_data.id, amount
        )
    
    @classmethod
    async def reduce_value_from_user_app_data(
        cls, user: User, amount: Decimal, currency_id: str
    ):
        base_currency_id = await UserAppDataCRUD.get_base_currency_id_by_user_id(
            user.id
        )
        await cls._convert_value_to_base_currency(
            amount, currency_id, base_currency_id, user.id
        )
        user_app_data = await UserAppDataCRUD.get_one_by_user_id(user.id)
        await cls._reduce_amount_from_user_app_data(
            user_app_data.id, amount
        )
