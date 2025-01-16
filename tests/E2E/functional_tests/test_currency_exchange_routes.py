from datetime import datetime, timezone
from decimal import Decimal

import pytest
from mongoengine import DoesNotExist

from models.models import Currency, CurrencyExchange, User


@pytest.fixture(scope="function", autouse=True)
async def cleanup_currency_exchanges(db):
    yield
    CurrencyExchange.objects().delete()


@pytest.fixture(scope="session", autouse=True)
async def ensure_test_currencies(db):
    test_currencies = [
        {
            "code": "USD",
            "name": "US Dollar",
            "symbol": "$",
            "currency_type": "fiat",
            "is_predefined": True,
        },
        {
            "code": "EUR",
            "name": "Euro",
            "symbol": "€",
            "currency_type": "fiat",
            "is_predefined": True,
        },
        {
            "code": "GBP",
            "name": "British Pound",
            "symbol": "£",
            "currency_type": "fiat",
            "is_predefined": True,
        },
    ]

    for currency_data in test_currencies:
        if not Currency.objects(code=currency_data["code"]).first():
            Currency(**currency_data).save()
    yield


@pytest.mark.asyncio
class TestCurrencyExchangeRoutesSetup:
    async def _create_test_exchange(
        self, test_user: User, **overrides
    ) -> CurrencyExchange:
        """Helper method to create a test currency exchange"""

        usd = Currency.objects(code="USD").first()
        eur = Currency.objects(code="EUR").first()

        exchange_data = {
            "user_id": test_user.id,
            "from_currency_id": usd.id,
            "to_currency_id": eur.id,
            "rate": Decimal("0.85"),
            "date": datetime.now(timezone.utc),
        }
        exchange_data.update(overrides)
        exchange = CurrencyExchange(**exchange_data).save()
        return exchange

    def _get_test_exchange_data(self, **overrides) -> dict:

        usd = Currency.objects(code="USD").first()
        eur = Currency.objects(code="EUR").first()

        exchange_data = {
            "from_currency_id": str(usd.id),
            "to_currency_id": str(eur.id),
            "rate": 0.85,
            "date": datetime.now(timezone.utc).isoformat(),
        }
        exchange_data.update(overrides)
        return exchange_data


@pytest.mark.asyncio
class TestCreateCurrencyExchangeRoutePositive(TestCurrencyExchangeRoutesSetup):
    """Happy path tests for currency exchange creation"""

    async def test_create_currency_exchange_success(self, client, auth_headers):
        """Test creating a currency exchange with valid data."""
        exchange_data = self._get_test_exchange_data()

        response = client.post(
            "/currency-exchanges", json=exchange_data, headers=auth_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "id" in response_data["data"]
        assert response_data["message"] == "Currency exchange created successfully"

    async def test_create_currency_exchange_different_pairs(self, client, auth_headers):
        """Test creating currency exchanges with different currency pairs."""
        gbp = Currency.objects(code="GBP").first()
        eur = Currency.objects(code="EUR").first()

        exchange_data = self._get_test_exchange_data(
            from_currency_id=str(gbp.id), to_currency_id=str(eur.id), rate=1.15
        )

        response = client.post(
            "/currency-exchanges", json=exchange_data, headers=auth_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "id" in response_data["data"]
        assert response_data["message"] == "Currency exchange created successfully"

    async def test_create_currency_exchange_with_future_date(
        self, client, auth_headers
    ):
        """Test creating a currency exchange with a future date."""
        future_date = datetime(2025, 1, 1)
        exchange_data = self._get_test_exchange_data(date=future_date.isoformat())

        response = client.post(
            "/currency-exchanges", json=exchange_data, headers=auth_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "id" in response_data["data"]
        assert response_data["message"] == "Currency exchange created successfully"

    async def test_create_currency_exchange_with_high_precision_rate(
        self, client, auth_headers
    ):
        """Test creating a currency exchange with high precision rate."""
        exchange_data = self._get_test_exchange_data(rate=0.12345678)

        response = client.post(
            "/currency-exchanges", json=exchange_data, headers=auth_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "id" in response_data["data"]
        assert response_data["message"] == "Currency exchange created successfully"

    async def test_create_currency_exchange_with_rate_above_one(
        self, client, auth_headers
    ):
        """Test creating a currency exchange with rate above 1."""
        exchange_data = self._get_test_exchange_data(rate=1.25)

        response = client.post(
            "/currency-exchanges", json=exchange_data, headers=auth_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "id" in response_data["data"]
        assert response_data["message"] == "Currency exchange created successfully"

    async def test_create_currency_exchange_with_past_date(self, client, auth_headers):
        """Test creating a currency exchange with a past date."""
        past_date = datetime(2023, 1, 1)
        exchange_data = self._get_test_exchange_data(date=past_date.isoformat())

        response = client.post(
            "/currency-exchanges", json=exchange_data, headers=auth_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "id" in response_data["data"]
        assert response_data["message"] == "Currency exchange created successfully"


@pytest.mark.asyncio
class TestReadCurrencyExchangeRoutePositive(TestCurrencyExchangeRoutesSetup):
    """Happy path tests for reading a single currency exchange"""

    async def test_read_currency_exchange_basic(self, client, auth_headers, test_user):
        """Test reading a specific currency exchange with basic data."""
        exchange = await self._create_test_exchange(test_user)

        response = client.get(
            f"/currency-exchanges/{str(exchange.id)}", headers=auth_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "currency_exchange" in response_data["data"]
        assert (
            str(exchange.from_currency_id.id)
            == response_data["data"]["currency_exchange"]["from_currency_id"]
        )
        assert response_data["message"] == "Currency exchange retrieved successfully"

    async def test_read_currency_exchange_with_different_currencies(
        self, client, auth_headers, test_user
    ):
        """Test reading a currency exchange with different currency pairs."""
        gbp = Currency.objects(code="GBP").first()
        eur = Currency.objects(code="EUR").first()

        exchange = await self._create_test_exchange(
            test_user,
            from_currency_id=gbp.id,
            to_currency_id=eur.id,
            rate=Decimal("1.15"),
        )

        response = client.get(
            f"/currency-exchanges/{str(exchange.id)}", headers=auth_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        exchange_data = response_data["data"]["currency_exchange"]
        assert str(gbp.id) == exchange_data["from_currency_id"]
        assert str(eur.id) == exchange_data["to_currency_id"]
        assert exchange_data["rate"] == 1.15

    async def test_read_currency_exchange_with_future_date(
        self, client, auth_headers, test_user
    ):
        """Test reading a currency exchange with a future date."""
        future_date = datetime(2025, 1, 1)
        exchange = await self._create_test_exchange(test_user, date=future_date)

        response = client.get(
            f"/currency-exchanges/{str(exchange.id)}", headers=auth_headers
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["data"]["currency_exchange"]["date"].startswith(
            "2025-01-01"
        )


@pytest.mark.asyncio
class TestReadAllCurrencyExchangesRoutePositive(TestCurrencyExchangeRoutesSetup):
    """Happy path tests for reading all currency exchanges"""

    async def test_read_all_currency_exchanges_empty(self, client, auth_headers):
        """Test reading all currency exchanges when none exist."""
        response = client.get("/currency-exchanges", headers=auth_headers)

        assert response.status_code == 200
        response_data = response.json()
        assert "currency_exchanges" in response_data["data"]
        assert len(response_data["data"]["currency_exchanges"]) == 0
        assert response_data["message"] == "Currency exchanges retrieved successfully"

    async def test_read_all_currency_exchanges_multiple(
        self, client, auth_headers, test_user
    ):
        """Test reading multiple currency exchanges."""
        usd = Currency.objects(code="USD").first()
        eur = Currency.objects(code="EUR").first()
        gbp = Currency.objects(code="GBP").first()

        exchanges = [
            await self._create_test_exchange(
                test_user, from_currency_id=usd.id, to_currency_id=eur.id
            ),
            await self._create_test_exchange(
                test_user, from_currency_id=eur.id, to_currency_id=gbp.id
            ),
            await self._create_test_exchange(
                test_user, from_currency_id=gbp.id, to_currency_id=usd.id
            ),
        ]

        response = client.get("/currency-exchanges", headers=auth_headers)

        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["data"]["currency_exchanges"]) == len(exchanges)

    async def test_read_all_currency_exchanges_different_pairs(
        self, client, auth_headers, test_user
    ):
        """Test reading currency exchanges with different currency pairs."""
        usd = Currency.objects(code="USD").first()
        eur = Currency.objects(code="EUR").first()
        gbp = Currency.objects(code="GBP").first()

        exchanges = [
            await self._create_test_exchange(
                test_user, from_currency_id=usd.id, to_currency_id=eur.id
            ),
            await self._create_test_exchange(
                test_user, from_currency_id=eur.id, to_currency_id=gbp.id
            ),
            await self._create_test_exchange(
                test_user, from_currency_id=gbp.id, to_currency_id=usd.id
            ),
        ]

        response = client.get("/currency-exchanges", headers=auth_headers)

        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["data"]["currency_exchanges"]) == len(exchanges)

        # Verify different currency pairs
        currency_pairs = set()
        for exchange in response_data["data"]["currency_exchanges"]:
            pair = (exchange["from_currency_id"], exchange["to_currency_id"])
            currency_pairs.add(pair)
        assert len(currency_pairs) == len(exchanges)

    async def test_read_all_currency_exchanges_different_dates(
        self, client, auth_headers, test_user
    ):
        """Test reading currency exchanges with different dates."""
        usd = Currency.objects(code="USD").first()
        eur = Currency.objects(code="EUR").first()
        gbp = Currency.objects(code="GBP").first()

        dates = [datetime(2024, 1, 1), datetime(2024, 2, 1), datetime(2024, 3, 1)]

        currency_pairs = [(usd.id, eur.id), (eur.id, gbp.id), (gbp.id, usd.id)]

        for date, (from_id, to_id) in zip(dates, currency_pairs):
            await self._create_test_exchange(
                test_user, from_currency_id=from_id, to_currency_id=to_id, date=date
            )

        response = client.get("/currency-exchanges", headers=auth_headers)

        assert response.status_code == 200
        response_data = response.json()
        exchanges = response_data["data"]["currency_exchanges"]
        assert len(exchanges) == len(dates)

        # Verify different dates
        response_dates = {exchange["date"][:10] for exchange in exchanges}
        expected_dates = {date.strftime("%Y-%m-%d") for date in dates}
        assert response_dates == expected_dates


@pytest.mark.asyncio
class TestUpdateCurrencyExchangeRoutePositive(TestCurrencyExchangeRoutesSetup):
    """Happy path tests for updating currency exchanges"""

    async def test_update_currency_exchange(self, client, auth_headers, test_user):
        """Test updating a currency exchange."""
        exchange = await self._create_test_exchange(test_user)
        update_data = {"rate": 0.90, "date": "2024-01-02"}

        response = client.put(
            f"/currency-exchanges/{str(exchange.id)}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "currency_exchange" in response_data["data"]
        assert response_data["data"]["currency_exchange"]["rate"] == 0.90
        assert response_data["message"] == "Currency exchange updated successfully"

    async def test_update_currency_exchange_rate(self, client, auth_headers, test_user):
        """Test updating only the rate."""
        exchange = await self._create_test_exchange(test_user)
        update_data = {"rate": 0.95}

        response = client.put(
            f"/currency-exchanges/{str(exchange.id)}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["data"]["currency_exchange"]["rate"] == 0.95
        assert response_data["message"] == "Currency exchange updated successfully"

    async def test_update_currency_exchange_date(self, client, auth_headers, test_user):
        """Test updating only the date."""
        exchange = await self._create_test_exchange(test_user)
        new_date = "2024-02-15T12:00:00"
        update_data = {"date": new_date}

        response = client.put(
            f"/currency-exchanges/{str(exchange.id)}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["data"]["currency_exchange"]["date"].startswith(
            "2024-02-15"
        )
        assert response_data["message"] == "Currency exchange updated successfully"

    async def test_update_currency_exchange_currencies(
        self, client, auth_headers, test_user
    ):
        """Test updating currency pair."""
        exchange = await self._create_test_exchange(test_user)
        gbp = Currency.objects(code="GBP").first()
        eur = Currency.objects(code="EUR").first()

        update_data = {"from_currency_id": str(gbp.id), "to_currency_id": str(eur.id)}

        response = client.put(
            f"/currency-exchanges/{str(exchange.id)}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        response_data = response.json()
        exchange_data = response_data["data"]["currency_exchange"]
        assert exchange_data["from_currency_id"] == str(gbp.id)
        assert exchange_data["to_currency_id"] == str(eur.id)
        assert response_data["message"] == "Currency exchange updated successfully"

    async def test_update_currency_exchange_all_fields(
        self, client, auth_headers, test_user
    ):
        """Test updating all fields at once."""
        exchange = await self._create_test_exchange(test_user)
        gbp = Currency.objects(code="GBP").first()
        eur = Currency.objects(code="EUR").first()

        update_data = {
            "from_currency_id": str(gbp.id),
            "to_currency_id": str(eur.id),
            "rate": 1.25,
            "date": "2024-03-01T12:00:00",
        }

        response = client.put(
            f"/currency-exchanges/{str(exchange.id)}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        response_data = response.json()
        exchange_data = response_data["data"]["currency_exchange"]
        assert exchange_data["from_currency_id"] == str(gbp.id)
        assert exchange_data["to_currency_id"] == str(eur.id)
        assert exchange_data["rate"] == 1.25
        assert exchange_data["date"].startswith("2024-03-01")
        assert response_data["message"] == "Currency exchange updated successfully"


@pytest.mark.asyncio
class TestDeleteCurrencyExchangeRoutePositive(TestCurrencyExchangeRoutesSetup):
    """Happy path tests for deleting currency exchanges"""

    async def _verify_exchange_deleted(self, exchange_id: str):
        """Helper method to verify exchange is deleted"""
        with pytest.raises(DoesNotExist):
            CurrencyExchange.objects.get(id=exchange_id)

    async def test_delete_currency_exchange_basic(
        self, client, auth_headers, test_user
    ):
        """Test deleting a basic currency exchange."""
        exchange = await self._create_test_exchange(test_user)

        response = client.delete(
            f"/currency-exchanges/{str(exchange.id)}", headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Currency exchange deleted successfully"
        await self._verify_exchange_deleted(str(exchange.id))

    async def test_delete_last_currency_exchange(self, client, auth_headers, test_user):
        """Test deleting the last remaining currency exchange."""
        # Ensure no other exchanges exist
        CurrencyExchange.objects().delete()

        exchange = await self._create_test_exchange(test_user)

        response = client.delete(
            f"/currency-exchanges/{str(exchange.id)}", headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Currency exchange deleted successfully"
        await self._verify_exchange_deleted(str(exchange.id))
        assert CurrencyExchange.objects().count() == 0

    async def test_delete_currency_exchange_with_future_date(
        self, client, auth_headers, test_user
    ):
        """Test deleting a currency exchange with future date."""
        future_date = datetime(2025, 1, 1)
        exchange = await self._create_test_exchange(test_user, date=future_date)

        response = client.delete(
            f"/currency-exchanges/{str(exchange.id)}", headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Currency exchange deleted successfully"
        await self._verify_exchange_deleted(str(exchange.id))
