from fastapi import APIRouter, Depends, Path
from models.schemas import (
    ResponseSchema,
    ErrorResponseModel,
    AssetTypeCreateSchema,
    AssetTypeUpdateSchema,
)
from models.schemas import Role as R
from app.api.controllers.auth_controller import has_role
from app.api.controllers.asset_type_controller import AssetTypeController

router = APIRouter(prefix="/asset-types", tags=["AssetType"])


@router.post(
    "",
    responses={
        200: {"model": ResponseSchema, "description": "Successful Response"},
        400: {"model": ErrorResponseModel, "description": "Bad Request"},
    },
)
async def create_asset_type_route(
    asset_type_schema: AssetTypeCreateSchema, user=Depends(has_role(R.USER))
):
    asset_type_id = await AssetTypeController.create_asset_type(asset_type_schema, user)
    message = "Asset type created successfully"
    data = {"id": asset_type_id}
    return ResponseSchema(data=data, message=message)


@router.get("/{asset_type_id}", response_model=ResponseSchema)
async def read_asset_type_route(
    asset_type_id: str = Path(..., description="The ID of the asset type to retrieve"),
    user=Depends(has_role(R.USER)),
):
    asset_type = await AssetTypeController.get_asset_type(asset_type_id, user.id)
    return ResponseSchema(
        data={"asset_type": asset_type}, message="Asset type retrieved successfully"
    )


@router.get("", response_model=ResponseSchema)
async def read_all_asset_types_route(user=Depends(has_role(R.USER))):
    asset_types = await AssetTypeController.get_all_asset_types(user.id)
    return ResponseSchema(
        data={"asset_types": asset_types},
        message="Asset types retrieved successfully",
    )


@router.put("/{asset_type_id}", response_model=ResponseSchema)
async def update_asset_type_route(
    asset_type_schema: AssetTypeUpdateSchema,
    asset_type_id: str = Path(..., description="The ID of the asset type to update"),
    user=Depends(has_role(R.USER)),
):
    updated_asset_type = await AssetTypeController.update_asset_type(
        asset_type_id, asset_type_schema, user.id
    )
    return ResponseSchema(
        data={"asset_type": updated_asset_type},
        message="Asset type updated successfully",
    )


@router.delete("/{asset_type_id}", response_model=ResponseSchema)
async def delete_asset_type_route(
    asset_type_id: str = Path(..., description="The ID of the asset type to delete"),
    user=Depends(has_role(R.USER)),
):
    success = await AssetTypeController.delete_asset_type(asset_type_id, user.id)
    return ResponseSchema(message="Asset type deleted successfully")
