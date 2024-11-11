from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Extra, Field
from typing import Optional, List


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
    email: str = Field(None, example="johndoe@example.com")
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


class TransactionCreateSchema(BaseModel):
    wallet_id: str = Field(..., example="60d21b4667d0d8992e610c85")
    category_id: str = Field(..., example="60d21b4967d0d8992e610c86")
    type: str = Field(..., choices=["income", "expense", "transfer"], example="expense")
    amount: float = Field(..., example=50.75)
    date: Optional[datetime] = Field(
        default_factory=datetime.utcnow, example="2023-10-15T14:30:00Z"
    )
    description: Optional[str] = Field(
        None, max_length=255, example="Weekly grocery shopping"
    )


class TransactionUpdateSchema(BaseModel):
    wallet_id: Optional[str] = Field(None, example="60d21b4667d0d8992e610c85")
    category_id: Optional[str] = Field(None, example="60d21b4967d0d8992e610c86")
    type: Optional[str] = Field(
        None, choices=["income", "expense", "transfer"], example="expense"
    )
    amount: Optional[float] = Field(None, example=50.75)
    date: Optional[datetime] = Field(None, example="2023-10-15T14:30:00Z")
    description: Optional[str] = Field(
        None, max_length=255, example="Weekly grocery shopping"
    )


class CategorySchema(BaseModel):
    name: str = Field(..., max_length=50, example="Groceries")
    is_predefined: bool = Field(False, example=True)


class AssetTypeSchema(BaseModel):
    name: str = Field(..., max_length=50, example="Real Estate")
    is_predefined: bool = Field(False, example=True)


class AssetSchema(BaseModel):
    asset_type: str = Field(..., example="Real Estate")
    name: str = Field(..., max_length=50, example="Family Home")
    description: Optional[str] = Field(
        None, max_length=255, example="A beautiful house in the suburbs"
    )
    value: float = Field(..., example=350000.00)


class Token(BaseModel):
    access_token: str
    token_type: str


class Role(Enum):
    ADMIN = "admin"
    USER = "user"
