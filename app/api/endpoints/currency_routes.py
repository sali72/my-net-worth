from fastapi import APIRouter, Depends, Path

from app.api.controllers.auth_controller import has_role
from app.api.controllers.currency_controller import CurrencyController
from models.schemas import (
    CurrencyCreateSchema,
    CurrencyUpdateSchema,
    ErrorResponseModel,
    ResponseSchema,
)
from models.schemas import Role as R

router = APIRouter(prefix="/currencies", tags=["Currency"])


@router.post(
    "",
    responses={
        200: {"model": ResponseSchema, "description": "Successful Response"},
        400: {"model": ErrorResponseModel, "description": "Bad Request"},
    },
)
async def create_currency_route(
    currency_schema: CurrencyCreateSchema, user=Depends(has_role(R.USER))
):
    currency_id = await CurrencyController.create_currency(currency_schema, user)
    message = "Currency created successfully"
    data = {"id": currency_id}
    return ResponseSchema(data=data, message=message)


@router.get("/{currency_id}", response_model=ResponseSchema)
async def read_currency_route(
    currency_id: str = Path(..., description="The ID of the currency to retrieve"),
    user=Depends(has_role(R.USER)),
):
    currency = await CurrencyController.get_currency(currency_id, user.id)
    return ResponseSchema(
        data={"currency": currency}, message="Currency retrieved successfully"
    )


@router.get("", response_model=ResponseSchema)
async def read_all_currencies_route(user=Depends(has_role(R.USER))):
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
):
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
):
    success = await CurrencyController.delete_currency(currency_id, user.id)
    return ResponseSchema(message="Currency deleted successfully")


@router.post("/set-base/{currency_id}", response_model=ResponseSchema)
async def set_base_currency_by_id_route(
    currency_id: str = Path(..., description="The ID of the currency to set as base"),
    user=Depends(has_role(R.USER)),
):
    result = await CurrencyController.set_base_currency_by_id(user.id, currency_id)
    return ResponseSchema(
        data=result,
        message="Base currency set successfully",
    )
