from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from fastapi import Query
from pydantic import BaseModel, EmailStr, Extra, Field, field_validator, model_validator

from models.enums import TransactionTypeEnum
from models.enums import TransactionTypeEnum as T
from models.models import CurrencyExchange, Transaction
from models.validator_utilities import check_value_precision
from models.validators import (
    CurrencyExchangeValidator,
    CurrencyValidator,
    TransactionValidator,
)


class BaseModelConfigured(BaseModel):
    class Config:
        extra = Extra.forbid


class ResponseSchema(BaseModelConfigured):
    message: str = Field(None, example="Task was done successfully ")
    data: dict = Field(None, example={"data": "Your requested data"})
    timestamp: datetime = Field(datetime.now(), example="2024-02-16T14:05:09.252968")


class ErrorResponseModel(BaseModelConfigured):
    exception_name: str = Field(None, example="ExceptionName")
    detail: str = Field(None, example="There was a problem serving your request ")


class UserSchema(BaseModel):
    username: str = Field(None, example="johndoe")
    email: EmailStr = Field(None, example="johndoe@example.com")
    password: str = Field(None, example="strongpassword123")
    base_currency_id: str = Field(..., example="currency_id_123")


class UpdateUserSchema(BaseModel):
    name: str = Field(None, example="John Doe")
    username: str = Field(None, example="newusername")
    email: EmailStr = Field(None, example="newemail@example.com")
    password: str = Field(None, example="newstrongpassword123")


class BalanceSchema(BaseModel):
    currency_id: str = Field(..., example="currency_id_123")
    amount: Decimal = Field(..., example=Decimal("100.50"))

    @field_validator("amount", mode="before")
    def validate_balance(cls, v):
        return check_value_precision(v, "amount")


class WalletCreateSchema(BaseModel):
    name: str = Field(..., example="Savings Wallet")
    type: str = Field(..., choices=["fiat", "crypto"], example="fiat")
    balances_ids: List[BalanceSchema] = Field(
        ...,
        example=[
            {"currency_id": "currency_id_123", "amount": Decimal("100.50")},
            {"currency_id": "currency_id_456", "amount": Decimal("200.75")},
        ],
    )


class WalletUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, example="Savings Wallet")
    balances_ids: Optional[List[BalanceSchema]] = Field(
        None, example=[{"currency_id": "currency_id_123", "amount": Decimal("150.00")}]
    )


class CurrencyCreateSchema(BaseModel):
    code: str = Field(..., max_length=10, example="USD")
    name: str = Field(..., max_length=50, example="United States Dollar")
    symbol: str = Field(..., max_length=5, example="$")
    currency_type: str = Field(..., choices=["fiat", "crypto"], example="fiat")

    @model_validator(mode="after")
    def validate_currency(cls, values):
        code = values.code
        currency_type = values.currency_type

        CurrencyValidator.validate_code_length(code, currency_type)
        return values


class CurrencyUpdateSchema(BaseModel):
    code: Optional[str] = Field(None, max_length=10, example="USD")
    name: Optional[str] = Field(None, max_length=50, example="United States Dollar")
    symbol: Optional[str] = Field(None, max_length=5, example="$")
    currency_type: Optional[str] = Field(
        None, choices=["fiat", "crypto"], example="fiat"
    )

    @model_validator(mode="after")
    def validate_currency(cls, values):
        code = values.code
        currency_type = values.currency_type

        if code and currency_type:
            # Validate code length using the validator
            CurrencyValidator.validate_code_length(code, currency_type)
        return values


class CurrencyExchangeCreateSchema(BaseModel):
    from_currency_id: str = Field(..., example="currency_id_123")
    to_currency_id: str = Field(..., example="currency_id_456")
    rate: Decimal = Field(..., example="0.85")
    date: Optional[datetime] = Field(
        default_factory=datetime.utcnow, example="2023-10-15T14:30:00Z"
    )

    @field_validator(CurrencyExchange.rate.name, mode="before")
    def validate_rate(cls, value):
        return check_value_precision(value, "Rate")

    @model_validator(mode="after")
    def validate_transaction(cls, values):
        exchange = CurrencyExchange(**values.model_dump())
        CurrencyExchangeValidator.validate_input_currency_ids(exchange)
        return values


class CurrencyExchangeUpdateSchema(BaseModel):
    from_currency_id: Optional[str] = Field(None, example="currency_id_123")
    to_currency_id: Optional[str] = Field(None, example="currency_id_456")
    rate: Optional[Decimal] = Field(None, example="0.85")
    date: Optional[datetime] = Field(None, example="2023-10-15T14:30:00Z")

    @field_validator(CurrencyExchange.rate.name, mode="before")
    def validate_rate(cls, value):
        if value is not None:
            return check_value_precision(value, "Rate")
        return value


class TransactionBaseSchema(BaseModel):
    category_id: Optional[str] = Field(None, example="category_id_123")
    amount: Optional[Decimal] = Field(None, example="50.75")
    date: Optional[datetime] = Field(None, example="2023-10-15T14:30:00Z")
    description: Optional[str] = Field(
        None, max_length=255, example="Transfer to savings"
    )

    @field_validator("amount", mode="before")
    def validate_amount(cls, v):
        if v is not None:
            return check_value_precision(v, "Amount")
        return v


class TransactionCreateSchema(TransactionBaseSchema):
    from_wallet_id: Optional[str] = Field(None, example="from_wallet_id_123")
    to_wallet_id: Optional[str] = Field(None, example="to_wallet_id_123")
    currency_id: str = Field(..., example="currency_id_123")
    type: str = Field(
        ...,
        choices=[T.INCOME.value, T.EXPENSE.value, T.TRANSFER.value],
        example=T.TRANSFER.value,
    )
    amount: Decimal = Field(..., example="50.75")

    @model_validator(mode="after")
    def validate_transaction(cls, values):
        transaction = Transaction(**values.model_dump())
        TransactionValidator.validate(transaction)
        return values


class TransactionUpdateSchema(TransactionBaseSchema):
    pass


class TransactionFilterParams(BaseModel):
    start_date: Optional[datetime] = Query(
        None,
        description="Start date for filtering in ISO format (e.g., 2023-10-15T14:30:00Z)",
    )
    end_date: Optional[datetime] = Query(
        None,
        description="End date for filtering in ISO format (e.g., 2023-10-15T14:30:00Z)",
    )
    transaction_type: Optional[TransactionTypeEnum] = Query(
        None, description="Type of transaction"
    )
    category_id: Optional[str] = Query(
        None, description="Category ID for filtering transactions"
    )
    from_wallet_id: Optional[str] = Query(
        None, description="ID of the wallet from which the transaction originates"
    )
    to_wallet_id: Optional[str] = Query(
        None, description="ID of the wallet to which the transaction is directed"
    )

    @model_validator(mode="after")
    def validate_wallet_ids(cls, values):
        transaction_type = values.transaction_type
        from_wallet_id = values.from_wallet_id
        to_wallet_id = values.to_wallet_id

        if transaction_type == TransactionTypeEnum.INCOME and from_wallet_id:
            raise ValueError(
                "For 'income' transactions, 'from_wallet_id' must not be provided."
            )
        elif transaction_type == TransactionTypeEnum.EXPENSE and to_wallet_id:
            raise ValueError(
                "For 'expense' transactions, 'to_wallet_id' must not be provided."
            )

        return values


class TransactionStatisticsParams(BaseModel):
    start_date: Optional[datetime] = Query(
        None,
        description="Start date for filtering in ISO format (e.g., 2023-10-15T14:30:00Z)",
    )
    end_date: Optional[datetime] = Query(
        None,
        description="End date for filtering in ISO format (e.g., 2023-10-15T14:30:00Z)",
    )


class CategoryCreateSchema(BaseModel):
    name: str = Field(..., max_length=50, example="Groceries")
    type: str = Field(
        ...,
        choices=[T.INCOME.value, T.EXPENSE.value, T.TRANSFER.value],
        example=T.EXPENSE.value,
    )
    description: Optional[str] = Field(
        None, max_length=255, example="Necessary Grocery shoppings"
    )


class CategoryUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=50, example="Groceries")
    description: Optional[str] = Field(
        None, max_length=255, example="Necessary Grocery shoppings"
    )


class AssetTypeCreateSchema(BaseModel):
    name: str = Field(..., max_length=50, example="Real Estate")
    description: Optional[str] = Field(None, max_length=255, example="My properties")


class AssetTypeUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=50, example="Real Estate")
    description: Optional[str] = Field(None, max_length=255, example="My properties")


class AssetCreateSchema(BaseModel):
    asset_type_id: Optional[str] = Field(None, example="asset_type_id_123")
    currency_id: str = Field(..., example="currency_id_123")
    name: str = Field(..., max_length=50, example="Family Home")
    description: Optional[str] = Field(
        None, max_length=255, example="A beautiful house in the suburbs"
    )
    value: Decimal = Field(..., example=Decimal("350000.00"))

    @field_validator("value", mode="before")
    def validate_value(cls, v):
        return check_value_precision(v, "Value")

    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow, example="2023-10-15T14:30:00Z"
    )


class AssetUpdateSchema(BaseModel):
    asset_type_id: Optional[str] = Field(None, example="asset_type_id_123")
    currency_id: Optional[str] = Field(None, example="currency_id_123")
    name: Optional[str] = Field(None, max_length=50, example="Family Home")
    description: Optional[str] = Field(
        None, max_length=255, example="A beautiful house in the suburbs"
    )
    value: Optional[Decimal] = Field(None, example="350000.00")

    @field_validator("value", mode="before")
    def validate_value(cls, v):
        if v is not None:
            return check_value_precision(v, "Value")
        return v

    updated_at: datetime = Field(
        default_factory=datetime.utcnow, example="2023-10-15T14:30:00Z"
    )


class AssetFilterSchema(BaseModel):
    name: Optional[str] = Query(
        None,
        description="Search by asset name",
    )
    asset_type_id: Optional[str] = Query(
        None,
        description="Filter by asset type ID",
    )
    currency_id: Optional[str] = Query(
        None,
        description="Filter by currency ID",
    )
    created_at_start: Optional[datetime] = Query(
        None,
        description="Start date for created_at filter in ISO format like: 2023-10-01T00:00:00Z",
    )
    created_at_end: Optional[datetime] = Query(
        None,
        description="End date for created_at filter in ISO format like: 2023-10-31T23:59:59Z",
    )
    updated_at_start: Optional[datetime] = Query(
        None,
        description="Start date for updated_at filter in ISO format like: 2023-10-01T00:00:00Z",
    )
    updated_at_end: Optional[datetime] = Query(
        None,
        description="End date for updated_at filter in ISO format like: 2023-10-31T23:59:59Z",
    )

    @field_validator("name")
    def name_min_length(cls, v):
        if v is not None and len(v) < 3:
            raise ValueError("Name must be at least 3 characters long")
        return v


class Token(BaseModel):
    access_token: str
    token_type: str
