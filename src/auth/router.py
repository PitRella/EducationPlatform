import uuid

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, Response, Request

from src.auth.dependencies import get_service
from src.auth.schemas import Token
from src.auth.services import AuthService
from src.settings import REFRESH_TOKEN_EXPIRE_DAYS, ACCESS_TOKEN_EXPIRE_MINUTES
from src.users.models import User

auth_router = APIRouter()


@auth_router.post(path="/login", response_model=Token)
async def login_user(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_service),
) -> Token:
    """
    Endpoint to login user based on email and password.
    :param response: User response.
    :param form_data: Form data with password and email.
    :param db: Async session to db.
    :return: Pair of access token and refresh token.
    """
    user: User = await service.auth_user(
        email=form_data.username,
        password=form_data.password,
    )
    token: Token = await service.create_token(user.user_id)
    response.set_cookie(
        "access_token",
        token.access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
    )
    response.set_cookie(
        "refresh_token",
        token.refresh_token,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 30 * 24 * 60,
        httponly=True,
    )
    return token


@auth_router.post(path="/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_service),
) -> Token:
    token: Token = await service.refresh_token(
        refresh_token=uuid.UUID(request.cookies.get("refresh_token"))
    )
    response.set_cookie(
        "access_token",
        token.access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
    )
    response.set_cookie(
        "refresh_token",
        token.refresh_token,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 30 * 24 * 60,
        httponly=True,
    )
    return token


@auth_router.delete(path="/logout", response_model=dict[str, str])
async def logout_user(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_service),
) -> dict[str, str]:
    await service.logout_user(request.cookies.get("refresh_token"))
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}
