from fastapi import APIRouter, Depends, Path

from app.api.controllers.auth_controller import has_role
from app.api.controllers.currency_exchange_controller import CurrencyExchangeController
from models.schemas import (
    CurrencyExchangeCreateSchema,
    CurrencyExchangeUpdateSchema,
    ErrorResponseModel,
    ResponseSchema,
)
from models.schemas import Role as R

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
    success = await CurrencyExchangeController.delete_currency_exchange(
        exchange_id, user.id
    )
    return ResponseSchema(message="Currency exchange deleted successfully")
