from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.api.endpoints.asset_routes import router as asset_routes
from app.api.endpoints.asset_type_routes import router as asset_type_routes
from app.api.endpoints.authentication_routes import router as auth_routes
from app.api.endpoints.category_routes import router as category_routes
from app.api.endpoints.currency_exchange_routes import (
    router as currency_exchange_routes,
)
from app.api.endpoints.transaction_routes import router as transaction_routes
from app.api.endpoints.wallet_routes import router as wallet_routes
from commons.exception_handlers import base_exception_handler, http_exception_handler
from database.database import connect_to_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_to_db()
    yield


app = FastAPI(
    title="My-net-worth app API",
    description="This app is a personal financial app that helps you manage your money better",
    lifespan=lifespan,
)

app.include_router(currency_exchange_routes)
app.include_router(asset_type_routes)
app.include_router(asset_routes)
app.include_router(auth_routes)
app.include_router(category_routes)
app.include_router(wallet_routes)
app.include_router(transaction_routes)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, base_exception_handler)
