from datetime import datetime

from bson import ObjectId
from mongoengine import (
    BooleanField,
    DateTimeField,
    DecimalField,
    Document,
    EmailField,
    EmbeddedDocument,
    EmbeddedDocumentField,
    LazyReferenceField,
    ListField,
    ReferenceField,
    StringField,
    ValidationError,
)

PRECISION_LIMIT_IN_DB = 10


class BaseDocument(Document):
    meta = {"abstract": True}

    def to_dict(self):
        # Convert the document to a dictionary
        doc_dict = self.to_mongo().to_dict()

        # Process each key-value pair in the dictionary
        for key, value in doc_dict.items():
            doc_dict[key] = self._convert_value(value)

        return doc_dict

    def _convert_value(self, value):
        """Convert ObjectId or list of ObjectIds/dicts to strings."""
        if isinstance(value, ObjectId):
            return self._convert_objectid_to_str(value)
        elif isinstance(value, list):
            return self._convert_list(value)
        return value

    def _convert_objectid_to_str(self, object_id):
        """Convert an ObjectId to a string."""
        return str(object_id)

    def _convert_list(self, value_list):
        """Convert a list of ObjectIds or dicts with ObjectIds to strings."""
        if all(isinstance(item, ObjectId) for item in value_list):
            return [self._convert_objectid_to_str(item) for item in value_list]
        elif all(isinstance(item, dict) for item in value_list):
            return [self._convert_dict(item) for item in value_list]
        return value_list

    def _convert_dict(self, value_dict):
        """Convert ObjectId values in a dictionary to strings."""
        for sub_key, sub_value in value_dict.items():
            if isinstance(sub_value, ObjectId):
                value_dict[sub_key] = self._convert_objectid_to_str(sub_value)
        return value_dict


class UserAppData(BaseDocument):
    base_currency_id = LazyReferenceField("Currency", required=True)
    net_worth = DecimalField(default=0, min_value=0, precision=PRECISION_LIMIT_IN_DB)
    assets_value = DecimalField(default=0, min_value=0, precision=PRECISION_LIMIT_IN_DB)
    wallets_value = DecimalField(default=0, min_value=0, precision=PRECISION_LIMIT_IN_DB)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)


class User(BaseDocument):
    name = StringField(required=False, max_length=50)
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    hashed_password = StringField(required=True)
    role = StringField(required=True, choices=["user", "admin"])
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    user_app_data = ReferenceField("UserAppData", reverse_delete_rule=4)


class Currency(BaseDocument):
    user_id = ReferenceField("User", required=False)
    code = StringField(required=True, max_length=10)  # Set max_length to the maximum possible length
    name = StringField(required=True, max_length=50)
    symbol = StringField(required=True, max_length=5)
    is_predefined = BooleanField(default=False)
    currency_type = StringField(required=True, choices=["fiat", "crypto"])
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    meta = {
        "indexes": [
            {"fields": ("user_id", "code"), "unique": True},
            {"fields": ("user_id", "name"), "unique": True},
            {"fields": ("user_id", "symbol"), "unique": True},
        ]
    }

    def clean(self):
        # Call the parent class's clean method
        super().clean()

        # Validate user_id for non-predefined currencies
        if not self.is_predefined and not self.user_id:
            raise ValidationError("user_id is required for non-predefined currencies.")

        # Validate code length based on currency_type
        if self.currency_type == "fiat":
            if len(self.code) != 3:
                raise ValidationError("Code must be exactly 3 characters for fiat currencies.")
        elif self.currency_type == "crypto":
            if not (3 <= len(self.code) <= 10):
                raise ValidationError("Code must be between 3 and 10 characters for crypto currencies.")


class CurrencyBalance(EmbeddedDocument):
    currency_id = LazyReferenceField("Currency", required=True, unique=True)
    balance = DecimalField(min_value=0, required=True, precision=PRECISION_LIMIT_IN_DB)


class Wallet(BaseDocument):
    user_id = ReferenceField("User", required=True)
    name = StringField(required=True, max_length=50)
    type = StringField(required=True, choices=["fiat", "crypto"])
    currency_balances = ListField(EmbeddedDocumentField(CurrencyBalance), required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    meta = {
        "indexes": [
            {
                "fields": ("user_id", "name"),
                "unique": True,
            }
        ]
    }


class CurrencyExchange(BaseDocument):
    user_id = ReferenceField("User", required=True)
    from_currency_id = ReferenceField(Currency, required=True)
    to_currency_id = ReferenceField(Currency, required=True)
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

    def save(self, *args, **kwargs):
        # Check for the existence of the reverse currency pair
        reverse_pair_exists = CurrencyExchange.objects(
            user_id=self.user_id,
            from_currency_id=self.to_currency_id,
            to_currency_id=self.from_currency_id,
        ).first()

        if reverse_pair_exists:
            raise ValidationError(
                "A reverse currency exchange pair already exists for this user."
            )

        return super(CurrencyExchange, self).save(*args, **kwargs)


class Transaction(BaseDocument):
    user_id = ReferenceField(User, required=True)
    from_wallet_id = ReferenceField(Wallet, required=False)
    to_wallet_id = ReferenceField(Wallet, required=False)
    category_id = ReferenceField("Category", required=False)
    currency_id = ReferenceField("Currency", required=True)
    type = StringField(required=True, choices=["income", "expense", "transfer"])
    amount = DecimalField(required=True, precision=PRECISION_LIMIT_IN_DB)
    date = DateTimeField(default=datetime.utcnow)
    description = StringField(max_length=255)

    def clean(self):
        if self.type == "transfer":
            self._validate_transfer()
        elif self.type == "expense":
            self._validate_expense()
        elif self.type == "income":
            self._validate_income()

    def _validate_transfer(self):
        if not self.from_wallet_id or not self.to_wallet_id:
            raise ValidationError(
                "Both from_wallet_id and to_wallet_id are required for transfers."
            )
        if self.from_wallet_id == self.to_wallet_id:
            raise ValidationError(
                "from_wallet_id and to_wallet_id cannot be the same for transfers."
            )

    def _validate_expense(self):
        if not self.from_wallet_id:
            raise ValidationError("from_wallet_id is required for expenses.")
        if self.to_wallet_id:
            raise ValidationError("to_wallet_id should not be provided for expenses.")

    def _validate_income(self):
        if not self.to_wallet_id:
            raise ValidationError("to_wallet_id is required for incomes.")
        if self.from_wallet_id:
            raise ValidationError("from_wallet_id should not be provided for incomes.")


class Category(BaseDocument):
    user_id = ReferenceField(User, required=False)
    name = StringField(required=True, max_length=50)
    type = StringField(required=True, choices=["income", "expense", "transfer"])
    description = StringField(max_length=255)
    is_predefined = BooleanField(default=False)
    meta = {
        "indexes": [
            {"fields": ("user_id", "name"), "unique": True},
        ]
    }

    def clean(self):
        if not self.is_predefined and not self.user_id:
            raise ValidationError("user_id is required for non-predefined categories.")


class AssetType(BaseDocument):
    user_id = ReferenceField(User, required=False)
    name = StringField(required=True, max_length=50)
    description = StringField(required=False, max_length=255)
    is_predefined = BooleanField(default=False)
    meta = {
        "indexes": [
            {"fields": ("user_id", "name"), "unique": True},
        ]
    }

    def clean(self):
        if not self.is_predefined and not self.user_id:
            raise ValidationError("user_id is required for non-predefined asset types.")


class Asset(BaseDocument):
    user_id = ReferenceField(User, required=True)
    asset_type_id = ReferenceField(AssetType, required=False)
    currency_id = ReferenceField(Currency, required=True)
    name = StringField(required=True, max_length=50)
    description = StringField(required=False, max_length=255)
    value = DecimalField(required=True, precision=PRECISION_LIMIT_IN_DB)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    meta = {
        "indexes": [
            {
                "fields": ("user_id", "name"),
                "unique": True,
            }
        ]
    }

    def clean(self):
        super().clean()  # Call the parent class's clean method if needed
        if len(self.name) < 3:
            raise ValidationError("Name must be at least 3 characters long.")
