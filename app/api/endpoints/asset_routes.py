from fastapi import APIRouter, Depends, Path

from app.api.controllers.asset_controller import AssetController
from app.api.controllers.auth_controller import has_role
from models.schemas import (
    AssetCreateSchema,
    AssetUpdateSchema,
    ErrorResponseModel,
    ResponseSchema,
)
from models.schemas import Role as R

router = APIRouter(prefix="/assets", tags=["Asset"])


@router.post(
    "",
    responses={
        200: {"model": ResponseSchema, "description": "Successful Response"},
        400: {"model": ErrorResponseModel, "description": "Bad Request"},
    },
)
async def create_asset_route(
    asset_schema: AssetCreateSchema, user=Depends(has_role(R.USER))
):
    asset_id = await AssetController.create_asset(asset_schema, user)
    message = "Asset created successfully"
    data = {"id": asset_id}
    return ResponseSchema(data=data, message=message)


@router.get("/total-value", response_model=ResponseSchema)
async def calculate_total_asset_value_route(user=Depends(has_role(R.USER))):
    total_value = await AssetController.calculate_total_asset_value(user.id)
    return ResponseSchema(
        data={"total_value": total_value},
        message="Total asset value calculated successfully",
    )


@router.get("/{asset_id}", response_model=ResponseSchema)
async def read_asset_route(
    asset_id: str = Path(..., description="The ID of the asset to retrieve"),
    user=Depends(has_role(R.USER)),
):
    asset = await AssetController.get_asset(asset_id, user.id)
    return ResponseSchema(data={"asset": asset}, message="Asset retrieved successfully")


@router.get("", response_model=ResponseSchema)
async def read_all_assets_route(user=Depends(has_role(R.USER))):
    assets = await AssetController.get_all_assets(user.id)
    return ResponseSchema(
        data={"assets": assets},
        message="Assets retrieved successfully",
    )


@router.put("/{asset_id}", response_model=ResponseSchema)
async def update_asset_route(
    asset_schema: AssetUpdateSchema,
    asset_id: str = Path(..., description="The ID of the asset to update"),
    user=Depends(has_role(R.USER)),
):
    updated_asset = await AssetController.update_asset(asset_id, asset_schema, user.id)
    return ResponseSchema(
        data={"asset": updated_asset},
        message="Asset updated successfully",
    )


@router.delete("/{asset_id}", response_model=ResponseSchema)
async def delete_asset_route(
    asset_id: str = Path(..., description="The ID of the asset to delete"),
    user=Depends(has_role(R.USER)),
):
    success = await AssetController.delete_asset(asset_id, user.id)
    return ResponseSchema(message="Asset deleted successfully")
