# My Net Worth App API

My Net Worth is a personal financial manager and planner application designed to help users keep track of their assets and currencies, calculate their net worth, and manage their financial transactions. The application supports various asset types and currencies, including fiat and cryptocurrencies, allowing users to have a comprehensive view of their financial status.

The app is currently live for demo on this link:
[https://my-net-worth.onrender.com/docs](https://my-net-worth.onrender.com/docs)

❗Your first request will be slow because the app spins down with inactivity (It's about deploying on render)

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Security Features](#security-features)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [Authentication](#authentication)
- [Error Handling](#error-handling)
- [License](#license)
- [Contact Information](#contact-information)
- [*More Details*](#navigation-panel)

## Features

- **Asset Management**: Keep track of all your assets, including customizable asset types.
- **Currency Support**: Manage currencies with support for fiat and cryptocurrencies.
- **Net Worth Calculation**: Easily calculate your net worth based on your assets and currency holdings.
- **Customizable Currencies and Asset Types**: Define your own currencies and asset types to suit your needs.
- **Wallet Management**: Create and manage multiple wallets with different currencies.
- **Transaction History**: Record, view, and manage your financial transactions.
- **User Authentication**: Secure user registration and authentication system.
- **Enhanced Security**: 
  - Nginx reverse proxy
  - HTTPS encryption
  - Rate limiting protection
  - CORS security
  - Request size limitations

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **Docker**: Docker Engine installed on your system
- **Docker Compose**: Docker Compose V2 installed
- **Git**: Version control system to clone the repository
- **SSL Certificates**: Valid SSL certificates for HTTPS (required for production)

## Installation

1. **Clone the Repository**

```bash
git clone https://github.com/sali72/my-net-worth
cd my-net-worth
```

2. **Deploy with Docker Compose**

```bash
docker-compose up --build
```

This command will:
- Build the application container
- Start the MongoDB service
- Configure the network between containers
- Start the application with Nginx reverse proxy

## Configuration

1. **Environment Variables**

Create a `.env` file in the project root directory:

```env
# DB config
DB_MODE=container
MONGO_DATABASE=my_net_worth_db
MONGO_ROOT_USERNAME=your_db_username
MONGO_ROOT_PASSWORD=your_db_password
MONGO_HOST=mongodb

# App config
ACCESS_TOKEN_EXPIRE_MINUTES=30
SECRET_KEY=your_secret_key
ALGORITHM=HS256
MINIMUM_PASSWORD_STRENGTH=3
```

2. **SSL Configuration**

Place your SSL certificates in:
- `/etc/nginx/ssl/certs/fullchain.pem`
- `/etc/nginx/ssl/private/privkey.pem`

## Security Features
The application implements several security measures using Nginx:

- **SSL/TLS**: Ensures encrypted data transmission
- **Rate Limiting**: Protects against brute force attacks and DoS attempts
- **CORS Protection**: Controls which domains can access the API
- **Request Limitations**: Prevents oversized payload attacks
- **Proxy Protection**: Maintains request integrity behind reverse proxy

## API Documentation

Once the application is running, access the interactive API documentation at:

- **URL**: `https://localhost/docs`

Note: All API endpoints are served over HTTPS only.

## Usage Examples

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

- **Obtaining a Token**: Use the `/auth/login` endpoint with your credentials
- **Using the Token**: Include the token in the `Authorization` header:
  ```http
  Authorization: Bearer your_jwt_token
  ```

## Error Handling

Errors are returned with appropriate HTTP status codes and a JSON response:

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

- [Main README](/README.md)
- [Step by Step Guide](/docs/README-GUIDE.md)
- [Developer Documentation](/docs/README-DEV.md)
- [Models Documentation](/docs/README-MODELS.md)
