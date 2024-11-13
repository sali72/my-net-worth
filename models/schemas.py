from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Extra, Field, model_validator


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


class CurrencyBalanceSchema(BaseModel):
    currency_id: str = Field(..., example="currency_id_123")
    balance: float = Field(..., example=100.50)


class WalletCreateSchema(BaseModel):
    name: str = Field(..., example="Savings Wallet")
    type: str = Field(..., choices=["fiat", "crypto"], example="fiat")
    currency_balances: List[CurrencyBalanceSchema] = Field(
        ...,
        example=[
            {"currency_id": "currency_id_123", "balance": 100.50},
            {"currency_id": "currency_id_456", "balance": 200.75},
        ],
    )


class WalletUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, example="Savings Wallet")
    type: Optional[str] = Field(None, choices=["fiat", "crypto"], example="fiat")
    currency_balances: Optional[List[CurrencyBalanceSchema]] = Field(
        None, example=[{"currency_id": "currency_id_123", "balance": 150.00}]
    )


class CurrencySchema(BaseModel):
    code: str = Field(..., max_length=10, example="USD")
    name: str = Field(..., max_length=50, example="United States Dollar")
    symbol: str = Field(..., max_length=5, example="$")
    is_predefined: bool = Field(False, example=True)
    is_base_currency: bool = Field(False, example=True)
    currency_type: str = Field(..., choices=["fiat", "crypto"], example="fiat")


class CurrencyExchangeSchema(BaseModel):
    from_currency_id: str = Field(None, example="USD")
    to_currency_id: str = Field(None, example="EUR")
    rate: float = Field(None, example=0.85)


class TransactionBaseSchema(BaseModel):
    from_wallet_id: Optional[str] = Field(None, example="from_wallet_id_123")
    to_wallet_id: Optional[str] = Field(None, example="to_wallet_id_123")
    category_id: Optional[str] = Field(None, example="category_id_123")
    currency_id: Optional[str] = Field(None, example="currency_id_123")
    type: Optional[str] = Field(
        None, choices=["income", "expense", "transfer"], example="transfer"
    )
    amount: Optional[float] = Field(None, example=50.75)
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
    category_id: str = Field(..., example="category_id_123")
    currency_id: str = Field(..., example="currency_id_123")
    type: str = Field(
        ..., choices=["income", "expense", "transfer"], example="transfer"
    )
    amount: float = Field(..., example=50.75)
    date: Optional[datetime] = Field(
        default_factory=datetime.utcnow, example="2023-10-15T14:30:00Z"
    )


class TransactionUpdateSchema(TransactionBaseSchema):
    pass


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
    asset_type: Optional[str] = Field(None, example="asset_type_id_123")
    name: str = Field(..., max_length=50, example="Family Home")
    description: Optional[str] = Field(
        None, max_length=255, example="A beautiful house in the suburbs"
    )
    value: float = Field(..., example=350000.00)
    created_at: datetime = Field(
        default_factory=datetime.utcnow, example="2023-10-15T14:30:00Z"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, example="2023-10-15T14:30:00Z"
    )


class AssetUpdateSchema(BaseModel):
    asset_type: Optional[str] = Field(None, example="asset_type_id_123")
    name: Optional[str] = Field(None, max_length=50, example="Family Home")
    description: Optional[str] = Field(
        None, max_length=255, example="A beautiful house in the suburbs"
    )
    value: Optional[float] = Field(None, example=350000.00)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, example="2023-10-15T14:30:00Z"
    )


class Token(BaseModel):
    access_token: str
    token_type: str


class Role(Enum):
    ADMIN = "admin"
    USER = "user"
