from fastapi import APIRouter, Depends, Path

from app.api.controllers.auth_controller import has_role
from app.api.controllers.currency_exchange_controller import CurrencyExchangeController
from models.enums import RoleEnum as R
from models.schemas import (
    CurrencyExchangeCreateSchema,
    CurrencyExchangeUpdateSchema,
    ErrorResponseModel,
    ResponseSchema,
)

router = APIRouter(prefix="/currency-exchanges", tags=["CurrencyExchange"])


@router.post(
    "",
    response_model=ResponseSchema,
    responses={
        200: {"model": ResponseSchema, "description": "Successful Response"},
        400: {"model": ErrorResponseModel, "description": "Bad Request"},
    },
)
async def create_currency_exchange_route(
    exchange_schema: CurrencyExchangeCreateSchema, user=Depends(has_role(R.USER))
) -> ResponseSchema:
    """
    Create a new currency exchange entry.

    Args:
        exchange_schema (CurrencyExchangeCreateSchema): The schema containing details of the currency exchange to create.
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing the created currency exchange's ID and a success message.
    """
    exchange_id = await CurrencyExchangeController.create_currency_exchange(
        exchange_schema, user
    )
    message = "Currency exchange created successfully"
    data = {"id": exchange_id}
    return ResponseSchema(data=data, message=message)


@router.get("/{exchange_id}", response_model=ResponseSchema)
async def read_currency_exchange_route(
    exchange_id: str = Path(
        ..., description="The ID of the currency exchange to retrieve"
    ),
    user=Depends(has_role(R.USER)),
) -> ResponseSchema:
    """
    Retrieve a specific currency exchange by its ID.

    Args:
        exchange_id (str): The ID of the currency exchange to retrieve.
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing the currency exchange details and a success message.
    """
    exchange = await CurrencyExchangeController.get_currency_exchange(
        exchange_id, user.id
    )
    return ResponseSchema(
        data={"currency_exchange": exchange},
        message="Currency exchange retrieved successfully",
    )


@router.get("", response_model=ResponseSchema)
async def read_all_currency_exchanges_route(
    user=Depends(has_role(R.USER)),
) -> ResponseSchema:
    """
    Retrieve all currency exchanges for the user.

    Args:
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing all currency exchanges and a success message.
    """
    exchanges = await CurrencyExchangeController.get_all_currency_exchanges(user.id)
    return ResponseSchema(
        data={"currency_exchanges": exchanges},
        message="Currency exchanges retrieved successfully",
    )


@router.put("/{exchange_id}", response_model=ResponseSchema)
async def update_currency_exchange_route(
    exchange_schema: CurrencyExchangeUpdateSchema,
    exchange_id: str = Path(
        ..., description="The ID of the currency exchange to update"
    ),
    user=Depends(has_role(R.USER)),
) -> ResponseSchema:
    """
    Update an existing currency exchange.

    Args:
        exchange_schema (CurrencyExchangeUpdateSchema): The schema containing updated currency exchange details.
        exchange_id (str): The ID of the currency exchange to update.
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing the updated currency exchange details and a success message.
    """
    updated_exchange = await CurrencyExchangeController.update_currency_exchange(
        exchange_id, exchange_schema, user.id
    )
    return ResponseSchema(
        data={"currency_exchange": updated_exchange},
        message="Currency exchange updated successfully",
    )


@router.delete("/{exchange_id}", response_model=ResponseSchema)
async def delete_currency_exchange_route(
    exchange_id: str = Path(
        ..., description="The ID of the currency exchange to delete"
    ),
    user=Depends(has_role(R.USER)),
) -> ResponseSchema:
    """
    Delete a currency exchange by its ID.

    Args:
        exchange_id (str): The ID of the currency exchange to delete.
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing a success message.
    """
    success = await CurrencyExchangeController.delete_currency_exchange(
        exchange_id, user.id
    )
    return ResponseSchema(message="Currency exchange deleted successfully")
