from fastapi import APIRouter, Depends, Path
from models.schemas import (
    ResponseSchema,
    WalletCreateSchema,
    WalletUpdateSchema,
    ErrorResponseModel,
    BalanceSchema,
)
from models.schemas import Role as R
from app.api.controllers.auth_controller import has_role
from app.api.controllers.wallet_controller import WalletController

router = APIRouter(prefix="/wallets", tags=["Wallet"])


@router.post(
    "",
    responses={
        200: {"model": ResponseSchema, "description": "Successful Response"},
        400: {"model": ErrorResponseModel, "description": "Bad Request"},
    },
)
async def create_wallet_route(
    wallet_schema: WalletCreateSchema, user=Depends(has_role(R.USER))
):
    wallet_id = await WalletController.create_wallet(wallet_schema, user)
    message = "Wallet created successfully"
    data = {"id": wallet_id}
    return ResponseSchema(data=data, message=message)


@router.get("/total-value", response_model=ResponseSchema)
async def calculate_total_wallet_value_route(user=Depends(has_role(R.USER))):
    total_value = await WalletController.calculate_total_wallet_value(user)
    return ResponseSchema(
        data={"total_value": total_value},
        message="Total wallet value calculated successfully",
    )


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
    wallet_schema: WalletUpdateSchema,
    wallet_id: str = Path(..., description="The ID of the wallet to update"),
    user=Depends(has_role(R.USER)),
):
    updated_wallet = await WalletController.update_wallet(
        wallet_id, wallet_schema, user
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

@router.post("/{wallet_id}/currency-balance", response_model=ResponseSchema)
async def add_balance_route(
    balance: BalanceSchema,
    wallet_id: str = Path(..., description="The ID of the wallet to update"),
    user=Depends(has_role(R.USER)),
):
    updated_wallet = await WalletController.add_balance(
        wallet_id, balance, user
    )
    return ResponseSchema(
        data={"wallet": updated_wallet}, message="Currency balance added successfully"
    )

@router.delete("/{wallet_id}/currency-balance/{currency_id}", response_model=ResponseSchema)
async def remove_balance_route(
    wallet_id: str = Path(..., description="The ID of the wallet to update"),
    currency_id: str = Path(..., description="The ID of the currency to remove"),
    user=Depends(has_role(R.USER)),
):
    updated_wallet = await WalletController.remove_balance(
        wallet_id, currency_id, user
    )
    return ResponseSchema(
        data={"wallet": updated_wallet}, message="Currency balance removed successfully"
    )