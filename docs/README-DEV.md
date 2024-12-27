
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
- **zxcvbn** : Checks password strength.
- **Blinker**: Signal support for MongoEngine.
- **Uvicorn**: ASGI server for running the application.
- **python-dotenv**: Manage environment variables.

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
├── docs/
│   └── ...                             (includes all docs other than main readme)
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
│   └── ...                             (test cases)
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

## Data Representation

- Decimal precision is controlled using `PRECISION_LIMIT_IN_DB` to ensure consistent precision across monetary fields.

- The `to_dict()` methods in models enable serialization for API responses, converting `ObjectId` fields to strings and including related data as needed.


## Testing

The `My Net Worth App API` includes a comprehensive suite of tests to ensure the functionality and reliability of the application. These tests are written using `pytest`. Now the main focus of tests are E2E test of routes. There can be different kind of tests written but for now I have written positive tests that checks intended usage of routes, some validation and negative tests are also included.

### Setting Up for Testing

1. **Install Required Packages:**
   Ensure you have all the necessary packages installed. You can do this by running:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Test Database:**
   The tests use a separate test database to avoid affecting production data. Ensure your test database is configured correctly in `database/database.py`.

3. **Environment Variables:**
   Make sure your `.env` file is set up correctly with any necessary environment variables for testing.

### Running Tests

1. **Run All Tests:**
   To run all tests in the project, navigate to the root directory of your project and execute:
   ```bash
   pytest
   ```

2. **Run Specific Tests:**
   You can run tests in a specific file or directory by specifying the path. For example, to run tests for wallet routes:
   ```bash
   pytest tests/E2E/functional_tests/test_wallet_routes.py
   ```

3. **Verbose Output:**
   For more detailed output, use the `-v` flag:
   ```bash
   pytest -v
   ```


### Test Structure

- **Fixtures:**
  The tests use `pytest` fixtures for setup and teardown operations. These are defined in `tests/E2E/functional_tests/conftest.py` and include fixtures for database connections, test clients, and test data setup.

- **Async Tests:**
  The tests are marked with `@pytest.mark.asyncio` to support asynchronous operations, which is essential for testing async FastAPI endpoints.

- **Test Organization:**
  Tests are organized by functionality, with separate files for different API routes and features. For example:
  - `test_wallet_routes.py` for wallet-related tests
  - `test_category_routes.py` for category-related tests


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

- [Main README](/README.md)
- [Step by Step Guide](/docs/README-GUIDE.md)
- [Developer Documentation](/docs/README-DEV.md)
- [Models Documentation](/docs/README-MODELS.md)
