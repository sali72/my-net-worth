
# My Net Worth App API

My Net Worth is a personal financial manager and planner application designed to help users keep track of their assets and currencies, calculate their net worth, and manage their financial transactions. The application supports various asset types and currencies, including fiat and cryptocurrencies, allowing users to have a comprehensive view of their financial status.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [Authentication](#authentication)
- [Error Handling](#error-handling)
- [License](#license)
- [Contact Information](#contact-information)

<br>

- [*More Details*](#navigation-panel)

## Features

- **Asset Management**: Keep track of all your assets, including customizable asset types.
- **Currency Support**: Manage currencies with support for fiat and cryptocurrencies.
- **Net Worth Calculation**: Easily calculate your net worth based on your assets and currency holdings.
- **Customizable Currencies and Asset Types**: Define your own currencies and asset types to suit your needs.
- **Wallet Management**: Create and manage multiple wallets with different currencies.
- **Transaction History**: Record, view, and manage your financial transactions.
- **User Authentication**: Secure user registration and authentication system.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **Python 3.8+**: Ensure Python is installed on your system.
- **MongoDB Database**: The application uses MongoDB for data storage.
- **Git**: Version control system to clone the repository.
- **Virtual Environment Tool**: (`venv` or `virtualenv`) Recommended for dependency management.

## Installation

Follow these steps to set up the project locally:

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/my-net-worth-api.git
   cd my-net-worth-api
   ```

2. **Create and Activate a Virtual Environment**

   - **On Windows:**

     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

   - **On Unix or MacOS:**

     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   *Note*: Ensure that `requirements.txt` is in the project root.

## Configuration

1. **Environment Variables**

   Create a `.env` file in the project root directory and add the following configurations:

    ```env
    # DB config
    TEST_MODE=true
    MONGO_DATABASE=my_net_worth_db
    MONGO_ROOT_USERNAME=your_db_username
    MONGO_ROOT_PASSWORD=your_db_password
    MONGO_HOST=mongodb
    MONGO_LOCAL_HOST=mongodb://localhost:27017

    # App config
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    SECRET_KEY = your_secret_key
    ALGORITHM = HS256
    # MINIMUM_PASSWORD_STRENGTH is from 4
    MINIMUM_PASSWORD_STRENGTH = 3
    ```

   Replace `your_secret_key`, `your_db_username`, and `your_db_password` with your actual credentials.
   Also create a db in mongodb with your desired name for the field `MONGO_DATABASE`.

2. **Database Setup**

   Ensure that MongoDB is installed and running on your machine. The application will connect to the MongoDB instance using the credentials provided in the `.env` file.

## Running the Application

Start the FastAPI application using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The `--reload` flag enables auto-reloading on code changes, which is useful during development.

## API Documentation

Once the application is running, access the interactive API documentation provided by Swagger UI at:

- **URL**: `http://localhost:8000/docs`

This interface allows you to explore and test the API endpoints directly from your browser.
*Note*: Ensure that the port is the one you are running uvicorn on it.

## Usage Examples
There are usage examples available in the wiki of github repo.

### Register a New User

```bash
POST /auth/register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "johndoe@example.com",
  "password": "strongpassword123",
  "base_currency_id": "currency_id_123"
}
```

### Log In

```bash
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=johndoe&password=strongpassword123
```

### Get User Net Worth

```bash
GET /user-app-data/net-worth
Authorization: Bearer your_jwt_token
```

### Create a New Wallet

```bash
POST /wallets
Authorization: Bearer your_jwt_token
Content-Type: application/json

{
  "name": "My Savings Wallet",
  "type": "fiat",
  "balances_ids": [
    {
      "currency_id": "currency_id_123",
      "amount": "1000.00"
    }
  ]
}
```

## Authentication

The API uses JSON Web Tokens (JWT) for authentication.

- **Obtaining a Token**: Use the `/auth/login` endpoint with your credentials to receive an access token.
- **Using the Token**: Include the token in the `Authorization` header for authenticated endpoints:

  ```http
  Authorization: Bearer your_jwt_token
  ```

## Error Handling

Errors are returned with appropriate HTTP status codes and a JSON response containing the error details.

**Sample Error Response**:

```json
{
  "exception_name": "HTTPException",
  "detail": "Invalid credentials"
}
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact Information

For questions or feedback, please reach out:

- **Email**: [sahashemi072@gmail.com](mailto:sahashemi072@gmail.com)
- **GitHub**: [sali72](https://github.com/sali72)


---

## Navigation Panel
For more technical details look at other readme files:

- [Main README](README.md)
- [Developer Documentation](README-DEV.md)
- [Models Documentation](README-MODELS.md)
