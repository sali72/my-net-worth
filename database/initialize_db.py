import logging

from app.crud.asset_type_crud import AssetTypeCRUD
from app.crud.category_crud import CategoryCRUD
from app.crud.currency_crud import CurrencyCRUD
from models.enums import TransactionTypeEnum as T
from models.models import AssetType, Category, Currency

logger = logging.getLogger(__name__)


async def initialize_fiat_and_crypto_currencies():
    currencies = [
        # Fiat currencies
        {"code": "USD", "name": "US Dollar", "symbol": "$", "currency_type": "fiat"},
        {"code": "EUR", "name": "Euro", "symbol": "€", "currency_type": "fiat"},
        {"code": "JPY", "name": "Japanese Yen", "symbol": "¥", "currency_type": "fiat"},
        {
            "code": "GBP",
            "name": "British Pound",
            "symbol": "£",
            "currency_type": "fiat",
        },
        {
            "code": "AUD",
            "name": "Australian Dollar",
            "symbol": "A$",
            "currency_type": "fiat",
        },
        {
            "code": "CAD",
            "name": "Canadian Dollar",
            "symbol": "C$",
            "currency_type": "fiat",
        },
        {
            "code": "CHF",
            "name": "Swiss Franc",
            "symbol": "CHF",
            "currency_type": "fiat",
        },
        {
            "code": "CNY",
            "name": "Chinese Yuan",
            "symbol": "CN¥",
            "currency_type": "fiat",
        },
        {
            "code": "SEK",
            "name": "Swedish Krona",
            "symbol": "kr",
            "currency_type": "fiat",
        },
        {
            "code": "NZD",
            "name": "New Zealand Dollar",
            "symbol": "NZ$",
            "currency_type": "fiat",
        },
        # Crypto currencies
        {"code": "BTC", "name": "Bitcoin", "symbol": "₿", "currency_type": "crypto"},
        {"code": "ETH", "name": "Ethereum", "symbol": "Ξ", "currency_type": "crypto"},
        {"code": "XRP", "name": "Ripple", "symbol": "XRP", "currency_type": "crypto"},
        {"code": "LTC", "name": "Litecoin", "symbol": "Ł", "currency_type": "crypto"},
        {
            "code": "BCH",
            "name": "Bitcoin Cash",
            "symbol": "BCH",
            "currency_type": "crypto",
        },
    ]

    for currency_data in currencies:
        existing_currency = await CurrencyCRUD.get_one_by_user_and_code_optional(
            currency_data["code"], None
        )
        if not existing_currency:
            currency = Currency(
                user_id=None,
                code=currency_data["code"],
                name=currency_data["name"],
                symbol=currency_data["symbol"],
                currency_type=currency_data["currency_type"],
                is_predefined=True,
            )
            await CurrencyCRUD.create_one(currency)

    logger.info("Currencies initialized")


async def initialize_common_categories():
    categories = [
        {"name": "Salary", "type": T.INCOME.value},
        {"name": "Freelance", "type": T.INCOME.value},
        {"name": "Groceries", "type": T.EXPENSE.value},
        {"name": "Rent", "type": T.EXPENSE.value},
        {"name": "Utilities", "type": T.EXPENSE.value},
        {"name": "Bank Transfer", "type": T.TRANSFER.value},
    ]

    for category_data in categories:
        existing_category = await CategoryCRUD.get_one_by_user_and_name_optional(
            category_data["name"], None
        )
        if not existing_category:
            category = Category(
                user_id=None,
                name=category_data["name"],
                type=category_data["type"],
                is_predefined=True,
            )
            await CategoryCRUD.create_one(category)

    logger.info("Categories initialized")


async def initialize_common_asset_types():
    asset_types = [
        {"name": "Real Estate"},
        {"name": "Vehicle"},
        {"name": "Precious Metals"},
        {"name": "Collectibles"},
        {"name": "Art"},
    ]

    for asset_type_data in asset_types:
        existing_asset_type = await AssetTypeCRUD.get_one_by_user_and_name_optional(
            asset_type_data["name"], None
        )
        if not existing_asset_type:
            asset_type = AssetType(
                user_id=None,
                name=asset_type_data["name"],
                is_predefined=True,
            )
            await AssetTypeCRUD.create_one(asset_type)

    logger.info("Categories initialized")
