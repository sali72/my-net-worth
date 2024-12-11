# My Net Worth App API - Step By Step Guide

This part of document provides an example usage of each API and explains the intended usage of them.

Pay more attention to 🔴, ⚠️ and ☝️ emoji signs as they provide important usage guides about application. some API's can not be used until you have some info provided from another API.



<details>
<summary>Toggle Authentication Details</summary>

## Authentication

- 🔴 First get all the predefined currencies available, then choose one.

    example curl request:

    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/currencies/predefined' \
      -H 'accept: application/json'
    ```

    example response body:

    ```json
    {
      "message": "Predefined currencies retrieved successfully",
      "data": {
        "currencies": [
          {
            "_id": "6745dbed6b99c20aab2de4e0",
            "code": "USD",
            "name": "US Dollar",
            "symbol": "$",
            "is_predefined": true,
            "currency_type": "fiat",
            "created_at": "2024-11-18T13:47:55.569000",
            "updated_at": "2024-11-18T13:47:55.569000"
          },
          {
            "_id": "6745dbed6b99c20aab2de4e1",
            "code": "EUR",
            "name": "Euro",
            "symbol": "€",
            "is_predefined": true,
            "currency_type": "fiat",
            "created_at": "2024-11-18T13:47:55.572000",
            "updated_at": "2024-11-18T13:47:55.572000"
          }
        ]
      },
      "timestamp": "2024-11-24T17:03:14.290672"
    }
    ```

- Then create an account using your desired base currency and your personal info. In this example, I want to use the dollar as my base currency. I used the id we got from the previous request. From now on, to use the app, for every request you need to provide the `access_token` you got here as a header named `Authentication`.

    example curl request:

    ```bash
    curl -X 'POST' \
      'http://127.0.0.1:8000/register' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "username": "johndoe",
      "email": "johndoe@example.com",
      "password": "UncommonPass?123",
      "base_currency_id": "6745dbed6b99c20aab2de4e0"
    }'
    ```

    example response body:

    ```json
    {
      "message": "User registered successfully",
      "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMzMjE2MTE1fQ.O9JqJ7LojkenwTD23Az7Dq-85vnoS78P4QOxZyRqf74",
        "token_type": "bearer"
      },
      "timestamp": "2024-12-03T11:03:20.141111"
    }
    ```

- 🔴 After registration, if you want to get your access token, you can log in using your credentials.

    example curl request:

    ```bash
    curl -X 'POST' \
      'http://127.0.0.1:8000/login' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/x-www-form-urlencoded' \
      -d 'grant_type=password&username=johndoe&password=UncommonPass%3F123&scope=&client_id=string&client_secret=string'
    ```

    example response body:

    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMzMjE2NDgwfQ.UYTDS0bOybXjs2VMujeqeNZBwSaw5N5Rr28_FS79_Ps",
      "token_type": "bearer"
    }
    ```

- You also can get your info.

    example curl request:

    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/user' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMzMjE2Mjc4fQ.VByWTQqSHHEiYHFh6fH4OLIPMHrBg_IGKfv8IzCeByQ'
    ```

    example response body:

    ```json
    {
      "message": "User data retrieved successfully",
      "data": {
        "_id": "674ec06bb42bef228d9ac134",
        "created_at": "2024-12-03T08:25:15.170000",
        "updated_at": "2024-12-03T08:25:15.170000",
        "username": "johndoe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$9Uvwmx8wa/PhrqCRnOr2y.wTZEhhB5r/TB/T8gm7XtUEcl56iCuXK",
        "role": "user"
      },
      "timestamp": "2024-12-03T11:03:20.141111"
    }
    ```

- Modify your info.

    example curl request:

    ```bash
    curl -X 'PUT' \
      'http://127.0.0.1:8000/update' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMzMjE2Mjc4fQ.VByWTQqSHHEiYHFh6fH4OLIPMHrBg_IGKfv8IzCeByQ' \
      -H 'Content-Type: application/json' \
      -d '{
      "name": "John Doe",
      "username": "newusername",
      "email": "newemail@example.com",
      "password": "newstrongpassword123"
    }'
    ```

    example response body:

    ```json
    {
      "message": "User credentials updated successfully",
      "data": {
        "_id": "674ec06bb42bef228d9ac134",
        "created_at": "2024-12-03T08:25:15.170000",
        "updated_at": "2024-12-03T08:25:15.170000",
        "username": "johndoe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$9Uvwmx8wa/PhrqCRnOr2y.wTZEhhB5r/TB/T8gm7XtUEcl56iCuXK",
        "role": "user"
      },
      "timestamp": "2024-12-03T11:03:20.141111"
    }
    ```

- Or delete your account. But beware that if you delete your account, all of your data will be lost too.

    example curl request:

    ```bash
    curl -X 'DELETE' \
      'http://127.0.0.1:8000/user' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMzMjE1OTk1fQ.6xTi3durHRHfIGNbW0Y6sEcI2wJ_VgSh4rdO8kQljzg'
    ```

    example response body:

    ```json
    {
      "message": "User deleted successfully",
      "data": {},
      "timestamp": "2024-12-03T11:03:20.141111"
    }
    ```

</details>


<details>
<summary>Toggle Currency Exchanges Details</summary>

## Currency Exchanges

- ⚠️ If you want to have any currency in your wallets other than your base currency, you have to make sure an exchange rate for them exists in the database. This is crucial to the app's functionalities because it wants to calculate the value of each currency to your base currency and give you an estimation of your wallets and assets value.

    example curl request:

    ```bash
    curl -X 'POST' \
      'http://127.0.0.1:8000/currency-exchanges' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNDY2NTMzfQ.U5VPkELge_1acLDjIPwnQ9nUxAuaemQY2Xfg6622OY0' \
      -H 'Content-Type: application/json' \
      -d '{
      "from_currency_id": "673b458b63f75539e9f1fcff",
      "to_currency_id": "673b458b63f75539e9f1fcfe",
      "rate": 0.85,
      "date": "2023-10-15T14:30:00Z"
    }'
    ```

    example response body:

    ```json
    {
    "message":"Currency exchange created successfully",
    "data": {
    "id": {
    "_id":"674350650627757e5b6ab189",
    "user_id":"6743368dfce3476d0b8c5de0",
    "from_currency_id":"673b458b63f75539e9f1fcff",
    "to_currency_id":"673b458b63f75539e9f1fcfe",
    "rate":0.85,
    "date":"2023-10-15T14:30:00Z"
        }
      },
    "timestamp":"2024-11-24T19:40:29.240770"
    }
    ```

- You can do other CRUD operations on currency exchanges. Let's try getting all.

    example curl request:

    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/currency-exchanges' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTE4MjE3fQ.TY29rBpfyuuWd4K7a3wszmlINvZMF2OjSqUXhySJM2M'
    ```

    example response body:

    ```json
    {
      "message": "Currency exchanges retrieved successfully",
      "data": {
        "currency_exchanges": [
          {
            "_id": "674350650627757e5b6ab189",
            "user_id": "6743368dfce3476d0b8c5de0",
            "from_currency_id": "673b458b63f75539e9f1fcff",
            "to_currency_id": "673b458b63f75539e9f1fcfe",
            "rate": 0.85,
            "date": "2023-10-15T14:30:00"
          }
        ]
      },
      "timestamp": "2024-11-25T10:03:06.482411"
    }
    ```

- Read an exchange.

    example curl request:

    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/currency-exchanges/674350650627757e5b6ab189' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTE4MjE3fQ.TY29rBpfyuuWd4K7a3wszmlINvZMF2OjSqUXhySJM2M'
    ```

    example response body:

    ```json
    {
      "message": "Currency exchange retrieved successfully",
      "data": {
        "currency_exchange": {
          "_id": "674350650627757e5b6ab189",
          "user_id": "6743368dfce3476d0b8c5de0",
          "from_currency_id": "673b458b63f75539e9f1fcff",
          "to_currency_id": "673b458b63f75539e9f1fcfe",
          "rate": 0.85,
          "date": "2023-10-15T14:30:00"
        }
      },
      "timestamp": "2024-11-25T10:03:06.482411"
    }
    ```

- Update an exchange.

    example curl request:

    ```bash
    curl -X 'PUT' \
      'http://127.0.0.1:8000/currency-exchanges/674350650627757e5b6ab189' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTE4MjE3fQ.TY29rBpfyuuWd4K7a3wszmlINvZMF2OjSqUXhySJM2M' \
      -H 'Content-Type: application/json' \
      -d '{
      "rate": 0.822
    }'
    ```

    example response body:

    ```json
    {
      "message": "Currency exchange updated successfully",
      "data": {
        "currency_exchange": {
          "_id": "674350650627757e5b6ab189",
          "user_id": "6743368dfce3476d0b8c5de0",
          "from_currency_id": "673b458b63f75539e9f1fcff",
          "to_currency_id": "673b458b63f75539e9f1fcfe",
          "rate": 0.822,
          "date": "2024-11-25T06:38:25.709000"
        }
      },
      "timestamp": "2024-11-25T10:03:06.482411"
    }
    ```

- Delete one exchange if you need to.

    example curl request:

    ```bash
    curl -X 'DELETE' \
      'http://127.0.0.1:8000/currency-exchanges/67441be179a9ae30778b0df0' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTE4MjE3fQ.TY29rBpfyuuWd4K7a3wszmlINvZMF2OjSqUXhySJM2M'
    ```

    example response body:

    ```json
    {
    "message":"Currency exchange deleted successfully",
    "data":null,
    "timestamp":"2024-11-25T10:03:06.482411"
    }
    ```

</details>


<details>
<summary>Toggle Wallets Details</summary>

## Wallets

- First things first, to create a wallet for yourself, you need to know the ids of currencies in your wallet. So now let's get all the currencies, user-defined or predefined.

    example curl request:

    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/currencies' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNDYxMDYwfQ.C25hYQ8l5ZxWUC0AOfZa5vY4vXZVCS9x5SxQyNZHBdM'
    ```

    example response body:

    ```json
    {
      "message": "Currencies retrieved successfully",
      "data": {
        "currencies": [
          {
            "_id": "673b458b63f75539e9f1fcfe",
            "code": "USD",
            "name": "US Dollar",
            "symbol": "$",
            "is_predefined": true,
            "currency_type": "fiat",
            "created_at": "2024-11-18T13:47:55.569000",
            "updated_at": "2024-11-18T13:47:55.569000"
          },
          {
            "_id": "673b458b63f75539e9f1fcff",
            "code": "EUR",
            "name": "Euro",
            "symbol": "€",
            "is_predefined": true,
            "currency_type": "fiat",
            "created_at": "2024-11-18T13:47:55.572000",
            "updated_at": "2024-11-18T13:47:55.572000"
          }
        ]
      },
      "timestamp": "2024-11-24T17:03:14.290672"
    }
    ```

- **☝️** Now if you have the needed currency exchange rates, you can create a wallet with your desired currencies. Use the ids of currencies you want in your wallet in the `balances_ids` section of the request. Each wallet can have many balances holding different currencies, provide an initial amount for each. You should also provide a name and type of wallet. The type of wallet can either be “fiat” or “crypto”. You can create as many wallets as you want.

    example curl request:

    ```bash
    curl -X 'POST' \
      'http://127.0.0.1:8000/wallets' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuZXd1c2VybmFtZSIsImV4cCI6MTczMzIxNjgyMX0.UqtH9QiSStRFehA7FUHZ5AjLlBCPYh2KNTpzzKhTp98' \
      -H 'Content-Type: application/json' \
      -d '{
      "name": "Savings Wallet",
      "type": "fiat",
      "balances_ids": [
        {
          "amount": "100.50",
          "currency_id": "6745dbed6b99c20aab2de4e0"
        },
        {
          "amount": "200.75",
          "currency_id": "6745dbed6b99c20aab2de4e1"
        }
      ]
    }'
    ```

    example response body:

    ```json
    {
      "message": "Wallet created successfully",
      "data": {
        "id": {
          "_id": "674ec683b42bef228d9ac13d",
          "created_at": "2024-12-03T08:51:15.147000",
          "updated_at": "2024-12-03T08:51:15.147000",
          "user_id": "674ec06bb42bef228d9ac134",
          "name": "Savings Wallet",
          "type": "fiat",
          "balances_ids": [
            {
              "_id": "674ec683b42bef228d9ac13e",
              "wallet_id": "674ec683b42bef228d9ac13d",
              "currency_id": "6745dbed6b99c20aab2de4e0",
              "amount": 100.5
            },
            {
              "_id": "674ec683b42bef228d9ac13f",
              "wallet_id": "674ec683b42bef228d9ac13d",
              "currency_id": "6745dbed6b99c20aab2de4e1",
              "amount": 200.75
            }
          ],
          "total_value": "311.28750000000000000000"
        }
      },
      "timestamp": "2024-12-03T11:03:20.141111"
    }
    ```

- You can now operate typical CRUD operations on wallet models. Let's get all wallets a user created.

    example curl request:

    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/wallets' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuZXd1c2VybmFtZSIsImV4cCI6MTczMzIxNjgyMX0.UqtH9QiSStRFehA7FUHZ5AjLlBCPYh2KNTpzzKhTp98'
    ```

    example response body:

    ```json
    {
      "message": "Wallets retrieved successfully",
      "data": {
        "wallets": [
          {
            "_id": "674eca33b42bef228d9ac141",
            "created_at": "2024-12-03T09:06:59.850000",
            "updated_at": "2024-12-03T09:06:59.850000",
            "user_id": "674ec06bb42bef228d9ac134",
            "name": "Crypto Wallet",
            "type": "crypto",
            "balances_ids": [
              {
                "_id": "674eca33b42bef228d9ac142",
                "wallet_id": "674eca33b42bef228d9ac141",
                "currency_id": "6745dbed6b99c20aab2de4ea",
                "amount": 0.052
              }
            ],
            "total_value": "4940.0000000000"
          },
          {
            "_id": "674ec683b42bef228d9ac13d",
            "created_at": "2024-12-03T08:51:15.147000",
            "updated_at": "2024-12-03T08:51:15.147000",
            "user_id": "674ec06bb42bef228d9ac134",
            "name": "Savings Wallet",
            "type": "fiat",
            "balances_ids": [
              {
                "_id": "674ec683b42bef228d9ac13e",
                "wallet_id": "674ec683b42bef228d9ac13d",
                "currency_id": "6745dbed6b99c20aab2de4e0",
                "amount": 100.5
              },
              {
                "_id": "674ec683b42bef228d9ac13f",
                "wallet_id": "674ec683b42bef228d9ac13d",
                "currency_id": "6745dbed6b99c20aab2de4e1",
                "amount": 200.75
              }
            ],
            "total_value": "311.2875000000"
          }
        ]
      },
      "timestamp": "2024-12-03T11:03:20.141111"
    }
    ```

- Get a wallet by its id.

    example curl request:

    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/wallets/674eca33b42bef228d9ac141' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuZXd1c2VybmFtZSIsImV4cCI6MTczMzIxODY0M30.e-kYTmiWO1Ejn7feO0A-J2dlhA-bU1aFkrU6oDaDh6I'
    ```

    example response body:

    ```json
    {
      "message": "Wallet retrieved successfully",
      "data": {
        "wallet": {
          "_id": "674eca33b42bef228d9ac141",
          "created_at": "2024-12-03T09:06:59.850000",
          "updated_at": "2024-12-03T09:06:59.850000",
          "user_id": "674ec06bb42bef228d9ac134",
          "name": "Crypto Wallet",
          "type": "crypto",
          "balances_ids": [
            {
              "_id": "674eca33b42bef228d9ac142",
              "wallet_id": "674eca33b42bef228d9ac141",
              "currency_id": "6745dbed6b99c20aab2de4ea",
              "amount": 0.052
            }
          ],
          "total_value": "4940.0000000000"
        }
      },
      "timestamp": "2024-12-03T11:03:20.141111"
    }
    ```

- Update a wallet.

    example curl request:

    ```bash
    curl -X 'PUT' \
      'http://127.0.0.1:8000/wallets/674eca33b42bef228d9ac141' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuZXd1c2VybmFtZSIsImV4cCI6MTczMzIxODY0M30.e-kYTmiWO1Ejn7feO0A-J2dlhA-bU1aFkrU6oDaDh6I' \
      -H 'Content-Type: application/json' \
      -d '{
      "name": "Crypto ",
      "balances_ids": [
        {
          "amount": "0.041",
          "currency_id": "6745dbed6b99c20aab2de4ea"
        }
      ]
    }'
    ```

    example response body:

    ```json
    {
      "message": "Wallet updated successfully",
      "data": {
        "wallet": {
          "_id": "674eca33b42bef228d9ac141",
          "created_at": "2024-12-03T09:06:59.850000",
          "updated_at": "2024-12-03T09:10:27.328000",
          "user_id": "674ec06bb42bef228d9ac134",
          "name": "Crypto ",
          "type": "crypto",
          "balances_ids": [
            {
              "_id": "674eca33b42bef228d9ac142",
              "wallet_id": "674eca33b42bef228d9ac141",
              "currency_id": "6745dbed6b99c20aab2de4ea",
              "amount": 0.041
            }
          ],
          "total_value": "3895.0000000000"
        }
      },
      "timestamp": "2024-12-03T11:03:20.141111"
    }
    ```

- Delete a wallet.

    example curl request:

    ```bash
    curl -X 'DELETE' \
      'http://127.0.0.1:8000/wallets/67433e42fce3476d0b8c5de2' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTIxMTA3fQ.0Rw1sLpMbkwKXpgA55UxI__xQb6-DoenGUPcrtOIKkI'
    ```

    example response body:

    ```json
    {
      "message": "Wallet deleted successfully",
      "data": null,
      "timestamp": "2024-11-25T10:55:57.506591"
    }
    ```

- There is a route to get the total value of all your wallets. What this route does is to fetch all of your wallets and sum their balances. It does not rely on the `total-value` field in the wallet model, so it can be used to fix any possible inconsistencies.

    example curl request:

    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/wallets/total-value' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuZXd1c2VybmFtZSIsImV4cCI6MTczMzIxODY0M30.e-kYTmiWO1Ejn7feO0A-J2dlhA-bU1aFkrU6oDaDh6I'
    ```

    example response body:

    ```json
    {
      "message": "Total wallet value calculated successfully",
      "data": {
        "total_value": "4206.28750000000000000000"
      },
      "timestamp": "2024-12-03T11:03:20.141111"
    }
    ```

</details>


<details>
<summary>Toggle Balances Details</summary>

## Balances

- You can also add new currencies to your wallet. Let's say you have some JPY and you want it to be in a specific wallet. Use JPY’s id and the amount you have to add it to your wallet.

    example curl request:

    ```bash
    curl -X 'POST' \
      'http://127.0.0.1:8000/wallets/674ec683b42bef228d9ac13d/balance' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuZXd1c2VybmFtZSIsImV4cCI6MTczMzIxOTM2M30.ovAKzXI-w2lEfObbTThbF7H_sdUTBNKKH3LCjWJcdn0' \
      -H 'Content-Type: application/json' \
      -d '{
      "currency_id": "6745dbed6b99c20aab2de4e2",
      "amount": 20000
    }'
    ```

    example response body:

    ```json
    {
      "message": "Currency balance added successfully",
      "data": {
        "wallet": {
          "_id": "674ec683b42bef228d9ac13d",
          "created_at": "2024-12-03T08:51:15.147000",
          "updated_at": "2024-12-03T08:51:15.147000",
          "user_id": "674ec06bb42bef228d9ac134",
          "name": "Savings Wallet",
          "type": "fiat",
          "balances_ids": [
            {
              "_id": "674ec683b42bef228d9ac13e",
              "wallet_id": "674ec683b42bef228d9ac13d",
              "currency_id": "6745dbed6b99c20aab2de4e0",
              "amount": 100.5
            },
            {
              "_id": "674ec683b42bef228d9ac13f",
              "wallet_id": "674ec683b42bef228d9ac13d",
              "currency_id": "6745dbed6b99c20aab2de4e1",
              "amount": 200.75
            },
            {
              "_id": "674ecda7cfbbb34e5924be26",
              "wallet_id": "674ec683b42bef228d9ac13d",
              "currency_id": "6745dbed6b99c20aab2de4e2",
              "amount": 20000
            }
          ],
          "total_value": "445.2875000000"
        }
      },
      "timestamp": "2024-12-03T12:46:00.102914"
    }
    ```

- You can, of course, remove any unwanted balances too, providing wallet and currency ids.

    example curl request:

    ```bash
    curl -X 'DELETE' \
      'http://127.0.0.1:8000/wallets/674ec683b42bef228d9ac13d/balance/6745dbed6b99c20aab2de4e2' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuZXd1c2VybmFtZSIsImV4cCI6MTczMzIxOTM2M30.ovAKzXI-w2lEfObbTThbF7H_sdUTBNKKH3LCjWJcdn0'
    ```

    example response body:

    ```json
    {
      "message": "Currency balance removed successfully",
      "data": {
        "wallet": {
          "_id": "674ec683b42bef228d9ac13d",
          "created_at": "2024-12-03T08:51:15.147000",
          "updated_at": "2024-12-03T08:51:15.147000",
          "user_id": "674ec06bb42bef228d9ac134",
          "name": "Savings Wallet",
          "type": "fiat",
          "balances_ids": [
            {
              "_id": "674ec683b42bef228d9ac13e",
              "wallet_id": "674ec683b42bef228d9ac13d",
              "currency_id": "6745dbed6b99c20aab2de4e0",
              "amount": 100.5
            },
            {
              "_id": "674ec683b42bef228d9ac13f",
              "wallet_id": "674ec683b42bef228d9ac13d",
              "currency_id": "6745dbed6b99c20aab2de4e1",
              "amount": 200.75
            }
          ],
          "total_value": "311.2875000000"
        }
      },
      "timestamp": "2024-12-03T12:46:00.102914"
    }
    ```

</details>


<details>
<summary>Toggle Currencies Details</summary>

## Currencies

- We can also add our own custom currencies and modify them. For example, here we see there is no Tether in predefined currencies, so we can add it manually. The currency type can either be “fiat” or “crypto”. ⚠️ Also remember that whenever you introduce a new currency, add an exchange rate to the base currency instantly after that so you won’t face any problems later.

    example curl request:

    ```bash
    curl -X 'POST' \
      'http://127.0.0.1:8000/currencies' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTI2MjQxfQ.o1M5_oGcvqzTYXYrLdxB0O_pDpgXH2joB1FREH4nHlM' \
      -H 'Content-Type: application/json' \
      -d '{
      "code": "USDT",
      "name": "Tether",
      "symbol": "₮",
      "currency_type": "crypto"
    }'
    ```

    example response body:

    ```json
    {
      "message": "Currency created successfully",
      "data": {
        "id": {
          "_id": "67443a0d0edbf08cff819104",
          "user_id": "6743368dfce3476d0b8c5de0",
          "code": "USDT",
          "name": "Tether",
          "symbol": "₮",
          "is_predefined": false,
          "currency_type": "crypto",
          "created_at": "2024-11-25T08:49:17.641783",
          "updated_at": "2024-11-25T08:49:17.641791"
        }
      },
      "timestamp": "2024-11-25T12:19:07.545506"
    }
    ```

- You can see all currencies, custom or predefined, all together.

    example curl request:

    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/currencies' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTI2MjQxfQ.o1M5_oGcvqzTYXYrLdxB0O_pDpgXH2joB1FREH4nHlM'
    ```

    example response body:

    ```json
    {
    "message":"Currencies retrieved successfully",
    "data": {
    "currencies": [
          {
    "_id":"673b458b63f75539e9f1fcfe",
    "code":"USD",
    "name":"US Dollar",
    "symbol":"$",
    "is_predefined":true,
    "currency_type":"fiat",
    "created_at":"2024-11-18T13:47:55.569000",
    "updated_at":"2024-11-18T13:47:55.569000"
          },
          {
    "_id":"673b458b63f75539e9f1fcff",
    "code":"EUR",
    "name":"Euro",
    "symbol":"€",
    "is_predefined":true,
    "currency_type":"fiat",
    "created_at":"2024-11-18T13:47:55.572000",
    "updated_at":"2024-11-18T13:47:55.572000"
          },
          {
    "_id":"67443a0d0edbf08cff819104",
    "user_id":"6743368dfce3476d0b8c5de0",
    "code":"USDT",
    "name":"Tether",
    "symbol":"₮",
    "is_predefined":false,
    "currency_type":"crypto",
    "created_at":"2024-11-25T08:49:17.641000",
    "updated_at":"2024-11-25T08:49:17.641000"
          }
        ]
      },
    "timestamp":"2024-11-25T12:19:07.545506"
    }
    ```

- You can get one currency by id.

    example curl request:

    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/currencies/67443a0d0edbf08cff819104' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTI2MjQxfQ.o1M5_oGcvqzTYXYrLdxB0O_pDpgXH2joB1FREH4nHlM'
    ```

    example response body:

    ```json
    {
      "message": "Currency retrieved successfully",
      "data": {
        "currency": {
          "_id": "67443a0d0edbf08cff819104",
          "user_id": "6743368dfce3476d0b8c5de0",
          "code": "USDT",
          "name": "Tether",
          "symbol": "₮",
          "is_predefined": false,
          "currency_type": "crypto",
          "created_at": "2024-11-25T08:49:17.641000",
          "updated_at": "2024-11-25T08:49:17.641000"
        }
      },
      "timestamp": "2024-11-25T12:19:07.545506"
    }
    ```

- Update a currency if you will.

    example curl request:

    ```bash
    curl -X 'PUT' \
      'http://127.0.0.1:8000/currencies/67443a0d0edbf08cff819104' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTI2MjQxfQ.o1M5_oGcvqzTYXYrLdxB0O_pDpgXH2joB1FREH4nHlM' \
      -H 'Content-Type: application/json' \
      -d '{
      "code": "MUSDT",
      "name": "My Custom Tether",
      "symbol": "MT"
    }'
    ```

    example response body:

    ```json
    {
      "message": "Currency updated successfully",
      "data": {
        "currency": {
          "_id": "67443a0d0edbf08cff819104",
          "user_id": "6743368dfce3476d0b8c5de0",
          "code": "MUSDT",
          "name": "My Custom Tether",
          "symbol": "MT",
          "is_predefined": false,
          "currency_type": "crypto",
          "created_at": "2024-11-25T08:49:17.641000",
          "updated_at": "2024-11-25T08:49:17.641000"
        }
      },
      "timestamp": "2024-11-25T12:19:07.545506"
    }
    ```

- Delete a currency if you want
    
    example curl request: 
    
    ```bash
    curl -X 'DELETE' \
      'http://127.0.0.1:8000/currencies/67443a0d0edbf08cff819104' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTI2MjQxfQ.o1M5_oGcvqzTYXYrLdxB0O_pDpgXH2joB1FREH4nHlM'
    ```
    
    example response body:
    
    ```json
    {
      "message": "Currency deleted successfully",
      "data": null,
      "timestamp": "2024-11-25T12:19:07.545506"
    }
    ```
</details>

<details>
<summary>Toggle Transactions Details</summary>

## Transactions

- Now that we have created some wallets and exchanges we can move on to transactions
There are 3 types of transactions available; ***income***, ***expense*** and ***transfer***
you have to provide wallet ids according to the transaction you want to do, for example if you want to save an income transaction you have to only provide to_wallet_id
**☝️** you can add a category to your transaction, but if you wanted to do that, you had to have the category id, so you needed to make a get request to /category to get them all first or create your custom categories then provide the id here.
other fields are self explanatory.
In this example I have created an income transaction.
    
    example curl request: 
    
    ```bash
    curl -X 'POST' \
      'http://127.0.0.1:8000/transactions' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTM2MjExfQ.k_XFzUZa3CPUPdNUM8bGf8dke_SyrgrSiTuePUCurhQ' \
      -H 'Content-Type: application/json' \
      -d '{
      "to_wallet_id": "67433c81fce3476d0b8c5de1",
      "currency_id": "673b458b63f75539e9f1fcff",
      "type": "income",
      "amount": 100,
      "description": "The gig income"
    }'
    ```
    
    example response body:
    
    ```json
    {
      "message": "Transaction created successfully",
      "data": {
        "id": {
          "_id": "67446180dde2b8e5a723ef69",
          "user_id": "6743368dfce3476d0b8c5de0",
          "to_wallet_id": "67433c81fce3476d0b8c5de1",
          "currency_id": "673b458b63f75539e9f1fcff",
          "type": "income",
          "amount": 100,
          "date": "2024-11-25T11:37:36.425015",
          "description": "The gig income"
        }
      },
      "timestamp": "2024-11-25T15:07:32.034183"
    }
    ```
    
- an example of expense transaction
    
    
    example curl request: 
    
    ```bash
    curl -X 'POST' \
      'http://127.0.0.1:8000/transactions' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTM2MjExfQ.k_XFzUZa3CPUPdNUM8bGf8dke_SyrgrSiTuePUCurhQ' \
      -H 'Content-Type: application/json' \
      -d '{
      "from_wallet_id": "67433c81fce3476d0b8c5de1",
      "currency_id": "673b458b63f75539e9f1fcff",
      "type": "expense",
      "amount": 50,
      "description": "groceries"
    }'
    ```
    
    example response body:
    
    ```json
    {
      "message": "Transaction created successfully",
      "data": {
        "id": {
          "_id": "6744637ddde2b8e5a723ef6b",
          "user_id": "6743368dfce3476d0b8c5de0",
          "from_wallet_id": "67433c81fce3476d0b8c5de1",
          "currency_id": "673b458b63f75539e9f1fcff",
          "type": "expense",
          "amount": 50,
          "date": "2024-11-25T11:46:05.868121",
          "description": "groceries"
        }
      },
      "timestamp": "2024-11-25T15:07:32.034183"
    }
    ```
    
- an example of transfer transaction
    
    
    example curl request: 
    
    ```bash
    curl -X 'POST' \
      'http://127.0.0.1:8000/transactions' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTM2MjExfQ.k_XFzUZa3CPUPdNUM8bGf8dke_SyrgrSiTuePUCurhQ' \
      -H 'Content-Type: application/json' \
      -d '{
      "from_wallet_id": "67433c81fce3476d0b8c5de1",
      "to_wallet_id": "67446414dde2b8e5a723ef6c",
      "currency_id": "673b458b63f75539e9f1fcfe",
      "type": "transfer",
      "amount": 150,
      "description": "transfer to bank"
    }'
    ```
    
    example response body:
    
    ```json
    {
      "message": "Transaction created successfully",
      "data": {
        "id": {
          "_id": "674464dddde2b8e5a723ef70",
          "user_id": "6743368dfce3476d0b8c5de0",
          "from_wallet_id": "67433c81fce3476d0b8c5de1",
          "to_wallet_id": "67446414dde2b8e5a723ef6c",
          "currency_id": "673b458b63f75539e9f1fcfe",
          "type": "transfer",
          "amount": 150,
          "date": "2024-11-25T11:51:57.525552",
          "description": "transfer to bank"
        }
      },
      "timestamp": "2024-11-25T15:07:32.034183"
    }
    ```
    
- Lets try basic CRUD operations
get all transactions
    
    
    example curl request: 
    
    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/transactions' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTM2MjExfQ.k_XFzUZa3CPUPdNUM8bGf8dke_SyrgrSiTuePUCurhQ'
    ```
    
    example response body:
    
    ```json
    {
      "message": "Transactions retrieved successfully",
      "data": {
        "transactions": [
          {
            "_id": "67446180dde2b8e5a723ef69",
            "user_id": "6743368dfce3476d0b8c5de0",
            "to_wallet_id": "67433c81fce3476d0b8c5de1",
            "currency_id": "673b458b63f75539e9f1fcff",
            "type": "income",
            "amount": 100,
            "date": "2024-11-25T11:37:36.425000",
            "description": "The gig income"
          },
          {
            "_id": "67446365dde2b8e5a723ef6a",
            "user_id": "6743368dfce3476d0b8c5de0",
            "from_wallet_id": "67433c81fce3476d0b8c5de1",
            "currency_id": "673b458b63f75539e9f1fcff",
            "type": "expense",
            "amount": 50,
            "date": "2024-11-25T11:45:41.878000",
            "description": "groceries"
          },
          {
            "_id": "674464dddde2b8e5a723ef70",
            "user_id": "6743368dfce3476d0b8c5de0",
            "from_wallet_id": "67433c81fce3476d0b8c5de1",
            "to_wallet_id": "67446414dde2b8e5a723ef6c",
            "currency_id": "673b458b63f75539e9f1fcfe",
            "type": "transfer",
            "amount": 150,
            "date": "2024-11-25T11:51:57.525000",
            "description": "transfer to bank"
          }
        ]
      },
      "timestamp": "2024-11-25T15:07:32.034183"
    }
    ```
    
- get a specific transaction details
    
    example curl request: 
    
    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/transactions/674464dddde2b8e5a723ef70' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTM2MjExfQ.k_XFzUZa3CPUPdNUM8bGf8dke_SyrgrSiTuePUCurhQ'
    ```
    
    example response body:
    
    ```json
    {
    "message":"Transaction retrieved successfully",
    "data": {
    "transaction": {
    "_id":"674464dddde2b8e5a723ef70",
    "user_id":"6743368dfce3476d0b8c5de0",
    "from_wallet_id":"67433c81fce3476d0b8c5de1",
    "to_wallet_id":"67446414dde2b8e5a723ef6c",
    "currency_id":"673b458b63f75539e9f1fcfe",
    "type":"transfer",
    "amount":150,
    "date":"2024-11-25T11:51:57.525000",
    "description":"transfer to bank"
        }
      },
    "timestamp":"2024-11-25T15:07:32.034183"
    }
    ```
    
    ---
    
- Update a transaction
you can only update category, amount, date and description.
    
    
    example curl request: 
    
    ```bash
    curl -X 'PUT' \
      'http://127.0.0.1:8000/transactions/67446bdcf5fbebe2b05a95b5' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTM4NDM5fQ.nEfDm-U4m-I_u4zfYWzSpp1E3q5xGlIaHBEf9JX31mg' \
      -H 'Content-Type: application/json' \
      -d '{
      "amount": 60,
      "date": "2023-10-15T14:30:00Z",
      "description": "Transfer to main bank"
    }'
    ```
    
    example response body:
    
    ```json
    {
      "message": "Transaction updated successfully",
      "data": {
        "transaction": {
          "_id": "67446bdcf5fbebe2b05a95b5",
          "user_id": "6743368dfce3476d0b8c5de0",
          "from_wallet_id": "67433c81fce3476d0b8c5de1",
          "to_wallet_id": "67446414dde2b8e5a723ef6c",
          "currency_id": "673b458b63f75539e9f1fcfe",
          "type": "transfer",
          "amount": 60,
          "date": "2023-10-15T14:30:00",
          "description": "Transfer to main bank"
        }
      },
      "timestamp": "2024-11-25T16:02:00.761796"
    }
    ```
    
- Delete a transaction
    
    
    example curl request: 
    
    ```bash
    curl -X 'DELETE' \
      'http://127.0.0.1:8000/transactions/674464dddde2b8e5a723ef70' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTQwODM4fQ.vltdoHbI0AxVSyKVfeN2dIN-vg1Pl7Tevei9l2b_8Js'
    ```
    
    example response body:
    
    ```json
    {
    "message":"Transaction deleted successfully",
    "data":null,
    "timestamp":"2024-11-25T16:18:22.168932"
    }
    ```
    
- You can get basic statistics about the transactions occurred in a specific period of time
    
    
    example curl request: 
    
    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/transactions/statistics?start_date=2020-01-01&end_date=2024-12-01' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTQwODM4fQ.vltdoHbI0AxVSyKVfeN2dIN-vg1Pl7Tevei9l2b_8Js'
    ```
    
    example response body:
    
    ```json
    {
    "message":"Transaction statistics retrieved successfully",
    "data": {
    "statistics": {
    "total_income":"150.0100000000",
    "total_expense":"100.0000000000",
    "net_balance":"50.0100000000"
        }
      },
    "timestamp":"2024-11-25T16:18:22.168932"
    }
    ```
    
- Can filter transactions too
    
    
    example curl request: 
    
    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/transactions/filter?start_date=2020-01-01&end_date=2024-12-01&transaction_type=expense&from_wallet_id=67433c81fce3476d0b8c5de1' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTQwODM4fQ.vltdoHbI0AxVSyKVfeN2dIN-vg1Pl7Tevei9l2b_8Js'
    ```
    
    example response body:
    
    ```json
    {
      "message": "Filtered transactions retrieved successfully",
      "data": {
        "transactions": [
          {
            "_id": "67446365dde2b8e5a723ef6a",
            "user_id": "6743368dfce3476d0b8c5de0",
            "from_wallet_id": "67433c81fce3476d0b8c5de1",
            "currency_id": "673b458b63f75539e9f1fcff",
            "type": "expense",
            "amount": 50,
            "date": "2024-11-25T11:45:41.878000",
            "description": "groceries"
          }
        ]
      },
      "timestamp": "2024-11-25T16:18:22.168932"
    }
    ```
</details>

<details>
<summary>Toggle Category Details</summary>

## Category

- Create a category
choose the type of transaction this category can apply to
    
    
    example curl request: 
    
    ```bash
    curl -X 'POST' \
      'http://127.0.0.1:8000/categories' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTQ4ODk5fQ.WRpaHJMwABv4_f7oFnQINK_-bE6rdB5onf4n1FIBvUU' \
      -H 'Content-Type: application/json' \
      -d '{
      "name": "My Groceries",
      "type": "expense",
      "description": "Necessary Grocery shoppings"
    }'
    ```
    
    example response body:
    
    ```json
    {
      "message": "Category created successfully",
      "data": {
        "id": {
          "_id": "674498e78e2d631a0ab55028",
          "user_id": "6743368dfce3476d0b8c5de0",
          "name": "My Groceries",
          "type": "expense",
          "description": "Necessary Grocery shoppings",
          "is_predefined": false
        }
      },
      "timestamp": "2024-11-25T19:03:18.045518"
    }
    ```
    
- Get all categories
    
    example curl request: 
    
    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/categories' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTUwODA1fQ.yb7qLp1MX6YeyqiXPKzKyEzSkRlBOjUo16v4mpWxsAQ'
    ```
    
    example response body:
    
    ```json
    {
      "message": "Categories retrieved successfully",
      "data": {
        "categories": [
          {
            "_id": "673b473de5b094d9f735d2a7",
            "name": "Salary",
            "type": "income",
            "is_predefined": true
          },
          {
            "_id": "673b473de5b094d9f735d2aa",
            "name": "Rent",
            "type": "expense",
            "is_predefined": true
          }
          {
            "_id": "673b473de5b094d9f735d2ac",
            "name": "Bank Transfer",
            "type": "transfer",
            "is_predefined": true
          },
          {
            "_id": "674498e78e2d631a0ab55028",
            "user_id": "6743368dfce3476d0b8c5de0",
            "name": "My Groceries",
            "type": "expense",
            "description": "Necessary Grocery shoppings",
            "is_predefined": false
          }
        ]
      },
      "timestamp": "2024-11-25T19:03:18.045518"
    }
    ```
    
- Get one category
    
    
    example curl request: 
    
    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/categories/673b473de5b094d9f735d2ac' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTUwODA1fQ.yb7qLp1MX6YeyqiXPKzKyEzSkRlBOjUo16v4mpWxsAQ'
    ```
    
    example response body:
    
    ```json
    {
      "message": "Category retrieved successfully",
      "data": {
        "category": {
          "_id": "673b473de5b094d9f735d2ac",
          "name": "Bank Transfer",
          "type": "transfer",
          "is_predefined": true
        }
      },
      "timestamp": "2024-11-25T19:03:18.045518"
    }
    ```
    
- Update a category
    
    
    example curl request: 
    
    ```bash
    curl -X 'PUT' \
      'http://127.0.0.1:8000/categories/674498e78e2d631a0ab55028' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTUxMzk4fQ.-g3lHD4HxtLn8Wmcj8g7WDkc5P8L3r0oNfFg1KmfVis' \
      -H 'Content-Type: application/json' \
      -d '{
      "name": "My Necessary Groceries",
      "description": "Necessary Grocery shoppings"
    }'
    ```
    
    example response body:
    
    ```json
    {
      "message": "Category updated successfully",
      "data": {
        "category": {
          "_id": "674498e78e2d631a0ab55028",
          "user_id": "6743368dfce3476d0b8c5de0",
          "name": "My Necessary Groceries",
          "type": "transfer",
          "description": "Necessary Grocery shoppings",
          "is_predefined": false
        }
      },
      "timestamp": "2024-11-25T19:16:16.859504"
    }
    ```
    
- Delete a category
    
    
    example curl request: 
    
    ```bash
    curl -X 'DELETE' \
      'http://127.0.0.1:8000/categories/674498e78e2d631a0ab55028' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTUxMzk4fQ.-g3lHD4HxtLn8Wmcj8g7WDkc5P8L3r0oNfFg1KmfVis'
    ```
    
    example response body:
    
    ```json
    {
      "message": "Category deleted successfully",
      "data": null,
      "timestamp": "2024-11-25T19:16:16.859504"
    }
    ```
    
</details>

<details>
<summary>Toggle Asset Type Details</summary>

## Asset Type

- You can create some asset types if you want
    
    
    example curl request: 
    
    ```bash
    curl -X 'POST' \
      'http://127.0.0.1:8000/asset-types' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTUzMzk0fQ.sOtC28zDZSqYneKXsYwNoGD7zwMcdBwboGkfRCF99Co' \
      -H 'Content-Type: application/json' \
      -d '{
      "name": "Jewelry",
      "description": "My Jewelries"
    }'
    ```
    
    example response body:
    
    ```json
    {
      "message": "Asset type created successfully",
      "data": {
        "id": {
          "_id": "6744a6e4cc384c4f59041c0a",
          "user_id": "6743368dfce3476d0b8c5de0",
          "name": "Jewelry",
          "description": "My Jewelries",
          "is_predefined": false
        }
      },
      "timestamp": "2024-11-25T20:02:13.181693"
    }
    ```
    
- Get all asset types
    
    example curl request: 
    
    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/asset-types' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTUzMzk0fQ.sOtC28zDZSqYneKXsYwNoGD7zwMcdBwboGkfRCF99Co'
    ```
    
    example response body:
    
    ```json
    {
      "message": "Asset types retrieved successfully",
      "data": {
        "asset_types": [
          {
            "_id": "673b473de5b094d9f735d2a2",
            "name": "Real Estate",
            "is_predefined": true
          },
          {
            "_id": "673b473de5b094d9f735d2a3",
            "name": "Vehicle",
            "is_predefined": true
          },
          {
            "_id": "6744a6e4cc384c4f59041c0a",
            "user_id": "6743368dfce3476d0b8c5de0",
            "name": "Jewelry",
            "description": "My Jewelries",
            "is_predefined": false
          }
        ]
      },
      "timestamp": "2024-11-25T20:02:13.181693"
    }
    ```
    
- Get an asset type
    
    example curl request: 
    
    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/asset-types/6744a6e4cc384c4f59041c0a' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTUzMzk0fQ.sOtC28zDZSqYneKXsYwNoGD7zwMcdBwboGkfRCF99Co'
    ```
    
    example response body:
    
    ```json
    {
      "message": "Asset type retrieved successfully",
      "data": {
        "asset_type": {
          "_id": "6744a6e4cc384c4f59041c0a",
          "user_id": "6743368dfce3476d0b8c5de0",
          "name": "Jewelry",
          "description": "My Jewelries",
          "is_predefined": false
        }
      },
      "timestamp": "2024-11-25T20:02:13.181693"
    }
    ```
    
- Update an asset type
    
    example curl request: 
    
    ```bash
    curl -X 'PUT' \
      'http://127.0.0.1:8000/asset-types/6744a6e4cc384c4f59041c0a' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTUzMzk0fQ.sOtC28zDZSqYneKXsYwNoGD7zwMcdBwboGkfRCF99Co' \
      -H 'Content-Type: application/json' \
      -d '{
      "name": "Gold Jewelries",
      "description": "My Gold Jewelries"
    }'
    ```
    
    example response body:
    
    ```json
    {
      "message": "Asset type updated successfully",
      "data": {
        "asset_type": {
          "_id": "6744a6e4cc384c4f59041c0a",
          "user_id": "6743368dfce3476d0b8c5de0",
          "name": "Gold Jewelries",
          "description": "My Gold Jewelries",
          "is_predefined": false
        }
      },
      "timestamp": "2024-11-25T20:02:13.181693"
    }
    ```
    
- Delete an asset type
    
    
    example curl request: 
    
    ```bash
    curl -X 'DELETE' \
      'http://127.0.0.1:8000/asset-types/6744a4e92d20832685ff0c06' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTUzMzk0fQ.sOtC28zDZSqYneKXsYwNoGD7zwMcdBwboGkfRCF99Co'
    ```
    
    example response body:
    
    ```json
    {
      "message": "Asset type deleted successfully",
      "data": null,
      "timestamp": "2024-11-25T19:56:10.083441"
    }
    ```

</details>

<details>
<summary>Toggle Asset Details</summary>

## Asset

- You can add your other valuable stuff as assets
lets create an asset here
    
    example curl request: 
    
    ```bash
    curl -X 'POST' \
      'http://127.0.0.1:8000/assets' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTU1NDE4fQ.OgdhrOhpZMdcZQGXU79pGFyGTsdtwBQxCBwu_r0pLBs' \
      -H 'Content-Type: application/json' \
      -d '{
      "asset_type_id": "673b473de5b094d9f735d2a2",
      "currency_id": "673b458b63f75539e9f1fcfe",
      "name": "Family Home",
      "description": "A beautiful house in the suburbs",
      "value": 350000,
      "created_at": "2023-10-15T14:30:00Z"
    }'
    ```
    
    example response body:
    
    ```json
    
      "message": "Asset created successfully",
      "data": {
        "id": {
          "_id": "6744abc3cc384c4f59041c0b",
          "user_id": "6743368dfce3476d0b8c5de0",
          "asset_type_id": "673b473de5b094d9f735d2a2",
          "currency_id": "673b458b63f75539e9f1fcfe",
          "name": "Family Home",
          "description": "A beautiful house in the suburbs",
          "value": 350000,
          "created_at": "2024-11-25T16:54:27.526642",
          "updated_at": "2024-11-25T16:54:27.526654"
        }
      },
      "timestamp": "2024-11-25T20:02:13.181693"
    }
    ```
    
- Get all assets of yours
    
    example curl request: 
    
    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/assets' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTU1NDE4fQ.OgdhrOhpZMdcZQGXU79pGFyGTsdtwBQxCBwu_r0pLBs'
    ```
    
    example response body:
    
    ```json
    {
      "message": "Assets retrieved successfully",
      "data": {
        "assets": [
          {
            "_id": "6744abc3cc384c4f59041c0b",
            "user_id": "6743368dfce3476d0b8c5de0",
            "asset_type_id": "673b473de5b094d9f735d2a2",
            "currency_id": "673b458b63f75539e9f1fcfe",
            "name": "Family Home",
            "description": "A beautiful house in the suburbs",
            "value": 350000,
            "created_at": "2024-11-25T16:54:27.526000",
            "updated_at": "2024-11-25T16:54:27.526000"
          }
        ]
      },
      "timestamp": "2024-11-25T20:02:13.181693"
    }
    ```
    
- Get an asset
    
    example curl request: 
    
    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/assets/6744abc3cc384c4f59041c0b' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTU1NDE4fQ.OgdhrOhpZMdcZQGXU79pGFyGTsdtwBQxCBwu_r0pLBs'
    ```
    
    example response body:
    
    ```json
    {
      "message": "Asset retrieved successfully",
      "data": {
        "asset": {
          "_id": "6744abc3cc384c4f59041c0b",
          "user_id": "6743368dfce3476d0b8c5de0",
          "asset_type_id": "673b473de5b094d9f735d2a2",
          "currency_id": "673b458b63f75539e9f1fcfe",
          "name": "Family Home",
          "description": "A beautiful house in the suburbs",
          "value": 350000,
          "created_at": "2024-11-25T16:54:27.526000",
          "updated_at": "2024-11-25T16:54:27.526000"
        }
      },
      "timestamp": "2024-11-25T20:02:13.181693"
    }
    ```
    
- Update an asset
    
    example curl request: 
    
    ```bash
    curl -X 'PUT' \
      'http://127.0.0.1:8000/assets/6744abc3cc384c4f59041c0b' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTU1NDE4fQ.OgdhrOhpZMdcZQGXU79pGFyGTsdtwBQxCBwu_r0pLBs' \
      -H 'Content-Type: application/json' \
      -d '{
      "currency_id": "673b458b63f75539e9f1fcff",
      "name": "Family Home",
      "description": "My beautiful house in the suburbs",
      "value": 350000,
      "updated_at": "2023-11-15T14:30:00Z"
    }'
    ```
    
    example response body:
    
    ```json
    {
      "message": "Asset updated successfully",
      "data": {
        "asset": {
          "_id": "6744abc3cc384c4f59041c0b",
          "user_id": "6743368dfce3476d0b8c5de0",
          "asset_type_id": "673b473de5b094d9f735d2a2",
          "currency_id": "673b458b63f75539e9f1fcff",
          "name": "Family Home",
          "description": "My beautiful house in the suburbs",
          "value": 350000,
          "created_at": "2024-11-25T16:54:27.526000",
          "updated_at": "2024-11-25T16:58:39.022000"
        }
      },
      "timestamp": "2024-11-25T20:02:13.181693"
    }
    ```
    
- Filter assets
you can search in your assets here
    
    example curl request: 
    
    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/assets/filter?name=Home&created_at_start=2020-01-01&created_at_end=2024-12-01' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTU1NDE4fQ.OgdhrOhpZMdcZQGXU79pGFyGTsdtwBQxCBwu_r0pLBs'
    ```
    
    example response body:
    
    ```json
    {
      "message": "Filtered assets retrieved successfully",
      "data": {
        "assets": [
          {
            "_id": "6744abc3cc384c4f59041c0b",
            "user_id": "6743368dfce3476d0b8c5de0",
            "asset_type_id": "673b473de5b094d9f735d2a2",
            "currency_id": "673b458b63f75539e9f1fcff",
            "name": "Family Home",
            "description": "My beautiful house in the suburbs",
            "value": 350000,
            "created_at": "2024-11-25T16:54:27.526000",
            "updated_at": "2024-11-25T16:58:39.022000"
          }
        ]
      },
      "timestamp": "2024-11-25T20:02:13.181693"
    }
    ```
    
- You can get total value of all of your assets converted to your base currency
    
    example curl request: 
    
    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/assets/total-value' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTU1NDE4fQ.OgdhrOhpZMdcZQGXU79pGFyGTsdtwBQxCBwu_r0pLBs'
    ```
    
    example response body:
    
    ```json
    {
      "message": "Total asset value calculated successfully",
      "data": {
        "total_value": "367500.00000000000000000000"
      },
      "timestamp": "2024-11-25T20:02:13.181693"
    }
    ```
    
- Finally you can delete an asset
    
    example curl request: 
    
    ```bash
    curl -X 'DELETE' \
      'http://127.0.0.1:8000/assets/6744abc3cc384c4f59041c0b' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTU1NDE4fQ.OgdhrOhpZMdcZQGXU79pGFyGTsdtwBQxCBwu_r0pLBs'
    ```
    
    example response body:
    
    ```json
    {
      "message": "Asset deleted successfully",
      "data": null,
      "timestamp": "2024-11-25T20:02:13.181693"
    }
    ```

</details>

<details>
<summary>Toggle User App Data Details</summary>

## User App Data

Each user has an user_app_data record to save some user related content

- You can get your data
    
    example curl request: 
    
    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/user-app-data/user-data' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTU1NDE4fQ.OgdhrOhpZMdcZQGXU79pGFyGTsdtwBQxCBwu_r0pLBs'
    ```
    
    example response body:
    
    ```json
    
      "message": "User app data retrieved successfully",
      "data": {
        "_id": "6743368dfce3476d0b8c5ddf",
        "base_currency_id": "673b458b63f75539e9f1fcfe",
        "net_worth": 102587.5,
        "assets_value": 0,
        "wallets_value": 102587.5,
        "created_at": "2024-11-24T14:22:05.038000",
        "updated_at": "2024-11-25T17:10:05.898000"
      },
      "timestamp": "2024-11-25T20:02:13.181693"
    }
    ```
    
- You can tell the app to calculate your net-worth
it processes all of your data at the time of request to calculate the values
    
    example curl request: 
    
    ```bash
    curl -X 'GET' \
      'http://127.0.0.1:8000/user-app-data/net-worth' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTU1NDE4fQ.OgdhrOhpZMdcZQGXU79pGFyGTsdtwBQxCBwu_r0pLBs'
    ```
    
    example response body:
    
    ```json
    {
      "message": "Net worth calculated successfully",
      "data": {
        "net_worth": "102587.50000000000000000000"
      },
      "timestamp": "2024-11-25T20:02:13.181693"
    }
    ```
    
- One special thing about this app is that you can change your base currency easily
**☝️** Just before adding the new base currency you need to add the necessary exchange rates
    
    example curl request: 
    
    ```bash
    curl -X 'POST' \
      'http://127.0.0.1:8000/user-app-data/change-base-currency/673b458b63f75539e9f1fcff' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzMyNTU4NTY2fQ.SBWpKc_NqJR4pjZx423NdDjkgGwByVBPOgm1aIgIQ6c' \
      -d ''
    ```
    
    example response body:
    
    ```json
    {
      "message": "Base currency changed successfully",
      "data": {
        "_id": "6743368dfce3476d0b8c5ddf",
        "base_currency_id": "673b458b63f75539e9f1fcff",
        "net_worth": 97865.4761904762,
        "assets_value": 0,
        "wallets_value": 97865.4761904762,
        "created_at": "2024-11-24T14:22:05.038000",
        "updated_at": "2024-11-25T17:59:27.099520"
      },
      "timestamp": "2024-11-25T21:29:00.265961"
    }
    ```
</details>


## Navigation Panel

Use the links below to navigate between different sections of the documentation:

- [Main README](/README.md)
- [Step by Step Guide](/docs/README-GUIDE.md)
- [Developer Documentation](/docs/README-DEV.md)
- [Models Documentation](/docs/README-MODELS.md)
