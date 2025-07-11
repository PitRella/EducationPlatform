import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm

from src.base.dependencies import get_service
from src.auth.schemas import Token
from src.auth.services import AuthService
from src.settings import Settings
from src.users.models import User

auth_router = APIRouter()
settings = Settings.load()


@auth_router.post(path='/login', response_model=Token)
async def login_user(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        service: Annotated[AuthService, Depends(get_service(AuthService))],
        response: Response,
) -> Token:
    """Authenticate user and issue JWT access and refresh tokens.

    Args:
        form_data (OAuth2PasswordRequestForm): User credentials from the form.
        service (AuthService): Auth service dependency.
        response (Response): FastAPI response to set cookies.

    Returns:
        Token: Access and refresh tokens to be used for authentication.

    """
    user: User = await service.auth_user(
        email=form_data.username,
        password=form_data.password,
    )
    token: Token = await service.create_token(user.id)
    response.set_cookie(
        'access_token',
        token.access_token,
        max_age=settings.token_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
    )
    response.set_cookie(
        'refresh_token',
        token.refresh_token,
        max_age=settings.token_settings.REFRESH_TOKEN_EXPIRE_DAYS
                * 30
                * 24
                * 60,
        httponly=True,
    )
    return token


@auth_router.post(path='/refresh', response_model=Token)
async def refresh_token(
        request: Request,
        response: Response,
        service: Annotated[AuthService, Depends(get_service(AuthService))],
) -> Token:
    """Refresh the access and refresh tokens.

    Args:
        request (Request): Incoming HTTP request, used to read cookies.
        response (Response): HTTP response to set updated cookies.
        service (AuthService): Auth service dependency.

    Returns:
        Token: New access and refresh tokens.

    """
    token: Token = await service.refresh_token(
        refresh_token=uuid.UUID(request.cookies.get('refresh_token')),
    )
    response.set_cookie(
        'access_token',
        token.access_token,
        max_age=settings.token_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
    )
    response.set_cookie(
        'refresh_token',
        token.refresh_token,
        max_age=settings.token_settings.REFRESH_TOKEN_EXPIRE_DAYS
                * 30
                * 24
                * 60,
        httponly=True,
    )
    return token


@auth_router.delete(path='/logout', response_model=dict[str, str])
async def logout_user(
        request: Request,
        response: Response,
        service: Annotated[AuthService, Depends(get_service(AuthService))],
) -> dict[str, str]:
    """Log out the user.

    Args:
        request (Request): HTTP request to read cookies.
        response (Response): HTTP response to delete cookies.
        service (AuthService): Auth service dependency.

    Returns:
        dict[str, str]: Confirmation message of successful logout.

    """
    await service.logout_user(request.cookies.get('refresh_token'))
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return {'message': 'Logged out successfully'}
