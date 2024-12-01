from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field

from app.api.controllers.auth_controller import AuthController, get_current_user
from app.crud.user_crud import UserCRUD
from models.schemas import ResponseSchema, Token, UserSchema, UpdateUserSchema

load_dotenv()

router = APIRouter(tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.post(
    "/register",
    response_model=ResponseSchema,
    response_description="Register a new user",
    status_code=status.HTTP_201_CREATED,
)
async def register(user_schema: UserSchema):
    access_token = await AuthController.register_user(user_schema)

    message = "User registered successfully"
    data = Token(access_token=access_token, token_type="bearer")
    return ResponseSchema(data=dict(data), message=message)


@router.post(
    "/login",
    response_description="Login a user",
    status_code=status.HTTP_200_OK,
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    access_token = await AuthController.login_user(
        form_data.username, form_data.password
    )
    return Token(access_token=access_token, token_type="bearer")


@router.put(
    "/update",
    response_model=ResponseSchema,
    response_description="Update user credentials",
    status_code=status.HTTP_200_OK,
)
async def update_user_credentials(
    update_data: UpdateUserSchema, token: str = Depends(oauth2_scheme)
):
    current_user = await get_current_user(token)

    updated_user = await AuthController.update_user_credentials(
        current_user, update_data.model_dump(exclude_unset=True)
    )

    message = "User credentials updated successfully"
    return ResponseSchema(data=updated_user.to_dict(), message=message)
