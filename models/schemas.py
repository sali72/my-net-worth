from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Extra, Field


class BaseModelConfigured(BaseModel):
    """
    Adds configuration to base model to use for all schemas.

    Configurations:
    forbid extra fields
    """

    class Config:
        extra = Extra.forbid


class ResponseSchema(BaseModelConfigured):
    message: str = Field(None, example=" task done successfully ")
    status: str = Field("success", example="success")
    data: dict = Field(None, example={"data": "Your requested data"})
    timestamp: datetime = Field(datetime.now(), example="2024-02-16T14:05:09.252968")


class UserSchema(BaseModelConfigured):
    username: str = Field(None, title="username")
    email: str = Field(None, title="email")
    password: str = Field(None, title="password")


class Token(BaseModel):
    access_token: str
    token_type: str


class Role(Enum):
    ADMIN = "admin"
    USER = "user"
