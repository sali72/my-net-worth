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
    LazyReferenceField
)


class BaseDocument(Document):
    meta = {"abstract": True}

    def to_dict(self):
        # Convert the document to a dictionary
        doc_dict = self.to_mongo().to_dict()

        # Convert ObjectId fields to strings
        for key, value in doc_dict.items():
            if isinstance(value, ObjectId):
                doc_dict[key] = str(value)
            elif isinstance(value, list) and all(
                isinstance(item, ObjectId) for item in value
            ):
                doc_dict[key] = [str(item) for item in value]

        return doc_dict


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
                raise ValidationError("Only one currency can be the base currency for each user.")
        
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
    from_currency_id = ReferenceField(Currency, required=True)
    to_currency_id = ReferenceField(Currency, required=True)
    rate = DecimalField(required=True)
    date = DateTimeField(default=datetime.utcnow)


class Transaction(BaseDocument):
    user_id = ReferenceField(User, required=True)
    wallet_id = ReferenceField(Wallet, required=True)
    category_id = ReferenceField("Category", required=True)
    type = StringField(required=True, choices=["income", "expense", "transfer"])
    amount = DecimalField(required=True, precision=2)
    date = DateTimeField(default=datetime.utcnow)
    description = StringField(max_length=255)


class Category(BaseDocument):
    name = StringField(required=True, max_length=50)
    is_predefined = BooleanField(default=False)


class AssetType(BaseDocument):
    name = StringField(required=True, unique=True, max_length=50)
    is_predefined = BooleanField(default=False)


class Asset(BaseDocument):
    asset_type = ReferenceField(AssetType, required=True)
    name = StringField(required=True, max_length=50)
    description = StringField(required=False, max_length=255)
    value = DecimalField(required=True, precision=10)
    user_id = ReferenceField(User, required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
