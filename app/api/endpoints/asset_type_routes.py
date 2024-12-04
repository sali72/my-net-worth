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
    """
    Create a new asset type for the user.

    Args:
        asset_type_schema (AssetTypeCreateSchema): The schema containing details of the asset type to create.
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing the created asset type's ID and a success message.
    """
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
    """
    Retrieve a specific asset type by its ID.

    Args:
        asset_type_id (str): The ID of the asset type to retrieve.
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing the asset type details and a success message.
    """
    asset_type: Dict = await AssetTypeController.get_asset_type(asset_type_id, user.id)
    return ResponseSchema(
        data={"asset_type": asset_type}, message="Asset type retrieved successfully"
    )


@router.get("", response_model=ResponseSchema)
async def read_all_asset_types_route(user=Depends(has_role(R.USER))) -> ResponseSchema:
    """
    Retrieve all asset types for the user.

    Args:
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing all asset types and a success message.
    """
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
    """
    Update an existing asset type.

    Args:
        asset_type_schema (AssetTypeUpdateSchema): The schema containing updated asset type details.
        asset_type_id (str): The ID of the asset type to update.
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing the updated asset type details and a success message.
    """
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
    """
    Delete an asset type by its ID.

    Args:
        asset_type_id (str): The ID of the asset type to delete.
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing a success message.
    """
    success: bool = await AssetTypeController.delete_asset_type(asset_type_id, user.id)
    return ResponseSchema(message="Asset type deleted successfully")
