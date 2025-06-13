import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, Response, Request, status

from src.auth.exceptions import WrongCredentialsException
from src.auth.schemas import Token
from src.auth.service import AuthService
from src.session import get_db
from src.settings import REFRESH_TOKEN_EXPIRE_DAYS, ACCESS_TOKEN_EXPIRE_MINUTES
from src.users.models import User

auth_router = APIRouter()


@auth_router.post(path="/login", response_model=Token)
async def login_user(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
) -> Token:
    user: Optional[User] = await AuthService.auth_user(
        email=form_data.username,
        password=form_data.password,
        db=db
    )
    if not user: raise WrongCredentialsException
    token: Token = await AuthService.create_token(user.user_id, db)
    response.set_cookie(
        'access_token',
        token.access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True
    )
    response.set_cookie(
        'refresh_token',
        token.refresh_token,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 30 * 24 * 60,
        httponly=True
    )
    return token
