from typing import Dict, List

from fastapi import APIRouter, Depends, Path

from app.api.controllers.asset_type_controller import AssetTypeController
from app.api.controllers.auth_controller import has_role
from models.enums import RoleEnum as R
from models.schemas import (
    AssetTypeCreateSchema,
    AssetTypeUpdateSchema,
    ErrorResponseModel,
    ResponseSchema,
)

router = APIRouter(prefix="/asset-types", tags=["AssetType"])


@router.post(
    "",
    response_model=ResponseSchema,
    responses={
        200: {"model": ResponseSchema, "description": "Successful Response"},
        400: {"model": ErrorResponseModel, "description": "Bad Request"},
    },
)
async def create_asset_type_route(
    asset_type_schema: AssetTypeCreateSchema, user=Depends(has_role(R.USER))
) -> ResponseSchema:
    asset_type_id: Dict = await AssetTypeController.create_asset_type(
        asset_type_schema, user
    )
    message = "Asset type created successfully"
    data = {"id": asset_type_id}
    return ResponseSchema(data=data, message=message)


@router.get("/{asset_type_id}", response_model=ResponseSchema)
async def read_asset_type_route(
    asset_type_id: str = Path(..., description="The ID of the asset type to retrieve"),
    user=Depends(has_role(R.USER)),
) -> ResponseSchema:
    asset_type: Dict = await AssetTypeController.get_asset_type(asset_type_id, user.id)
    return ResponseSchema(
        data={"asset_type": asset_type}, message="Asset type retrieved successfully"
    )


@router.get("", response_model=ResponseSchema)
async def read_all_asset_types_route(user=Depends(has_role(R.USER))) -> ResponseSchema:
    asset_types: List[Dict] = await AssetTypeController.get_all_asset_types(user.id)
    return ResponseSchema(
        data={"asset_types": asset_types},
        message="Asset types retrieved successfully",
    )


@router.put("/{asset_type_id}", response_model=ResponseSchema)
async def update_asset_type_route(
    asset_type_schema: AssetTypeUpdateSchema,
    asset_type_id: str = Path(..., description="The ID of the asset type to update"),
    user=Depends(has_role(R.USER)),
) -> ResponseSchema:
    updated_asset_type: Dict = await AssetTypeController.update_asset_type(
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
) -> ResponseSchema:
    success: bool = await AssetTypeController.delete_asset_type(asset_type_id, user.id)
    return ResponseSchema(message="Asset type deleted successfully")
