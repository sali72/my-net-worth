from typing import Dict

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.controllers.auth_controller import (
    AuthController,
    get_current_user,
    oauth2_scheme,
)
from models.schemas import ResponseSchema, Token, UpdateUserSchema, UserSchema

load_dotenv()

router = APIRouter(tags=["Authentication"])


@router.post(
    "/register",
    response_model=ResponseSchema,
    response_description="Register a new user",
    status_code=status.HTTP_201_CREATED,
)
async def register(user_schema: UserSchema) -> ResponseSchema:
    """
    Register a new user.

    Args:
        user_schema (UserSchema): The schema containing user registration details.

    Returns:
        ResponseSchema: The response containing the access token and a success message.
    """
    access_token = await AuthController.register_user(user_schema)
    message = "User registered successfully"
    data = Token(access_token=access_token, token_type="bearer")
    return ResponseSchema(data=dict(data), message=message)


@router.post(
    "/login",
    response_model=Token,
    response_description="Login a user",
    status_code=status.HTTP_200_OK,
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """
    Login a user and return an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing username and password.

    Returns:
        Token: The access token and token type.
    """
    access_token = await AuthController.login_user(
        form_data.username, form_data.password
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/user",
    response_model=ResponseSchema,
    response_description="Get current user data",
    status_code=status.HTTP_200_OK,
)
async def get_user_data(token: str = Depends(oauth2_scheme)) -> ResponseSchema:
    """
    Retrieve the current user's data.

    Args:
        token (str): The JWT token for authentication.

    Returns:
        ResponseSchema: The response containing the current user's data and a success message.
    """
    current_user = await get_current_user(token)
    message = "User data retrieved successfully"
    return ResponseSchema(data=current_user.to_dict(), message=message)


@router.put(
    "/update",
    response_model=ResponseSchema,
    response_description="Update user credentials",
    status_code=status.HTTP_200_OK,
)
async def update_user_credentials(
    update_data: UpdateUserSchema, token: str = Depends(oauth2_scheme)
) -> ResponseSchema:
    """
    Update the current user's credentials.

    Args:
        update_data (UpdateUserSchema): The schema containing updated user credentials.
        token (str): The JWT token for authentication.

    Returns:
        ResponseSchema: The response containing the updated user data and a success message.
    """
    current_user = await get_current_user(token)
    updated_user = await AuthController.update_user_credentials(
        current_user, update_data.model_dump(exclude_unset=True)
    )
    message = "User credentials updated successfully"
    return ResponseSchema(data=updated_user.to_dict(), message=message)


@router.delete(
    "/user",
    response_model=ResponseSchema,
    response_description="Delete current user",
    status_code=status.HTTP_200_OK,
)
async def delete_user(token: str = Depends(oauth2_scheme)) -> ResponseSchema:
    """
    Delete the current user.

    Args:
        token (str): The JWT token for authentication.

    Returns:
        ResponseSchema: The response containing a success message.
    """
    current_user = await get_current_user(token)
    await AuthController.delete_user(current_user)
    message = "User deleted successfully"
    return ResponseSchema(data={}, message=message)
