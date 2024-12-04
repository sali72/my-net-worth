
# My Net Worth App API - Developer Guide

Welcome to the developer guide for the **My Net Worth App API**. This document provides an in-depth look into the technological aspects of the application, aimed at helping developers understand, set up, and contribute to the project effectively.

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Database Connection](#database-connection)
- [Application Entry Point](#application-entry-point)
- [Modules and Packages](#modules-and-packages)
- [Coding Standards and Best Practices](#coding-standards-and-best-practices)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Contributing](#contributing)
- [Back to User Guide](#back-to-user-guide)

<br>

- [*More Details*](#navigation-panel)

## Project Overview

**My Net Worth** is a personal financial manager and planner application that enables users to keep an account of their assets, currencies, and overall net worth. It allows users to:

- Track assets and their estimated values.
- Manage different currencies, including fiat and cryptocurrencies.
- Calculate net worth effortlessly.
- Define custom currencies and asset types.
- Manage multiple wallets with different currencies.
- Record and review transaction history.

## Architecture

The application follows a modular architecture using **FastAPI** for building the API endpoints and **MongoDB** as the database. The codebase is organized to promote scalability, maintainability, and adherence to best practices.

### Key Architectural Components

- **API Routes**: Managed by FastAPI routers, segregated by functionality.
- **Controllers**: Handle business logic and interact with models.
- **Models**: Represent data structures using MongoEngine.
- **Database Connection**: Handled centrally to manage connections effectively.
- **Exception Handling**: Custom exception handlers for consistent error responses.

## Technologies Used

- **Python 3.8+**
- **FastAPI**: High-performance web framework for building APIs.
- **MongoDB**: NoSQL database for storing application data.
- **MongoEngine**: Object-Document Mapper (ODM) for MongoDB.
- **Pydantic**: Data validation and settings management.
- **PyJWT**: Handling JSON Web Tokens for authentication.
- **Passlib**: Secure password hashing.
- **Blinker**: Signal support for MongoEngine.
- **Uvicorn**: ASGI server for running the application.
- **Dotenv**: Manage environment variables.

## Project Structure

The project is organized into several directories and modules:

```markdown
my-net-worth-api/
├── app/
│   ├── api/
│   │   ├── controllers/
│   │   │   └── ...                     (business logic)
│   │   ├── endpoints/
│   │   │   └── ...                     (API routes)
│   │   ├── crud/
│   │   │   └── ...                     (database interaction modules)
│   ├── main.py                         (application entry point)
├── database/
│   ├── database.py                     (database connection and initialization)
│   ├── initialize_db.py                (database initialization scripts)
├── models/
│   ├── enums.py                        (enum classes used across the app)
│   ├── models.py                       (all MongoEngine models)
│   ├── schemas.py                      (Pydantic validators for user input)
│   ├── validator_utilities.py          (general validators)
│   └── validators.py                   (model specific validators)
│                    
├── commons/
│   ├── exception_handlers.py           (custom exception handlers)
│   ├── ...                             (additional shared modules)
├── tests/
│   └── ...                             (test cases will be added)
├── .env                                (environment variables)
├── requirements.txt                    (project dependencies)
.
.
. 
```


## Database Connection

The database connection is managed centrally in the `database/database.py` module:

## Application Entry Point

The entry point of the application is `app/main.py`. It initializes the FastAPI app, includes routers, and sets up exception handlers.

### Lifespan Event

Using the `@asynccontextmanager`, the application manages startup and shutdown events:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_to_db()
    yield
```

### FastAPI Initialization

```python
app = FastAPI(
    title="My Net Worth App API",
    description="Personal financial manager and planner application",
    lifespan=lifespan,
)
```

### Including Routers

The application includes routers for different endpoints:

```python
app.include_router(auth_routes)
app.include_router(user_app_data_routes)
app.include_router(currency_routes)
app.include_router(currency_exchange_routes)
app.include_router(wallet_routes)
app.include_router(transaction_routes)
app.include_router(asset_type_routes)
app.include_router(asset_routes)
app.include_router(category_routes)
```

### Exception Handlers

Custom exception handlers are added for consistent error responses:

```python
from fastapi import HTTPException
from commons.exception_handlers import base_exception_handler, http_exception_handler

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, base_exception_handler)
```

## Modules and Packages

### API Endpoints

Located in `app/api/endpoints/`, each module defines routes related to a specific feature, such as:

- `asset_routes.py`
- `wallet_routes.py`
- `transaction_routes.py`

**Example Route Definition:**

```python
from fastapi import APIRouter, Depends, Path
from app.api.controllers.auth_controller import has_role
from app.api.controllers.wallet_controller import WalletController
from models.enums import RoleEnum as R
from models.schemas import WalletCreateSchema, ResponseSchema

router = APIRouter(prefix="/wallets", tags=["Wallet"])

@router.post(
    "",
    response_model=ResponseSchema,
)
async def create_wallet_route(
    wallet_schema: WalletCreateSchema, user=Depends(has_role(R.USER))
) -> ResponseSchema:
    """
    Create a new wallet for the user.

    Args:
        wallet_schema (WalletCreateSchema): The schema containing wallet details.
        user (User): The current user, injected by dependency.

    Returns:
        ResponseSchema: The response containing the created wallet's ID and a success message.
    """
    wallet_id = await WalletController.create_wallet(wallet_schema, user)
    return ResponseSchema(data={"id": wallet_id}, message="Wallet created successfully")
```

### Controllers

Located in `app/api/controllers/`, controllers contain the business logic and interact with models.

**Example Controller Method:**

```python
class WalletController:
    @staticmethod
    async def create_wallet(wallet_schema: WalletCreateSchema, user: User):
        # Business logic to create a wallet
        wallet = Wallet(**wallet_schema.dict(), user_id=user.id)
        wallet.save()
        return str(wallet.id)
```

### Models

Defined in `models/models.py`, using MongoEngine for ODM.

**Example Model Definition:**

```python
from mongoengine import Document, StringField, ReferenceField, ListField
from models.user import User

class Wallet(Document):
    name = StringField(required=True)
    type = StringField(required=True)
    user_id = ReferenceField(User, required=True)
    balances_ids = ListField(ReferenceField('Balance'))
```

### Schemas

Defined in `models/schemas.py`, using Pydantic for request and response validation.

**Example Schema:**

```python
from pydantic import BaseModel

class WalletCreateSchema(BaseModel):
    name: str
    type: str
    balances_ids: list
```

### Exception Handling

Custom exception handlers in `commons/exception_handlers.py` ensure consistent error responses.

**Example Exception Handler:**

```python
from fastapi.responses import JSONResponse

async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"exception_name": exc.__class__.__name__, "detail": exc.detail},
    )
```

## Coding Standards and Best Practices

- **PEP 8**: Follow Python's PEP 8 style guide for code consistency.
- **Type Hinting**: Use type annotations for better code readability and tooling support.
- **Dependency Injection**: Utilize FastAPI's `Depends` for injecting dependencies like the current user.
- **Modular Design**: Keep the code modular by separating concerns into different modules and packages.
- **Documentation**: Include Google-style docstrings for all endpoints.
- **Error Handling**: Use centralized exception handlers for consistent error responses.
- **Security**: Implement proper authentication and authorization checks.

## Running the Application


# Data Models

The application's data layer is modeled using MongoEngine document models, defined in `models/models.py`. The models represent the various entities and their relationships in the **My Net Worth** application. This section provides an overview of each model, their functionality, and the purpose of each field.

## Base Classes

### `BaseDocument`

`BaseDocument` is an abstract base class inherited by other models to provide common functionality. It extends `Document` from MongoEngine and includes methods for converting documents to dictionaries, handling custom serialization like converting `ObjectId` fields to strings.

- **Purpose**: Provides common serialization methods for all models.

### `TimestampMixin`

`TimestampMixin` is a mixin that adds timestamp fields to a document.

- **Fields**:
  - `created_at` (`DateTimeField`): The timestamp when the document was created (default to current UTC datetime).
  - `updated_at` (`DateTimeField`): The timestamp when the document was last updated (default to current UTC datetime).

- **Purpose**: Automatically records creation and modification times for documents.

## Models

### `User`

Represents a user in the application.

- **Fields**:
  - `name` (`StringField`): The user's full name (optional, max length 50).
  - `username` (`StringField`): Unique username for the user (required).
  - `email` (`EmailField`): Unique email address (required).
  - `hashed_password` (`StringField`): The user's hashed password (required).
  - `role` (`StringField`): The user's role in the system (required, choices: `"user"`, `"admin"`).

- **Purpose**: Stores user credentials and role information.

### `PredefinedEntity`

An abstract base class for entities that can be predefined (available system-wide) or user-specific.

- **Fields**:
  - `user_id` (`ReferenceField` to `User`): The owner of the entity (optional for predefined entities).
  - `name` (`StringField`): The name of the entity (required, max length 50).
  - `is_predefined` (`BooleanField`): Indicates whether the entity is predefined (default `False`).

- **Purpose**: Provides common fields and validation for entities that can be predefined or user-defined.

- **Validation**:
  - Ensures that `user_id` is provided for non-predefined entities.
  - Prevents duplication of predefined entities with the same name.

### `Currency`

Represents a currency, either fiat or cryptocurrency.

- **Inherits**: `PredefinedEntity`, `TimestampMixin`

- **Fields**:
  - `code` (`StringField`): The currency code (e.g., `"USD"`, `"BTC"`) (required, max length 10).
  - `symbol` (`StringField`): The currency symbol (e.g., `"$"`, `"₿"`) (required, max length 5).
  - `currency_type` (`StringField`): Type of currency (required, choices: `"fiat"`, `"crypto"`).

- **Purpose**: Stores information about different currencies used in the application.

- **Validation**:
  - Validates the length of the `code` based on `currency_type` (fiat codes must be exactly 3 characters).

### `UserAppData`

Stores application-specific data related to a user.

- **Fields**:
  - `user_id` (`ReferenceField` to `User`): The user to which this data belongs (required, unique).
  - `base_currency_id` (`LazyReferenceField` to `Currency`): The user's base currency (required).
  - `net_worth` (`DecimalField`): The user's net worth (default `0`).
  - `assets_value` (`DecimalField`): Total value of the user's assets (default `0`).
  - `wallets_value` (`DecimalField`): Total value of the user's wallets (default `0`).

- **Purpose**: Stores aggregated financial data for a user.

### `Wallet`

Represents a user's wallet that holds balances in various currencies.

- **Fields**:
  - `user_id` (`ReferenceField` to `User`): The owner of the wallet (required).
  - `name` (`StringField`): The wallet's name (required, max length 50).
  - `type` (`StringField`): The type of wallet (required, choices: `"fiat"`, `"crypto"`).
  - `balances_ids` (`ListField` of `ReferenceField` to `Balance`): List of balances associated with the wallet.
  - `total_value` (`DecimalField`): The total value of the wallet (default `0`).

- **Purpose**: Manages a collection of balances in different currencies for a user.

- **Relationships**:
  - One-to-many relationship with `Balance` (a wallet can have multiple balances).

- **Methods**:
  - `to_dict()`: Custom serialization method to include balances and total value.

### `Balance`

Represents the amount of a specific currency held in a wallet.

- **Fields**:
  - `wallet_id` (`LazyReferenceField` to `Wallet`): The wallet containing this balance (required).
  - `currency_id` (`LazyReferenceField` to `Currency`): The currency of the balance (required).
  - `amount` (`DecimalField`): The amount of currency (required).

- **Purpose**: Tracks the balance of a specific currency within a wallet.

- **Relationships**:
  - Belongs to a `Wallet`.

- **Signals**:
  - `pre_save`: Updates the associated wallet's `total_value` before saving a balance.
  - `post_save`: Adds the balance to the wallet's `balances_ids` after saving.
  - `pre_delete`: Updates the wallet's `total_value` when a balance is deleted.

### `CurrencyExchange`

Represents an exchange rate between two currencies.

- **Fields**:
  - `user_id` (`ReferenceField` to `User`): The owner of the exchange rate (required).
  - `from_currency_id` (`ReferenceField` to `Currency`): The currency being converted from (required).
  - `to_currency_id` (`ReferenceField` to `Currency`): The currency being converted to (required).
  - `rate` (`DecimalField`): The exchange rate (required).
  - `date` (`DateTimeField`): The date of the exchange rate (default to current datetime).

- **Purpose**: Stores custom exchange rates defined by the user.

- **Validation**:
  - Prevents duplicate or reverse pairs of currency exchanges for the same user.

### `Category`

Represents a category for transactions.

- **Inherits**: `PredefinedEntity`

- **Fields**:
  - `type` (`StringField`): The type of transaction associated with the category (required, choices: `"income"`, `"expense"`, `"transfer"`).
  - `description` (`StringField`): A description of the category (optional, max length 255).

- **Purpose**: Categorizes transactions for better organization and reporting.

- **Validation**:
  - Ensures unique category names within predefined and user-defined scopes.

### `Transaction`

Represents a financial transaction.

- **Fields**:
  - `user_id` (`ReferenceField` to `User`): The owner of the transaction (required).
  - `from_wallet_id` (`ReferenceField` to `Wallet`): The wallet the amount is debited from (optional).
  - `to_wallet_id` (`ReferenceField` to `Wallet`): The wallet the amount is credited to (optional).
  - `category_id` (`ReferenceField` to `Category`): The category of the transaction (optional).
  - `currency_id` (`ReferenceField` to `Currency`): The currency of the transaction (required).
  - `type` (`StringField`): The type of transaction (required, choices: `"income"`, `"expense"`, `"transfer"`).
  - `amount` (`DecimalField`): The amount of the transaction (required).
  - `date` (`DateTimeField`): The date of the transaction (default to current datetime).
  - `description` (`StringField`): A description of the transaction (optional, max length 255).

- **Purpose**: Records transactions affecting wallets and assets.

- **Validation**:
  - Custom validation based on transaction `type`:
    - **Income**: `to_wallet_id` is required; `from_wallet_id` should not be provided.
    - **Expense**: `from_wallet_id` is required; `to_wallet_id` should not be provided.
    - **Transfer**: Both `from_wallet_id` and `to_wallet_id` are required and cannot be the same.

### `AssetType`

Represents a type of asset.

- **Inherits**: `PredefinedEntity`

- **Fields**:
  - `description` (`StringField`): Description of the asset type (optional, max length 255).

- **Purpose**: Categorizes assets for better organization.

- **Validation**:
  - Ensures unique asset type names within predefined and user-defined scopes.

### `Asset`

Represents a user's asset.

- **Fields**:
  - `user_id` (`ReferenceField` to `User`): The owner of the asset (required).
  - `asset_type_id` (`ReferenceField` to `AssetType`): The type of the asset (optional).
  - `currency_id` (`ReferenceField` to `Currency`): The currency in which the asset is valued (required).
  - `name` (`StringField`): The name of the asset (required, min length 3, max length 50).
  - `description` (`StringField`): A description of the asset (optional, max length 255).
  - `value` (`DecimalField`): The monetary value of the asset (required).

- **Purpose**: Stores information about user assets outside of wallets.

- **Validation**:
  - Ensures the `name` is at least 3 characters long.

## Relationships Between Models

- **User**:
  - Has one `UserAppData`.
  - Owns multiple `Wallet`, `Asset`, `Transaction`, `CurrencyExchange`, `Category`, `AssetType`.

- **Wallet**:
  - Contains multiple `Balance`.
  - Owned by a `User`.

- **Balance**:
  - Belongs to a `Wallet`.
  - Represents the amount of a specific `Currency`.

- **Transaction**:
  - Associated with a `User`.
  - May involve `from_wallet_id` and/or `to_wallet_id` (depending on `type`).
  - Categorized by a `Category`.

- **Asset**:
  - Owned by a `User`.
  - Defined by an `AssetType`.
  - Valued in a specific `Currency`.

- **CurrencyExchange**:
  - Owned by a `User`.
  - Defines the exchange rate between two `Currency` entities.

- **Category** and **AssetType**:
  - Can be predefined (available to all users) or user-defined.

## Validators and Signals

- **Validators**:
  - Custom validators are defined in `models/validators.py` and are used to enforce business rules during model validation.
    - `PredefinedEntityValidator`: Validates that `user_id` is provided for non-predefined entities and prevents duplicates.
    - `CurrencyValidator`: Validates the `code` length based on `currency_type`.
    - `CurrencyExchangeValidator`: Ensures there are no reverse currency pairs for the same user.
    - `TransactionValidator`: Validates `Transaction` fields based on `type`.

- **Signals**:
  - Models like `Balance` utilize MongoEngine signals (`pre_save`, `post_save`, `pre_delete`) to maintain data consistency, such as updating the wallet's total value when balances change.

## Data Representation

- Decimal precision is controlled using `PRECISION_LIMIT_IN_DB` to ensure consistent precision across monetary fields.

- The `to_dict()` methods in models enable serialization for API responses, converting `ObjectId` fields to strings and including related data as needed.

## Data Models

## Testing

Will be added in future.

## Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the Repository**

2. **Create a Feature Branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Commit Your Changes**

   ```bash
   git commit -m "Description of your changes"
   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request**

---

## Navigation Panel

Use the links below to navigate between different sections of the documentation:

- [Main README](README.md)
- [Developer Documentation](README-DEV.md)
- [Models Documentation](README-MODELS.md)
