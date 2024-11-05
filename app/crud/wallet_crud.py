from models.models import Wallet


class WalletCRUD:

    async def create_one(self, user: Wallet) -> Wallet:
        user.save()
        return user