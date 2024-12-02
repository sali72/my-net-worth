from fastapi import APIRouter, Depends, Path, Query

from app.api.controllers.auth_controller import has_role
from app.api.controllers.transaction_controller import TransactionController
from app.api.controllers.user_app_data_controller import UserAppDataController
from app.api.controllers.wallet_controller import WalletController
from models.enums import RoleEnum as R
from models.schemas import (
    ErrorResponseModel,
    ResponseSchema,
    TransactionCreateSchema,
    TransactionFilterParams,
    TransactionStatisticsParams,
    TransactionUpdateSchema,
)

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
) -> ResponseSchema:
    transaction = await TransactionController.create_transaction(
        transaction_schema, user
    )
    await UserAppDataController.add_value_to_user_app_data_wallets_value(
        user, transaction.amount, transaction.currency_id.id
    )

    message = "Transaction created successfully"
    data = {"result": transaction.to_dict()}
    return ResponseSchema(data=data, message=message)


@router.get("/filter", response_model=ResponseSchema)
async def filter_transactions_route(
    params: TransactionFilterParams = Query(...),
    user=Depends(has_role(R.USER)),
) -> ResponseSchema:
    transactions = await TransactionController.filter_transactions(
        user.id,
        params.start_date,
        params.end_date,
        params.transaction_type,
        params.category_id,
        params.from_wallet_id,
        params.to_wallet_id,
    )
    return ResponseSchema(
        data={"transactions": transactions},
        message="Filtered transactions retrieved successfully",
    )


@router.get("/statistics", response_model=ResponseSchema)
async def transaction_statistics_route(
    params: TransactionStatisticsParams = Query(...),
    user=Depends(has_role(R.USER)),
) -> ResponseSchema:
    statistics = await TransactionController.calculate_statistics(
        user.id, params.start_date, params.end_date
    )
    return ResponseSchema(
        data={"statistics": statistics},
        message="Transaction statistics retrieved successfully",
    )


@router.get("/{transaction_id}", response_model=ResponseSchema)
async def read_transaction_route(
    transaction_id: str = Path(
        ..., description="The ID of the transaction to retrieve"
    ),
    user=Depends(has_role(R.USER)),
) -> ResponseSchema:
    transaction = await TransactionController.get_transaction(transaction_id, user.id)
    return ResponseSchema(
        data={"transaction": transaction}, message="Transaction retrieved successfully"
    )


@router.get("", response_model=ResponseSchema)
async def read_all_transactions_route(user=Depends(has_role(R.USER))) -> ResponseSchema:
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
) -> ResponseSchema:
    updated_transaction = await TransactionController.update_transaction(
        transaction_id, transaction_schema, user.id
    )
    await WalletController.calculate_total_wallet_value(user)

    return ResponseSchema(
        data={"transaction": updated_transaction},
        message="Transaction updated successfully",
    )


@router.delete("/{transaction_id}", response_model=ResponseSchema)
async def delete_transaction_route(
    transaction_id: str = Path(..., description="The ID of the transaction to delete"),
    user=Depends(has_role(R.USER)),
) -> ResponseSchema:
    transaction = await TransactionController.delete_transaction(
        transaction_id, user.id
    )

    await UserAppDataController.reduce_value_from_user_app_data_wallets_value(
        user, transaction.amount, transaction.currency_id.id
    )
    return ResponseSchema(message="Transaction deleted successfully")
