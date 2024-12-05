from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.api.endpoints.asset_routes import router as asset_routes
from app.api.endpoints.asset_type_routes import router as asset_type_routes
from app.api.endpoints.authentication_routes import router as auth_routes
from app.api.endpoints.category_routes import router as category_routes
from app.api.endpoints.currency_exchange_routes import (
    router as currency_exchange_routes,
)
from app.api.endpoints.currency_routes import router as currency_routes
from app.api.endpoints.transaction_routes import router as transaction_routes
from app.api.endpoints.user_app_data_routes import router as user_app_data_routes
from app.api.endpoints.wallet_routes import router as wallet_routes
from commons.exception_handlers import base_exception_handler, http_exception_handler
from database.database import connect_to_db

# from models.models import AssetType


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_db()
    # # Fix indexes of collections if needed
    # AssetType._get_collection().drop_indexes()
    # AssetType.ensure_indexes()
    yield


app = FastAPI(
    title="My-net-worth app API",
    description="This app is a personal financial app \
        that helps you manage your money better",
    lifespan=lifespan,
)

app.include_router(auth_routes)
app.include_router(user_app_data_routes)
app.include_router(currency_routes)
app.include_router(currency_exchange_routes)
app.include_router(wallet_routes)
app.include_router(transaction_routes)
app.include_router(asset_type_routes)
app.include_router(asset_routes)
app.include_router(category_routes)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, base_exception_handler)
