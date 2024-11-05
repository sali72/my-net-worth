from app.crud.wallet_crud import WalletCRUD
from app.crud.user_crud import UserCRUD
from app.crud.currency_crud import CurrencyCRUD
from models.models import Wallet, User
from models.schemas import WalletSchema


class WalletController:

    wallet_crud = WalletCRUD()
    user_crud = UserCRUD()
    currency_crud = CurrencyCRUD()

    @classmethod
    async def create_wallet(cls, wallet_schema: WalletSchema, user: User) -> str:
        wallet = await cls.__create_wallet(wallet_schema, user.id)
        wallet_in_db: Wallet = await cls.wallet_crud.create_one(wallet)
        return str(wallet_in_db.id)

    @classmethod
    async def __create_wallet(cls, wallet_schema: WalletSchema, user_id) -> Wallet:
        currencies = await cls.currency_crud.find_by_currency_codes(
            wallet_schema.currency_codes
        )
        return Wallet(
            user_id=user_id,
            name=wallet_schema.name,
            type=wallet_schema.type,
            currency_ids=currencies,
        )
