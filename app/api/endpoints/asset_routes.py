from fastapi import APIRouter, Depends, Path, Query

from app.api.controllers.asset_controller import AssetController
from app.api.controllers.auth_controller import has_role
from app.api.controllers.user_app_data_controller import UserAppDataController
from app.crud.asset_crud import AssetCRUD
from models.enums import RoleEnum as R
from models.models import User
from models.schemas import (
    AssetCreateSchema,
    AssetFilterSchema,
    AssetUpdateSchema,
    ErrorResponseModel,
    ResponseSchema,
)

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
) -> ResponseSchema:
    """
    Create a new asset for the user.

    Args:
        asset_schema (AssetCreateSchema): The schema containing asset details.
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing the created asset's ID and a success message.
    """
    asset = await AssetController.create_asset(asset_schema, user)

    await UserAppDataController.add_value_to_user_app_data_assets_value(
        user, asset.value, asset.currency_id.id
    )

    message = "Asset created successfully"
    data = {"id": asset.to_dict()}
    return ResponseSchema(data=data, message=message)


@router.get("/total-value", response_model=ResponseSchema)
async def calculate_total_asset_value_route(
    user=Depends(has_role(R.USER)),
) -> ResponseSchema:
    """
    Calculate the total value of all assets for the user.

    Args:
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing the total asset value and a success message.
    """
    total_value = await AssetController.calculate_total_asset_value(user)
    return ResponseSchema(
        data={"total_value": total_value},
        message="Total asset value calculated successfully",
    )


@router.get("/filter", response_model=ResponseSchema)
async def filter_assets_route(
    params: AssetFilterSchema = Query(...),
    user=Depends(has_role(R.USER)),
) -> ResponseSchema:
    """
    Retrieve assets based on specified filters.

    Args:
        params (AssetFilterSchema): The filters to apply to the asset retrieval.
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing the filtered assets and a success message.
    """
    filtered_assets = await AssetController.filter_assets(params, user.id)
    return ResponseSchema(
        data={"assets": filtered_assets},
        message="Filtered assets retrieved successfully",
    )


@router.get("/{asset_id}", response_model=ResponseSchema)
async def read_asset_route(
    asset_id: str = Path(..., description="The ID of the asset to retrieve"),
    user=Depends(has_role(R.USER)),
) -> ResponseSchema:
    """
    Retrieve a specific asset by its ID.

    Args:
        asset_id (str): The ID of the asset to retrieve.
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing the asset details and a success message.
    """
    asset = await AssetController.get_asset(asset_id, user.id)
    return ResponseSchema(data={"asset": asset}, message="Asset retrieved successfully")


@router.get("", response_model=ResponseSchema)
async def read_all_assets_route(user=Depends(has_role(R.USER))) -> ResponseSchema:
    """
    Retrieve all assets for the user.

    Args:
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing all assets and a success message.
    """
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
) -> ResponseSchema:
    """
    Update an existing asset.

    Args:
        asset_schema (AssetUpdateSchema): The schema containing updated asset details.
        asset_id (str): The ID of the asset to update.
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing the updated asset details and a success message.
    """
    await _update_user_app_data_assets_value(asset_schema, asset_id, user)

    updated_asset = await AssetController.update_asset(asset_id, asset_schema, user.id)

    return ResponseSchema(
        data={"asset": updated_asset},
        message="Asset updated successfully",
    )


@router.delete("/{asset_id}", response_model=ResponseSchema)
async def delete_asset_route(
    asset_id: str = Path(..., description="The ID of the asset to delete"),
    user=Depends(has_role(R.USER)),
) -> ResponseSchema:
    """
    Delete an asset by its ID.

    Args:
        asset_id (str): The ID of the asset to delete.
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing a success message.
    """
    asset = await AssetController.delete_asset(asset_id, user.id)

    await UserAppDataController.reduce_value_from_user_app_data_assets_value(
        user, asset.value, asset.currency_id.id
    )

    return ResponseSchema(message="Asset deleted successfully")


async def _update_user_app_data_assets_value(
    asset_schema: AssetUpdateSchema, asset_id: str, user: User
) -> None:
    """
    Update the user's app data asset values based on the asset update.

    This function calculates the difference in asset value and updates the user's
    app data accordingly by either adding or reducing the value.

    Args:
        asset_schema (AssetUpdateSchema): The schema containing updated asset details.
        asset_id (str): The ID of the asset to update.
        user (User): The current user, whose asset data is being updated.

    Returns:
        None: This function does not return any value.

    Raises:
        ValueError: If the asset value difference calculation fails.
    """
    current_asset = await AssetCRUD.get_one_by_user(asset_id, user.id)
    if asset_schema.value:
        difference = await AssetController.calculate_asset_value_difference_in_update(
            user.id, asset_id, asset_schema
        )
        if difference != 0:
            if difference > 0:
                await UserAppDataController.add_value_to_user_app_data_assets_value(
                    user, difference, current_asset.currency_id.id
                )
            elif difference < 0:
                await UserAppDataController.reduce_value_from_user_app_data_assets_value(
                    user, difference, current_asset.currency_id.id
                )
