from fastapi import APIRouter, Depends, HTTPException, Path
from models.schemas import ResponseSchema, WalletSchema
from models.schemas import Role as R
from app.api.controllers.auth_controller import has_role
from app.api.controllers.wallet_controller import WalletController

router = APIRouter(prefix="/wallets", tags=["Wallet"])


@router.post("", response_model=ResponseSchema)
async def create_wallet_route(
    wallet_schema: WalletSchema, user=Depends(has_role(R.USER))
):
    wallet_id = await WalletController.create_wallet(wallet_schema, user)
    message = "Wallet created successfully"
    data = {"id": wallet_id}
    return ResponseSchema(data=data, message=message)


@router.get("/{wallet_id}", response_model=ResponseSchema)
async def read_wallet_route(
    wallet_id: str = Path(..., description="The ID of the wallet to retrieve"),
    user=Depends(has_role(R.USER)),
):
    wallet = await WalletController.get_wallet(wallet_id, user.id)
    return ResponseSchema(
        data={"wallet": wallet}, message="Wallet retrieved successfully"
    )


@router.get("", response_model=ResponseSchema)
async def read_all_wallets_route(user=Depends(has_role(R.USER))):
    wallets = await WalletController.get_all_wallets(user.id)
    return ResponseSchema(
        data={"wallets": wallets}, message="Wallets retrieved successfully"
    )


@router.put("/{wallet_id}", response_model=ResponseSchema)
async def update_wallet_route(
    wallet_schema: WalletSchema,
    wallet_id: str = Path(..., description="The ID of the wallet to update"),
    user=Depends(has_role(R.USER)),
):
    updated_wallet = await WalletController.update_wallet(
        wallet_id, wallet_schema, user.id
    )
    return ResponseSchema(
        data={"wallet": updated_wallet}, message="Wallet updated successfully"
    )


@router.delete("/{wallet_id}", response_model=ResponseSchema)
async def delete_wallet_route(
    wallet_id: str = Path(..., description="The ID of the wallet to delete"),
    user=Depends(has_role(R.USER)),
):
    success = await WalletController.delete_wallet(wallet_id, user.id)
    return ResponseSchema(message="Wallet deleted successfully")
