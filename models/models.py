from datetime import datetime
from bson import ObjectId
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
    EmbeddedDocument,
    EmbeddedDocumentField,
    LazyReferenceField,
)


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


class User(BaseDocument):
    name = StringField(required=False, max_length=50)
    username = StringField(required=True, unique=True)
    # email = EmailField(required=True, unique=True) #TODO uncomment it
    email = StringField(required=True, unique=True)
    hashed_password = StringField(required=True)
    role = StringField(required=True, choices=["user", "admin"])
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)


class Currency(BaseDocument):
    user_id = ReferenceField("User", required=True)
    code = StringField(required=True, max_length=3, unique=True)
    name = StringField(required=True, max_length=50)
    symbol = StringField(required=True, max_length=5)
    is_predefined = BooleanField(default=False)
    is_base_currency = BooleanField(default=False)
    currency_type = StringField(required=True, choices=["fiat", "crypto"])
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    def save(self, *args, **kwargs):
        if self.is_base_currency:
            # Check if there is already a base currency for this user
            existing_base_currency = Currency.objects(
                user_id=self.user_id, is_base_currency=True
            ).first()
            if existing_base_currency and existing_base_currency.id != self.id:
                raise ValidationError(
                    "Only one currency can be the base currency for each user."
                )

        return super(Currency, self).save(*args, **kwargs)


class CurrencyBalance(EmbeddedDocument):
    currency_id = LazyReferenceField("Currency", required=True)
    balance = DecimalField(min_value=0, required=True)


class Wallet(BaseDocument):
    user_id = ReferenceField("User", required=True)
    name = StringField(unique=True, required=True, max_length=50)
    type = StringField(required=True, choices=["fiat", "crypto"])
    currency_balances = ListField(EmbeddedDocumentField(CurrencyBalance), required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)


class CurrencyExchange(BaseDocument):
    user_id = ReferenceField("User", required=True)
    from_currency_id = ReferenceField(Currency, required=True)
    to_currency_id = ReferenceField(Currency, required=True)
    rate = DecimalField(required=True)
    date = DateTimeField(default=datetime.utcnow)
    # make sure "user_id", "from_currency_id" and "to_currency_id" are unique together
    meta = {
        "indexes": [
            {
                "fields": ("user_id", "from_currency_id", "to_currency_id"),
                "unique": True,
            }
        ]
    }


class Transaction(BaseDocument):
    user_id = ReferenceField(User, required=True)
    from_wallet_id = ReferenceField(Wallet, required=False)
    to_wallet_id = ReferenceField(Wallet, required=False)
    category_id = ReferenceField("Category", required=True)
    type = StringField(required=True, choices=["income", "expense", "transfer"])
    amount = DecimalField(required=True, precision=2)
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

    def _validate_income(self):
        if not self.to_wallet_id:
            raise ValidationError("to_wallet_id is required for incomes.")


class Category(BaseDocument):
    user_id = ReferenceField(User, required=True)
    name = StringField(required=True, max_length=50)
    is_predefined = BooleanField(default=False)


class AssetType(BaseDocument):
    user_id = ReferenceField(User, required=True)
    name = StringField(required=True, unique=True, max_length=50)
    is_predefined = BooleanField(default=False)


class Asset(BaseDocument):
    user_id = ReferenceField(User, required=True)
    asset_type = ReferenceField(AssetType, required=True)
    name = StringField(required=True, max_length=50)
    description = StringField(required=False, max_length=255)
    value = DecimalField(required=True, precision=10)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
