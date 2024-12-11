
# My Net Worth App API

My Net Worth is a personal financial manager and planner application designed to help users keep track of their assets and currencies, calculate their net worth, and manage their financial transactions. The application supports various asset types and currencies, including fiat and cryptocurrencies, allowing users to have a comprehensive view of their financial status.

The app is currently live for demo on this link:
[https://my-net-worth.onrender.com/docs](https://my-net-worth.onrender.com/docs)

❗Your first request will be slow, because app spins down with inactivity (It's about deploying on render)

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

Certainly! Below is the revised documentation section that includes both the Docker Compose setup and the instructions for deploying without Docker Compose, while retaining the configuration details:


## Installation

You can either try the app with or without docker compose but first clone the repository:

**Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/my-net-worth-api.git
   cd my-net-worth-api
   ```

- **With Docker Compose**

   If you prefer using Docker Compose, ensure you have Docker installed on your machine. Then, run the following command to build and start the services:

   ```bash
   docker-compose up --build
   ```

   This will start the application and a MongoDB service as defined in the `docker-compose.yml` file.

- **Without Docker Compose**

   - **Create and Activate a Virtual Environment**

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

   - **Install Dependencies**

     ```bash
     pip install -r requirements.txt
     ```

     *Note*: Ensure that `requirements.txt` is in the project root.

## Configuration

1. **Environment Variables**

   Create a `.env` file in the project root directory and add the following configurations:

    ```env
    # DB config
    DB_MODE=local
    MONGO_DATABASE=my_net_worth_db
    MONGO_ROOT_USERNAME=your_db_username
    MONGO_ROOT_PASSWORD=your_db_password
    MONGO_HOST=mongodb
    MONGO_LOCAL_HOST=mongodb://localhost:27017
    MONGO_ATLAS_CONNECTION_STRING=your_mongo_atlas_connection_string

    # App config
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    SECRET_KEY=your_secret_key
    ALGORITHM=HS256
    MINIMUM_PASSWORD_STRENGTH=3
    ```

   Replace `your_secret_key`, `your_db_username`, and `your_db_password` with your actual credentials. If you want to use MongoDB Atlas, set `TEST_MODE=atlas` and provide the `MONGO_ATLAS_CONNECTION_STRING`.


## Database Setup

The application supports connecting to MongoDB in three different modes: locally, within a Docker container, or using MongoDB Atlas. You can configure the mode by setting the `DB_MODE` environment variable in your `.env` file.

1. **Local MongoDB**

   To use a local MongoDB instance, set `DB_MODE=local` in your `.env` file. Ensure MongoDB is installed and running on your machine. The application will connect using the following environment variables:

   ```env
   DB_MODE=local
   MONGO_DATABASE=my_net_worth_db
   MONGO_LOCAL_HOST=mongodb://localhost:27017
   ```

2. **MongoDB in Docker Container**

   If you prefer to use MongoDB within a Docker container, set `DB_MODE=container`. This mode is typically used when deploying the application with Docker Compose. The connection will use the following environment variables:

   ```env
   DB_MODE=container
   MONGO_DATABASE=my_net_worth_db
   MONGO_HOST=mongodb
   ```

   You can optionally add `MONGO_ROOT_USERNAME` and `MONGO_ROOT_PASSWORD` if authentication is required, but ensure the user is created in MongoDB.

3. **MongoDB Atlas**

   To connect to MongoDB Atlas, set `DB_MODE=atlas` and provide your MongoDB Atlas connection string. Ensure your MongoDB Atlas cluster is configured to allow connections from your network. Use the following environment variables:

   ```env
   DB_MODE=atlas
   MONGO_ATLAS_CONNECTION_STRING=your_mongo_atlas_connection_string
   ```

   Replace `your_mongo_atlas_connection_string` with the actual connection string provided by MongoDB Atlas.

By configuring the `DB_MODE` and the corresponding environment variables, you can easily switch between different MongoDB setups based on your deployment needs.


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
