
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi import APIRouter, Depends, Response

from src.auth.schemas import Token
from src.auth.service import AuthService
from src.session import get_db
from src.settings import REFRESH_TOKEN_EXPIRE_DAYS, ACCESS_TOKEN_EXPIRE_MINUTES
from src.users.models import User

auth_router = APIRouter()

oauth_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


@auth_router.post(path="/login", response_model=Token)
async def login_user(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
) -> Token:
    """
    Endpoint to login user based on email and password.
    :param response: User response.
    :param form_data: Form data with password and email.
    :param db: Async session to db.
    :return: Pair of access token and refresh token.
    """
    user: User = await AuthService.auth_user(
        email=form_data.username,
        password=form_data.password,
        db=db
    )
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


async def get_user_from_jwt(
        token=Depends(oauth_scheme),
        db: AsyncSession = Depends(get_db)
) -> User:
    """
    Method to take user_id from access token.
    :param token: Access token.
    :param db: Async session to db.
    :return: User.
    """
    user: User = await AuthService.validate_token(token, db)
    return user


@auth_router.get(path='/test')
async def test_endpoint(
        jwt_user: User = Depends(get_user_from_jwt),
        db: AsyncSession = Depends(get_db)
):
    return {
        "name": jwt_user.name,
    }
