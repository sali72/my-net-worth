import os
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Union

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from zxcvbn import zxcvbn

from app.crud.user_app_data_crud import UserAppDataCRUD
from app.crud.user_crud import UserCRUD
from models.enums import RoleEnum
from models.models import User, UserAppData
from models.schemas import UserSchema

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
MINIMUM_PASSWORD_STRENGTH = int(os.getenv("MINIMUM_PASSWORD_STRENGTH"))


class AuthController:

    user_crud = UserCRUD()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    async def login_user(cls, username: str, password: str) -> str:
        user = await cls.authenticate_user(username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = cls.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return access_token

    @classmethod
    async def register_user(cls, user_schema: UserSchema) -> str:
        await cls.__check_password_strength(user_schema.password, user_schema.username)
        hashed_password = cls.pwd_context.hash(user_schema.password)
        await cls.__create_user_model_atomic(user_schema, hashed_password)
        return await cls.login_user(user_schema.username, user_schema.password)

    @classmethod
    async def update_user_credentials(
        cls, current_user: User, update_data: Dict[str, Union[str, None]]
    ) -> User:
        updated_fields = update_data
        if "password" in updated_fields:
            updated_fields["hashed_password"] = cls.pwd_context.hash(
                updated_fields.pop("password")
            )
        try:
            return await cls.user_crud.update_one(current_user.username, updated_fields)
        except Exception as e:
            raise e

    @classmethod
    async def delete_user(cls, current_user: User) -> None:
        await cls.user_crud.delete_one(current_user.username)

    @classmethod
    async def authenticate_user(cls, username: str, password: str) -> Optional[User]:
        user = await cls.user_crud.get_one_by_username_optional(username)
        if not user or not cls.verify_password(password, user.hashed_password):
            return None
        return user

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def create_access_token(
        cls, data: Dict[str, str], expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @classmethod
    async def __create_user_model_atomic(
        cls, user_schema: UserSchema, hashed_password: str
    ) -> None:
        user_model = User(
            username=user_schema.username,
            hashed_password=hashed_password,
            email=user_schema.email,
            role=RoleEnum.USER.value,
        )
        user_in_db = await cls.user_crud.create_one(user_model)
        try:
            user_app_data = UserAppData(
                user_id=user_in_db, base_currency_id=user_schema.base_currency_id
            )
            await UserAppDataCRUD.create_one(user_app_data)
        except Exception as e:
            await UserCRUD.delete_one(user_in_db)
            raise e

    @classmethod
    async def __check_password_strength(cls, password: str, username: str) -> None:
        password_policy = await cls.__check_password_policy(password)
        if not password_policy["status"]:
            raise HTTPException(status_code=400, detail=password_policy["message"])
        result = zxcvbn(password, user_inputs=[username])
        if result["score"] < MINIMUM_PASSWORD_STRENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Your password is not strong enough, {result['feedback']['suggestions']}",
            )

    @classmethod
    async def __check_password_policy(
        cls, password: str
    ) -> Dict[str, Union[bool, str]]:
        if len(password) < 8:
            return {
                "status": False,
                "message": "Password must be at least 8 characters long",
            }
        if re.search("[0-9]", password) is None:
            return {
                "status": False,
                "message": "Password must contain at least one digit",
            }
        if re.search("[A-Z]", password) is None:
            return {
                "status": False,
                "message": "Password must contain at least one uppercase letter",
            }
        if re.search("[a-z]", password) is None:
            return {
                "status": False,
                "message": "Password must contain at least one lowercase letter",
            }
        return {"status": True, "message": "Password is strong"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = await AuthController.user_crud.get_one_by_username_optional(username)
    if user is None:
        raise credentials_exception
    return user


def has_role(role: RoleEnum):
    def role_verifier(current_user: User = Depends(get_current_user)) -> User:
        if (role.value != current_user.role) and (
            RoleEnum.ADMIN.value != current_user.role
        ):
            raise HTTPException(status_code=403, detail="Operation not permitted")
        return current_user

    return role_verifier
