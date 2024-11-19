from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from fastapi import Query

from pydantic import (
    BaseModel,
    EmailStr,
    Extra,
    Field,
    field_validator,
    model_validator,
    root_validator,
)

MAX_INTEGER_PART = 10**10
MAX_DECIMAL_PART = 8


def check_value_precision(value: Decimal, field_name: str) -> Decimal:
    value = Decimal(str(value))
    if value.as_tuple().exponent < -MAX_DECIMAL_PART:
        raise ValueError(f"{field_name} cannot have more than eight decimal places")
    if value >= MAX_INTEGER_PART:
        raise ValueError(
            f"{field_name} cannot have an integer part greater than {MAX_INTEGER_PART}"
        )
    return value


class BaseModelConfigured(BaseModel):
    """
    Adds configuration to base model to use for all schemas.

    Configurations:
    forbid extra fields
    """

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


class CurrencyBalanceSchema(BaseModel):
    currency_id: str = Field(..., example="currency_id_123")
    balance: Decimal = Field(..., example=Decimal("100.50"))

    @field_validator("balance", mode="before")
    def validate_balance(cls, v):
        return check_value_precision(v, "Balance")


class WalletCreateSchema(BaseModel):
    name: str = Field(..., example="Savings Wallet")
    type: str = Field(..., choices=["fiat", "crypto"], example="fiat")
    currency_balances: List[CurrencyBalanceSchema] = Field(
        ...,
        example=[
            {"currency_id": "currency_id_123", "balance": Decimal("100.50")},
            {"currency_id": "currency_id_456", "balance": Decimal("200.75")},
        ],
    )


class WalletUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, example="Savings Wallet")
    type: Optional[str] = Field(None, choices=["fiat", "crypto"], example="fiat")
    currency_balances: Optional[List[CurrencyBalanceSchema]] = Field(
        None, example=[{"currency_id": "currency_id_123", "balance": Decimal("150.00")}]
    )


class CurrencyCreateSchema(BaseModel):
    code: str = Field(..., max_length=3, example="USD")
    name: str = Field(..., max_length=50, example="United States Dollar")
    symbol: str = Field(..., max_length=5, example="$")
    currency_type: str = Field(..., choices=["fiat", "crypto"], example="fiat")


class CurrencyUpdateSchema(BaseModel):
    code: Optional[str] = Field(None, max_length=3, example="USD")
    name: Optional[str] = Field(None, max_length=50, example="United States Dollar")
    symbol: Optional[str] = Field(None, max_length=5, example="$")
    currency_type: Optional[str] = Field(
        None, choices=["fiat", "crypto"], example="fiat"
    )


class CurrencyExchangeCreateSchema(BaseModel):
    from_currency_id: str = Field(..., example="currency_id_123")
    to_currency_id: str = Field(..., example="currency_id_456")
    rate: Decimal = Field(..., example=Decimal("0.85"))

    @field_validator("rate", mode="before")
    def validate_rate(cls, v):
        return check_value_precision(v, "Rate")

    date: Optional[datetime] = Field(
        default_factory=datetime.utcnow, example="2023-10-15T14:30:00Z"
    )


class CurrencyExchangeUpdateSchema(BaseModel):
    from_currency_id: Optional[str] = Field(None, example="currency_id_123")
    to_currency_id: Optional[str] = Field(None, example="currency_id_456")
    rate: Optional[Decimal] = Field(None, example=Decimal("0.85"))

    @field_validator("rate", mode="before")
    def validate_rate(cls, v):
        if v is not None:
            return check_value_precision(v, "Rate")
        return v

    date: Optional[datetime] = Field(None, example="2023-10-15T14:30:00Z")


class TransactionBaseSchema(BaseModel):
    from_wallet_id: Optional[str] = Field(None, example="from_wallet_id_123")
    to_wallet_id: Optional[str] = Field(None, example="to_wallet_id_123")
    category_id: Optional[str] = Field(None, example="category_id_123")
    currency_id: Optional[str] = Field(None, example="currency_id_123")
    type: Optional[str] = Field(
        None, choices=["income", "expense", "transfer"], example="transfer"
    )
    amount: Optional[Decimal] = Field(None, example=Decimal("50.75"))

    @field_validator("amount", mode="before")
    def validate_amount(cls, v):
        if v is not None:
            return check_value_precision(v, "Amount")
        return v

    date: Optional[datetime] = Field(None, example="2023-10-15T14:30:00Z")
    description: Optional[str] = Field(
        None, max_length=255, example="Transfer to savings"
    )

    @model_validator(mode="after")
    def validate_transaction(cls, values):
        transaction_type = values.type
        from_wallet_id = values.from_wallet_id
        to_wallet_id = values.to_wallet_id

        if transaction_type == "transfer":
            cls._validate_transfer_wallets(from_wallet_id, to_wallet_id)
        elif transaction_type == "expense":
            cls._validate_expense_wallet(from_wallet_id, to_wallet_id)
        elif transaction_type == "income":
            cls._validate_income_wallet(from_wallet_id, to_wallet_id)

        return values

    @staticmethod
    def _validate_transfer_wallets(
        from_wallet_id: Optional[str], to_wallet_id: Optional[str]
    ):
        if not from_wallet_id or not to_wallet_id:
            raise ValueError(
                "Both from_wallet_id and to_wallet_id are required for transfers."
            )
        if from_wallet_id == to_wallet_id:
            raise ValueError(
                "from_wallet_id and to_wallet_id cannot be the same for transfers."
            )

    @staticmethod
    def _validate_expense_wallet(
        from_wallet_id: Optional[str], to_wallet_id: Optional[str]
    ):
        if not from_wallet_id:
            raise ValueError("from_wallet_id is required for expenses.")
        if to_wallet_id:
            raise ValueError("to_wallet_id should not be provided for expenses.")

    @staticmethod
    def _validate_income_wallet(
        from_wallet_id: Optional[str], to_wallet_id: Optional[str]
    ):
        if not to_wallet_id:
            raise ValueError("to_wallet_id is required for incomes.")
        if from_wallet_id:
            raise ValueError("from_wallet_id should not be provided for incomes.")


class TransactionCreateSchema(TransactionBaseSchema):
    currency_id: str = Field(..., example="currency_id_123")
    type: str = Field(
        ..., choices=["income", "expense", "transfer"], example="transfer"
    )
    amount: Decimal = Field(..., example=Decimal("50.75"))

    @field_validator("amount", mode="before")
    def validate_amount(cls, v):
        return check_value_precision(v, "Amount")

    date: Optional[datetime] = Field(
        default_factory=datetime.utcnow, example="2023-10-15T14:30:00Z"
    )


class TransactionUpdateSchema(TransactionBaseSchema):
    pass


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class TransactionFilterParams(BaseModel):
    start_date: Optional[datetime] = Query(
        None,
        description="Start date for filtering in ISO format (e.g., 2023-10-15T14:30:00Z)",
    )
    end_date: Optional[datetime] = Query(
        None,
        description="End date for filtering in ISO format (e.g., 2023-10-15T14:30:00Z)",
    )
    transaction_type: Optional[TransactionType] = Query(
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

        if transaction_type == TransactionType.INCOME and from_wallet_id:
            raise ValueError(
                "For 'income' transactions, 'from_wallet_id' must not be provided."
            )
        elif transaction_type == TransactionType.EXPENSE and to_wallet_id:
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
        ..., choices=["income", "expense", "transfer"], example="transfer"
    )
    description: Optional[str] = Field(
        None, max_length=255, example="Necessary Grocery shoppings"
    )


class CategoryUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=50, example="Groceries")
    type: Optional[str] = Field(
        None, choices=["income", "expense", "transfer"], example="transfer"
    )
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
    value: Optional[Decimal] = Field(None, example=Decimal("350000.00"))

    @field_validator("value", mode="before")
    def validate_value(cls, v):
        if v is not None:
            return check_value_precision(v, "Value")
        return v

    updated_at: datetime = Field(
        default_factory=datetime.utcnow, example="2023-10-15T14:30:00Z"
    )


class Token(BaseModel):
    access_token: str
    token_type: str


class Role(Enum):
    ADMIN = "admin"
    USER = "user"
