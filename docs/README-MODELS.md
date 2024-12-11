# My Net Worth App API - Data Models

This document provides an overview of the data models used in the **My Net Worth** application, detailing their functionality, fields, and relationships.

## Table of Contents

1. [Base Classes](#base-classes)
   - [BaseDocument](#basedocument)
   - [TimestampMixin](#timestampmixin)
2. [Models](#models)
   - [User](#user)
   - [PredefinedEntity](#predefinedentity)
   - [Currency](#currency)
   - [UserAppData](#userappdata)
   - [Wallet](#wallet)
   - [Balance](#balance)
   - [CurrencyExchange](#currencyexchange)
   - [Category](#category)
   - [Transaction](#transaction)
   - [AssetType](#assettype)
   - [Asset](#asset)
3. [Relationships Between Models](#relationships-between-models)
4. [Validators and Signals](#validators-and-signals)
5. [Data Representation](#data-representation)

<br>

- [*More Details*](#navigation-panel)
---


# Data Models

The application's data layer is modeled using MongoEngine document models, defined in `models/models.py`.

The diagram represents persisted models in DB and their relationships with each other:

![Relationship Diagram](/docs/relationship_diagram.png)

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


---


## Navigation Panel

Use the links below to navigate between different sections of the documentation:

- [Main README](/README.md)
- [Step by Step Guide](/docs/README-GUIDE.md)
- [Developer Documentation](/docs/README-DEV.md)
- [Models Documentation](/docs/README-MODELS.md)
