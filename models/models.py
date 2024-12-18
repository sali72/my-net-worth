from datetime import datetime, timezone
from decimal import Decimal

from bson import ObjectId
from mongoengine import (
    CASCADE,
    DENY,
    NULLIFY,
    PULL,
    BooleanField,
    DateTimeField,
    DecimalField,
    Document,
    EmailField,
    LazyReferenceField,
    ListField,
    ReferenceField,
    StringField,
    ValidationError,
    signals,
)

from models.enums import TransactionTypeEnum as T
from models.validators import (
    CurrencyExchangeValidator,
    CurrencyValidator,
    PredefinedEntityValidator,
    TransactionValidator,
)

PRECISION_LIMIT_IN_DB = 10


class BaseDocument(Document):
    meta = {"abstract": True}

    def to_dict(self) -> dict:
        # Convert the document to a dictionary
        doc_dict = self.to_mongo().to_dict()

        # Process each key-value pair in the dictionary
        for key, value in doc_dict.items():
            doc_dict[key] = self._convert_value(value)

        return doc_dict

    def _convert_value(self, value) -> object:
        """Convert ObjectId or list of ObjectIds/dicts to strings."""
        if isinstance(value, ObjectId):
            return self._convert_objectid_to_str(value)
        elif isinstance(value, list):
            return self._convert_list(value)
        return value

    def _convert_objectid_to_str(self, object_id: ObjectId) -> str:
        """Convert an ObjectId to a string."""
        return str(object_id)

    def _convert_list(self, value_list: list) -> list:
        """Convert a list of ObjectIds or dicts with ObjectIds to strings."""
        if all(isinstance(item, ObjectId) for item in value_list):
            return [self._convert_objectid_to_str(item) for item in value_list]
        elif all(isinstance(item, dict) for item in value_list):
            return [self._convert_dict(item) for item in value_list]
        return value_list

    def _convert_dict(self, value_dict: dict) -> dict:
        """Convert ObjectId values in a dictionary to strings."""
        for sub_key, sub_value in value_dict.items():
            if isinstance(sub_value, ObjectId):
                value_dict[sub_key] = self._convert_objectid_to_str(sub_value)
        return value_dict


class TimestampMixin:
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))


class User(BaseDocument, TimestampMixin):
    name = StringField(required=False, max_length=50)
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    hashed_password = StringField(required=True)
    role = StringField(required=True, choices=["user", "admin"])


class PredefinedEntity(BaseDocument):
    user_id = ReferenceField("User", required=False, reverse_delete_rule=CASCADE)
    name = StringField(required=True, max_length=50)
    is_predefined = BooleanField(default=False)
    meta = {"abstract": True}

    def clean(self) -> None:
        super().clean()
        PredefinedEntityValidator.validate(self)


class Currency(PredefinedEntity, TimestampMixin):
    code = StringField(required=True, max_length=10)
    symbol = StringField(required=True, max_length=5)
    currency_type = StringField(required=True, choices=["fiat", "crypto"])
    meta = {
        "indexes": [
            {"fields": ("user_id", "code"), "unique": True},
            {"fields": ("user_id", "name"), "unique": True},
            {"fields": ("user_id", "symbol"), "unique": True},
        ]
    }

    def clean(self) -> None:
        super().clean()
        CurrencyValidator.validate_code_length(self.code, self.currency_type)


class UserAppData(BaseDocument, TimestampMixin):
    user_id = ReferenceField(
        "User", required=True, unique=True, reverse_delete_rule=CASCADE
    )
    base_currency_id = LazyReferenceField(
        "Currency", required=True, reverse_delete_rule=DENY
    )
    net_worth = DecimalField(default=0, min_value=0, precision=PRECISION_LIMIT_IN_DB)
    assets_value = DecimalField(default=0, min_value=0, precision=PRECISION_LIMIT_IN_DB)
    wallets_value = DecimalField(
        default=0, min_value=0, precision=PRECISION_LIMIT_IN_DB
    )


class Balance(BaseDocument):
    wallet_id = LazyReferenceField("Wallet", required=True)
    currency_id = LazyReferenceField(
        "Currency", required=True, reverse_delete_rule=DENY
    )
    amount = DecimalField(min_value=0, required=True, precision=PRECISION_LIMIT_IN_DB)
    meta = {"indexes": [{"fields": ("wallet_id", "currency_id"), "unique": True}]}

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        # Check if the document is new and update wallets total-value
        is_new = document.pk is None
        wallet = Wallet.objects.get(id=document.wallet_id.id)
        if is_new:
            wallet.total_value += document.amount
        else:
            current_balance = Balance.objects.get(id=document.id)
            difference = document.amount - current_balance.amount
            wallet.total_value += difference
        wallet.save()

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        # Update wallet's balance_ids if it's a new balance
        is_new = kwargs.get("created", False)
        wallet = Wallet.objects.get(id=document.wallet_id.id)
        if is_new and document.id not in wallet.balances_ids:
            wallet.balances_ids.append(document.id)
            wallet.save()

    @classmethod
    def pre_delete(cls, sender, document, **kwargs):
        # update wallets total-value
        wallet = Wallet.objects.get(id=document.wallet_id.id)
        wallet.total_value -= document.amount
        wallet.save()


signals.pre_save.connect(Balance.pre_save, sender=Balance)
signals.post_save.connect(Balance.post_save, sender=Balance)
signals.pre_delete.connect(Balance.pre_delete, sender=Balance)


class Wallet(BaseDocument, TimestampMixin):
    user_id = ReferenceField("User", required=True, reverse_delete_rule=CASCADE)
    name = StringField(required=True, max_length=50)
    type = StringField(required=True, choices=["fiat", "crypto"])
    balances_ids = ListField(
        ReferenceField(Balance, reverse_delete_rule=PULL), required=False
    )
    total_value = DecimalField(
        required=False, default=Decimal("0.00"), precision=PRECISION_LIMIT_IN_DB
    )
    meta = {"indexes": [{"fields": ("user_id", "name"), "unique": True}]}

    def to_dict(self) -> dict:
        doc_dict = super().to_dict()
        balances = self.balances_ids
        doc_dict["balances_ids"] = [balance.to_dict() for balance in balances]
        doc_dict["total_value"] = str(self.total_value)
        return doc_dict


Wallet.register_delete_rule(Balance, "wallet_id", CASCADE)


class CurrencyExchange(BaseDocument):
    user_id = ReferenceField("User", required=True, reverse_delete_rule=CASCADE)
    from_currency_id = ReferenceField(Currency, required=True, reverse_delete_rule=DENY)
    to_currency_id = ReferenceField(Currency, required=True, reverse_delete_rule=DENY)
    rate = DecimalField(required=True, precision=PRECISION_LIMIT_IN_DB)
    date = DateTimeField(default=datetime.utcnow)

    meta = {
        "indexes": [
            {
                "fields": ("user_id", "from_currency_id", "to_currency_id"),
                "unique": True,
            }
        ]
    }

    def save(self, *args, **kwargs) -> None:
        CurrencyExchangeValidator.validate_reverse_pair(self)
        return super(CurrencyExchange, self).save(*args, **kwargs)


class Category(PredefinedEntity):
    type = StringField(
        required=True, choices=[T.INCOME.value, T.EXPENSE.value, T.TRANSFER.value]
    )
    description = StringField(max_length=255)
    meta = {
        "indexes": [
            {
                "fields": ("name",),
                "unique": True,
                "partialFilterExpression": {"is_predefined": True},
            },
            {
                "fields": ("user_id", "name"),
                "unique": True,
                "partialFilterExpression": {"is_predefined": False},
            },
        ]
    }


class Transaction(BaseDocument):
    user_id = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)
    from_wallet_id = ReferenceField(Wallet, required=False, reverse_delete_rule=CASCADE)
    to_wallet_id = ReferenceField(Wallet, required=False, reverse_delete_rule=CASCADE)
    category_id = ReferenceField(
        "Category", required=False, reverse_delete_rule=NULLIFY
    )
    currency_id = ReferenceField("Currency", required=True, reverse_delete_rule=DENY)
    type = StringField(
        required=True, choices=[T.INCOME.value, T.EXPENSE.value, T.TRANSFER.value]
    )
    amount = DecimalField(required=True, precision=PRECISION_LIMIT_IN_DB)
    date = DateTimeField(default=datetime.utcnow)
    description = StringField(max_length=255)

    def clean(self) -> None:
        super().clean()
        TransactionValidator.validate(self)


class AssetType(PredefinedEntity):
    description = StringField(max_length=255)
    meta = {
        "indexes": [
            {
                "fields": ("name",),
                "unique": True,
                "partialFilterExpression": {"is_predefined": True},
            },
            {
                "fields": ("user_id", "name"),
                "unique": True,
                "partialFilterExpression": {"is_predefined": False},
            },
        ]
    }


class Asset(BaseDocument, TimestampMixin):
    user_id = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)
    asset_type_id = ReferenceField(
        AssetType, required=False, reverse_delete_rule=NULLIFY
    )
    currency_id = ReferenceField(Currency, required=True, reverse_delete_rule=DENY)
    name = StringField(required=True, max_length=50)
    description = StringField(required=False, max_length=255)
    value = DecimalField(required=True, precision=PRECISION_LIMIT_IN_DB)

    def clean(self) -> None:
        super().clean()
        if len(self.name) < 3:
            raise ValidationError("Name must be at least 3 characters long.")

    meta = {"indexes": [{"fields": ("user_id", "name"), "unique": True}]}
