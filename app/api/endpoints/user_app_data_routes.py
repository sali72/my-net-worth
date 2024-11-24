from fastapi import APIRouter, Depends, Path

from app.api.controllers.asset_controller import AssetController
from app.api.controllers.auth_controller import has_role
from app.api.controllers.user_app_data_controller import UserAppDataController
from app.api.controllers.wallet_controller import WalletController
from models.schemas import ResponseSchema
from models.schemas import Role as R

router = APIRouter(prefix="/user-app-data", tags=["UserAppData"])


@router.post("/change-base-currency/{currency_id}", response_model=ResponseSchema)
async def change_base_currency_by_id_route(
    currency_id: str = Path(
        ..., description="The ID of the currency to change as base"
    ),
    user=Depends(has_role(R.USER)),
):
    result = await UserAppDataController.change_base_currency_by_id(user, currency_id)
    return ResponseSchema(
        data=result,
        message="Base currency changed successfully",
    )


@router.get("/net-worth", response_model=ResponseSchema)
async def calculate_net_worth_route(user=Depends(has_role(R.USER))):

    total_wallets_value = await WalletController.calculate_total_wallet_value(user)
    total_assets_value = await AssetController.calculate_total_asset_value(user)
    net_worth = total_wallets_value + total_assets_value

    await UserAppDataController.update_user_app_data_net_worth(user, net_worth)

    return ResponseSchema(
        data={"net_worth": net_worth},
        message="Net worth calculated successfully",
    )


@router.get("/user-data", response_model=ResponseSchema)
async def get_user_app_data_route(user=Depends(has_role(R.USER))):
    user_app_data = await UserAppDataController.get_user_app_data(user)
    return ResponseSchema(
        data=user_app_data,
        message="User app data retrieved successfully",
    )
