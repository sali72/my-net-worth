from fastapi import APIRouter, Depends, Path
from models.schemas import (
    ResponseSchema,
    ErrorResponseModel,
    TransactionCreateSchema,
    TransactionUpdateSchema,
)
from models.schemas import Role as R
from app.api.controllers.auth_controller import has_role
from app.api.controllers.transaction_controller import TransactionController

router = APIRouter(prefix="/transactions", tags=["Transaction"])


@router.post(
    "",
    responses={
        200: {"model": ResponseSchema, "description": "Successful Response"},
        400: {"model": ErrorResponseModel, "description": "Bad Request"},
    },
)
async def create_transaction_route(
    transaction_schema: TransactionCreateSchema, user=Depends(has_role(R.USER))
):
    transaction_id = await TransactionController.create_transaction(
        transaction_schema, user
    )
    message = "Transaction created successfully"
    data = {"id": transaction_id}
    return ResponseSchema(data=data, message=message)


@router.get("/{transaction_id}", response_model=ResponseSchema)
async def read_transaction_route(
    transaction_id: str = Path(
        ..., description="The ID of the transaction to retrieve"
    ),
    user=Depends(has_role(R.USER)),
):
    transaction = await TransactionController.get_transaction(transaction_id, user.id)
    return ResponseSchema(
        data={"transaction": transaction}, message="Transaction retrieved successfully"
    )


@router.get("", response_model=ResponseSchema)
async def read_all_transactions_route(user=Depends(has_role(R.USER))):
    transactions = await TransactionController.get_all_transactions(user.id)
    return ResponseSchema(
        data={"transactions": transactions},
        message="Transactions retrieved successfully",
    )


@router.put("/{transaction_id}", response_model=ResponseSchema)
async def update_transaction_route(
    transaction_schema: TransactionUpdateSchema,
    transaction_id: str = Path(..., description="The ID of the transaction to update"),
    user=Depends(has_role(R.USER)),
):
    updated_transaction = await TransactionController.update_transaction(
        transaction_id, transaction_schema, user.id
    )
    return ResponseSchema(
        data={"transaction": updated_transaction},
        message="Transaction updated successfully",
    )


@router.delete("/{transaction_id}", response_model=ResponseSchema)
async def delete_transaction_route(
    transaction_id: str = Path(..., description="The ID of the transaction to delete"),
    user=Depends(has_role(R.USER)),
):
    success = await TransactionController.delete_transaction(transaction_id, user.id)
    return ResponseSchema(message="Transaction deleted successfully")
