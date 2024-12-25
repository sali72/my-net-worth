import pytest
from fastapi.testclient import TestClient

from app.api.controllers.auth_controller import AuthController
from app.crud.currency_crud import CurrencyCRUD
from app.crud.user_app_data_crud import UserAppDataCRUD
from app.crud.user_crud import UserCRUD
from app.main import app
from database.database import connect_to_test_db, disconnect_test_db
from models.schemas import UserSchema


@pytest.fixture(scope="session", autouse=True)
async def db():
    await connect_to_test_db()
    yield
    await disconnect_test_db()


@pytest.fixture(scope="session", autouse=True)
async def client():
    client = TestClient(app)
    yield client


@pytest.fixture(scope="session", autouse=True)
async def test_currency(db):
    test_currency = await CurrencyCRUD.get_one_by_user_and_code_optional(
        code="USD", user_id=None
    )
    yield test_currency


@pytest.fixture(scope="session")
async def access_token(db, test_currency):
    """Register a test user and return the access token string"""
    user_schema = UserSchema(
        username="testuser",
        email="test@example.com",
        password="TestPassword!@#123",
        base_currency_id=str(test_currency.id),
    )
    access_token = await AuthController.register_user(user_schema)
    yield access_token


@pytest.fixture(scope="session", autouse=True)
async def test_user(db, access_token):
    test_user = await UserCRUD.get_one_by_username("testuser")
    yield test_user


@pytest.fixture(scope="session", autouse=True)
def auth_headers(access_token):
    yield {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="session", autouse=True)
async def test_user_app_data(db, test_user):
    test_user_app_data = await UserAppDataCRUD.get_one_by_user_id(test_user.id)
    yield test_user_app_data
