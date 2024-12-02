from enum import Enum


class TransactionTypeEnum(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class RoleEnum(str, Enum):
    ADMIN = "admin"
    USER = "user"
