from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.api.endpoints.authentication_routes import router as auth_routes
from app.api.endpoints.wallet_routes import router as wallet_routes
from app.api.endpoints.transaction_routes import router as transaction_routes
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

app.include_router(auth_routes)
app.include_router(wallet_routes)
app.include_router(transaction_routes)


app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, base_exception_handler)
