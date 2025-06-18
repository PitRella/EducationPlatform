import uuid
from calendar import timegm
from typing import Tuple

from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from src.auth.exceptions import (
    WrongCredentialsException,
    AccessTokenExpiredException,
    RefreshTokenException
)
from src.auth.models import RefreshSessionModel
from src.settings import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS
)


class TokenManager:
    """
    A class responsible for managing JWT access tokens and refresh tokens.

    This class provides functionality to:
    - Generate and decode JWT access tokens
    - Generate refresh tokens with expiration times
    - Validate token expiration for both access and refresh tokens

    All methods are implemented as class methods for stateless operation.
    """

    @classmethod
    def generate_access_token(cls, user_id: uuid.UUID) -> str:
        """
        Generate a new JWT access token for the user.

        :param user_id: UUID of the user to generate token for
        :return: Bearer token string containing the JWT
        """
        to_encode: dict[str, str | datetime] = {
            "sub": str(user_id),
            "exp": datetime.now() + timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        encoded_jwt: str = jwt.encode(
            to_encode,
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        return f'Bearer {encoded_jwt}'

    @classmethod
    def generate_refresh_token(cls) -> Tuple[uuid.UUID, timedelta]:
        """
        Generate a new refresh token and its expiration time.

        :return: Tuple of (UUID refresh token, timedelta expiration time)
        """
        return uuid.uuid4(), timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    @classmethod
    def decode_access_token(cls, token: str) -> dict[str, str | int]:
        """
        Decode and verify a JWT token.

        :param token: JWT token string to decode
        :return: Dictionary containing decoded token claims
        """
        try:
            decoded_jwt: dict[str, str | int] = jwt.decode(
                token=token,
                key=SECRET_KEY,
                algorithms=ALGORITHM
            )
        except JWTError:
            raise WrongCredentialsException
        return decoded_jwt

    @classmethod
    def validate_access_token_expired(cls, decoded: dict[str, str | int]) -> None:
        """
        Check if the access token has expired.

        :param decoded: Dictionary containing a decoded token claims
        :raises: AccessTokenExpiredException if the token has expired
        """
        jwt_exp_date: int = int(decoded.get("exp", 0))
        current_time: int = timegm(datetime.now().utctimetuple())
        if not jwt_exp_date or current_time >= jwt_exp_date:
            raise AccessTokenExpiredException

    @classmethod
    def validate_refresh_token_expired(
            cls,
            refresh_token_model: RefreshSessionModel,
    ) -> None:
        """
        Check if the refresh token has expired.

        :param refresh_token_model: RefreshSessionModel instance containing token details
        :raises: RefreshTokenException if the token has not expired
        """
        current_date: datetime = datetime.now(timezone.utc)
        refresh_token_expire_date: datetime = (refresh_token_model.created_at +
                                               timedelta(
                                                   seconds=refresh_token_model.expires_in))
        if not (current_date >= refresh_token_expire_date):
            raise RefreshTokenException
