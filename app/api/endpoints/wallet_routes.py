from fastapi import APIRouter, Depends

from app.api.controllers.auth_controller import has_role
from models.schemas import ResponseSchema, WalletSchema
from models.schemas import Role as R
from app.api.controllers.wallet_controller import WalletController

router = APIRouter(prefix="/wallets", tags=["Wallet"])


@router.post("", response_model=ResponseSchema)
async def create_wallet_route(
    wallet_schema: WalletSchema, 
    user=Depends(has_role(R.USER))
):
    wallet_id = await WalletController.create_wallet(wallet_schema, user)
    message = "Wallet created successfully"
    data = {"id": wallet_id}
    return ResponseSchema(data=data, message=message)
