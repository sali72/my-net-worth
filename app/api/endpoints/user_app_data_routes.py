from fastapi import APIRouter, Depends, Path

from app.api.controllers.auth_controller import has_role
from app.api.controllers.user_app_data_controller import UserAppDataController
from models.schemas import ResponseSchema
from models.schemas import Role as R

router = APIRouter(prefix="/user-app-data", tags=["UserAppData"])

@router.post("/set-base/{currency_id}", response_model=ResponseSchema)
async def set_base_currency_by_id_route(
    currency_id: str = Path(..., description="The ID of the currency to set as base"),
    user=Depends(has_role(R.USER)),
):
    result = await UserAppDataController.set_base_currency_by_id(user, currency_id)
    return ResponseSchema(
        data=result,
        message="Base currency set successfully",
    )