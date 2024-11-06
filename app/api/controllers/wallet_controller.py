from app.crud.wallet_crud import WalletCRUD
from app.crud.user_crud import UserCRUD
from app.crud.currency_crud import CurrencyCRUD
from models.models import Wallet, User, CurrencyBalance
from models.schemas import WalletCreateSchema, CurrencyBalanceSchema
from typing import List


class WalletController:

    wallet_crud = WalletCRUD()
    user_crud = UserCRUD()
    currency_crud = CurrencyCRUD()

    @classmethod
    async def create_wallet(cls, wallet_schema: WalletCreateSchema, user: User) -> str:
        wallet = await cls.__create_wallet_object(wallet_schema, user.id)
        wallet_in_db: Wallet = await cls.wallet_crud.create_one(wallet)
        return wallet_in_db.to_dict()

    @classmethod
    async def __create_wallet_object(
        cls, wallet_schema: WalletCreateSchema, user_id
    ) -> Wallet:
        currency_balances = await cls.__create_currency_balance_objects_list(
            wallet_schema.currency_balances
        )
        return Wallet(
            user_id=user_id,
            name=wallet_schema.name,
            type=wallet_schema.type,
            currency_balances=currency_balances,
        )

    @classmethod
    async def __create_currency_balance_objects_list(
        cls, currency_balances_in_schema: List[CurrencyBalanceSchema]
    ) -> List[CurrencyBalance]:
        currency_balances = []
        for cb in currency_balances_in_schema:
            await cls.__validate_currency(cb)
            
            currency_balance = CurrencyBalance(
                currency_id=cb.currency_id, balance=cb.balance
            )
            currency_balances.append(currency_balance)
        return currency_balances

    @classmethod
    async def __validate_currency(cls, cb):
        await CurrencyCRUD.get_one_by_id(cb.currency_id)

    @classmethod
    async def get_wallet(cls, wallet_id: str, user_id: str) -> Wallet:
        wallet = await cls.wallet_crud.get_one_by_user(wallet_id, user_id)
        return wallet.to_dict()

    @classmethod
    async def get_all_wallets(cls, user_id: str) -> List[dict]:
        wallets: List[Wallet] = await cls.wallet_crud.get_all_by_user_id_optional(
            user_id
        )
        wallets_list = [wallet.to_dict() for wallet in wallets]
        return wallets_list

    @classmethod
    async def update_wallet(
        cls, wallet_id: str, wallet_schema: WalletCreateSchema, user_id: str
    ) -> Wallet:
        updated_wallet = cls.__create_wallet_for_update(wallet_schema)
        await cls.wallet_crud.update_one_by_user(user_id, wallet_id, updated_wallet)
        return await cls.wallet_crud.get_one_by_user(wallet_id)

    @classmethod
    def __create_wallet_for_update(cls, wallet_schema) -> Wallet:
        updated_wallet = Wallet(
            name=wallet_schema.name,
            type=wallet_schema.type,
            currency_ids=wallet_schema.currency_codes,
        )
        return updated_wallet

    @classmethod
    async def delete_wallet(cls, wallet_id: str, user_id: str) -> bool:
        await cls.wallet_crud.delete_one_by_user(user_id, wallet_id)
        return True
