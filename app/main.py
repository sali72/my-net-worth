from contextlib import asynccontextmanager

from fastapi import FastAPI
from mongoengine.errors import DoesNotExist

from app.api.endpoints.authentication_routes import router as auth_routes
from app.api.endpoints.wallet_routes import router as wallet_routes
from commons.mongoengine_exception_handlers import does_not_exist_handler
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

app.add_exception_handler(DoesNotExist, does_not_exist_handler)
