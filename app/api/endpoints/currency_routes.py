from fastapi import APIRouter, Depends, Path

from app.api.controllers.auth_controller import has_role
from app.api.controllers.currency_controller import CurrencyController
from models.enums import RoleEnum as R
from models.schemas import (
    CurrencyCreateSchema,
    CurrencyUpdateSchema,
    ErrorResponseModel,
    ResponseSchema,
)

router = APIRouter(prefix="/currencies", tags=["Currency"])


@router.get("/predefined", response_model=ResponseSchema)
async def read_predefined_currencies_route() -> ResponseSchema:
    """
    Retrieve predefined currencies.

    Returns:
        ResponseSchema: The response containing predefined currencies and a success message.
    """
    currencies = await CurrencyController.get_predefined_currencies()
    return ResponseSchema(
        data={"currencies": currencies},
        message="Predefined currencies retrieved successfully",
    )


@router.post(
    "",
    response_model=ResponseSchema,
    responses={
        200: {"model": ResponseSchema, "description": "Successful Response"},
        400: {"model": ErrorResponseModel, "description": "Bad Request"},
    },
)
async def create_currency_route(
    currency_schema: CurrencyCreateSchema, user=Depends(has_role(R.USER))
) -> ResponseSchema:
    """
    Create a new currency.

    Args:
        currency_schema (CurrencyCreateSchema): The schema containing details of the currency to create.
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing the created currency's ID and a success message.
    """
    currency_id = await CurrencyController.create_currency(currency_schema, user)
    message = "Currency created successfully"
    data = {"id": currency_id}
    return ResponseSchema(data=data, message=message)


@router.get("/{currency_id}", response_model=ResponseSchema)
async def read_currency_route(
    currency_id: str = Path(..., description="The ID of the currency to retrieve"),
    user=Depends(has_role(R.USER)),
) -> ResponseSchema:
    """
    Retrieve a specific currency by its ID.

    Args:
        currency_id (str): The ID of the currency to retrieve.
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing the currency details and a success message.
    """
    currency = await CurrencyController.get_currency(currency_id, user.id)
    return ResponseSchema(
        data={"currency": currency}, message="Currency retrieved successfully"
    )


@router.get("", response_model=ResponseSchema)
async def read_all_currencies_route(user=Depends(has_role(R.USER))) -> ResponseSchema:
    """
    Retrieve all currencies for the user.

    Args:
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing all currencies and a success message.
    """
    currencies = await CurrencyController.get_all_currencies(user.id)
    return ResponseSchema(
        data={"currencies": currencies},
        message="Currencies retrieved successfully",
    )


@router.put("/{currency_id}", response_model=ResponseSchema)
async def update_currency_route(
    currency_schema: CurrencyUpdateSchema,
    currency_id: str = Path(..., description="The ID of the currency to update"),
    user=Depends(has_role(R.USER)),
) -> ResponseSchema:
    """
    Update an existing currency.

    Args:
        currency_schema (CurrencyUpdateSchema): The schema containing updated currency details.
        currency_id (str): The ID of the currency to update.
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing the updated currency details and a success message.
    """
    updated_currency = await CurrencyController.update_currency(
        currency_id, currency_schema, user.id
    )
    return ResponseSchema(
        data={"currency": updated_currency},
        message="Currency updated successfully",
    )


@router.delete("/{currency_id}", response_model=ResponseSchema)
async def delete_currency_route(
    currency_id: str = Path(..., description="The ID of the currency to delete"),
    user=Depends(has_role(R.USER)),
) -> ResponseSchema:
    """
    Delete a currency by its ID.

    Args:
        currency_id (str): The ID of the currency to delete.
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing a success message.
    """
    success = await CurrencyController.delete_currency(currency_id, user.id)
    return ResponseSchema(message="Currency deleted successfully")
