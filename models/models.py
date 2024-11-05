from datetime import datetime

from mongoengine import (
    BooleanField,
    DateTimeField,
    DecimalField,
    Document,
    ListField,
    ReferenceField,
    StringField,
    ValidationError,
    EmailField,
)


class User(Document):
    name = StringField(required=False, max_length=50)
    username = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    hashed_password = StringField(required=True)
    role = StringField(required=True, choices=["user", "admin"])
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)


class Currency(Document):
    currency_id = StringField(primary_key=True)
    code = StringField(required=True, max_length=3, unique=True)
    name = StringField(required=True, max_length=50)
    symbol = StringField(required=True, max_length=5)
    is_predefined = BooleanField(default=False)
    is_base_currency = BooleanField(default=False)
    currency_type = StringField(required=True, choices=["fiat", "crypto"])

    def save(self, *args, **kwargs):
        if self.is_base_currency:
            if Currency.objects(is_base_currency=True).count() > 0:
                raise ValidationError("Only one currency can be the base currency.")
        return super(Currency, self).save(*args, **kwargs)


class Wallet(Document):
    user_id = ReferenceField(User, required=True)
    name = StringField(unique=True, required=True, max_length=50)
    type = StringField(required=True, choices=["fiat", "crypto"])
    currency_ids = ListField(ReferenceField(Currency), required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)


class CurrencyExchange(Document):
    from_currency_id = ReferenceField(Currency, required=True)
    to_currency_id = ReferenceField(Currency, required=True)
    rate = DecimalField(required=True)
    date = DateTimeField(default=datetime.utcnow)


class Transaction(Document):
    user_id = ReferenceField(User, required=True)
    wallet_id = ReferenceField(Wallet, required=True)
    category_id = ReferenceField("Category", required=True)
    type = StringField(required=True, choices=["income", "expense", "transfer"])
    amount = DecimalField(required=True, precision=2)
    date = DateTimeField(default=datetime.utcnow)
    description = StringField(max_length=255)


class Category(Document):
    name = StringField(required=True, max_length=50)
    is_predefined = BooleanField(default=False)


class AssetType(Document):
    name = StringField(required=True, unique=True, max_length=50)
    is_predefined = BooleanField(default=False)


class Asset(Document):
    asset_type = ReferenceField(AssetType, required=True)
    name = StringField(required=True, max_length=50)
    description = StringField(required=False, max_length=255)
    value = DecimalField(required=True, precision=10)
    user_id = ReferenceField(User, required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
