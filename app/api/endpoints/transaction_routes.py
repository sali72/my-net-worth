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
    response_model=ResponseSchema,
    responses={
        200: {"model": ResponseSchema, "description": "Successful Response"},
        400: {"model": ErrorResponseModel, "description": "Bad Request"},
    },
)
async def create_transaction_route(
    transaction_schema: TransactionCreateSchema, user=Depends(has_role(R.USER))
) -> ResponseSchema:
    """
    Create a new transaction and adjust wallet balances.

    Args:
        transaction_schema (TransactionCreateSchema): The schema containing transaction details.
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing the created transaction details and a success message.
    """
    transaction = await TransactionController.create_transaction(
        transaction_schema, user
    )
    await UserAppDataController.handle_transaction_user_app_data_wallet_value_update(
        transaction, user
    )

    message = "Transaction created successfully"
    data = {"result": transaction.to_dict()}
    return ResponseSchema(data=data, message=message)


@router.get("/filter", response_model=ResponseSchema)
async def filter_transactions_route(
    params: TransactionFilterParams = Query(...),
    user=Depends(has_role(R.USER)),
) -> ResponseSchema:
    """
    Retrieve transactions based on specified filters.

    Args:
        params (TransactionFilterParams): The filters to apply to the transaction retrieval.
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing the filtered transactions and a success message.
    """
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
    """
    Calculate transaction statistics for a user.

    Args:
        params (TransactionStatisticsParams): The parameters for calculating statistics.
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing transaction statistics and a success message.
    """
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
    """
    Retrieve a specific transaction by its ID.

    Args:
        transaction_id (str): The ID of the transaction to retrieve.
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing the transaction details and a success message.
    """
    transaction = await TransactionController.get_transaction(transaction_id, user.id)
    return ResponseSchema(
        data={"transaction": transaction}, message="Transaction retrieved successfully"
    )


@router.get("", response_model=ResponseSchema)
async def read_all_transactions_route(user=Depends(has_role(R.USER))) -> ResponseSchema:
    """
    Retrieve all transactions for the user.

    Args:
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing all transactions and a success message.
    """
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
    """
    Update an existing transaction.

    Args:
        transaction_schema (TransactionUpdateSchema): The schema containing updated transaction details.
        transaction_id (str): The ID of the transaction to update.
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing the updated transaction details and a success message.
    """
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
    """
    Delete a transaction by its ID.

    Args:
        transaction_id (str): The ID of the transaction to delete.
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing a success message.
    """
    transaction = await TransactionController.delete_transaction(
        transaction_id, user.id
    )

    transaction.amount = -transaction.amount
    await UserAppDataController.handle_transaction_user_app_data_wallet_value_update(
        transaction, user
    )
    return ResponseSchema(message="Transaction deleted successfully")
