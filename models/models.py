from datetime import datetime

from mongoengine import (
    BooleanField,
    DateTimeField,
    DecimalField,
    Document,
    EmailField,
    FloatField,
    IntField,
    ReferenceField,
    StringField,
)


class User(Document):
    # user_id = StringField(primary_key=True)
    name = StringField(required=False, max_length=50)
    username = StringField(required=True, unique=True)
    # email = EmailField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    hashed_password = StringField(required=True)
    role = StringField(required=True, choices=["user", "admin"])
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)


class Wallet(Document):
    wallet_id = StringField(primary_key=True)
    user_id = ReferenceField(User, required=True)
    currency_id = ReferenceField("Currency", required=True)
    name = StringField(required=True, max_length=50)
    balance = DecimalField(required=True, precision=2)
    is_predefined = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)


class Currency(Document):
    currency_id = StringField(primary_key=True)
    code = StringField(required=True, max_length=3, unique=True)
    name = StringField(required=True, max_length=50)
    symbol = StringField(required=True, max_length=5)
    is_predefined = BooleanField(default=False)


class CurrencyExchange(Document):
    exchange_id = StringField(primary_key=True)
    from_currency_id = ReferenceField(Currency, required=True)
    to_currency_id = ReferenceField(Currency, required=True)
    rate = FloatField(required=True)
    date = DateTimeField(default=datetime.utcnow)


class Transaction(Document):
    transaction_id = StringField(primary_key=True)
    user_id = ReferenceField(User, required=True)
    wallet_id = ReferenceField(Wallet, required=True)
    category_id = ReferenceField("Category", required=True)
    type = StringField(required=True, choices=["income", "expense", "transfer"])
    amount = DecimalField(required=True, precision=2)
    date = DateTimeField(default=datetime.utcnow)
    description = StringField(max_length=255)


class Category(Document):
    category_id = StringField(primary_key=True)
    name = StringField(required=True, max_length=50)
    is_predefined = BooleanField(default=False)
