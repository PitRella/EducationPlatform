import uuid
from calendar import timegm
from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from src.auth.exceptions import (
    AccessTokenExpiredException,
    RefreshTokenException,
    WrongCredentialsException,
)
from src.auth.models import RefreshToken
from src.settings import Settings

settings = Settings.load()

type access_token = dict[str, str | datetime]


class TokenManager:
    """A class responsible for managing JWT access tokens and refresh tokens.

    This class provides functionality to:
    - Generate and decode JWT access tokens
    - Generate refresh tokens with expiration times
    - Validate token expiration for both access and refresh tokens

    All methods are implemented as class methods for stateless operation.
    """

    @classmethod
    def generate_access_token(cls, user_id: uuid.UUID) -> str:
        """Generate a new JWT access token for the user.

        :param user_id: UUID of the user to generate token for
        :return: Bearer token string containing the JWT
        """
        to_encode: access_token = {
            'sub': str(user_id),
            'exp': datetime.now(UTC)
            + timedelta(
                minutes=settings.token_settings.ACCESS_TOKEN_EXPIRE_MINUTES
            ),
        }
        encoded_jwt: str = jwt.encode(
            to_encode,
            settings.token_settings.SECRET_KEY,
            algorithm=settings.token_settings.ALGORITHM,
        )
        return f'Bearer {encoded_jwt}'

    @classmethod
    def generate_refresh_token(cls) -> tuple[uuid.UUID, timedelta]:
        """Generate a new refresh token and its expiration time.

        :return: Tuple of (UUID refresh token, timedelta expiration time)
        """
        return uuid.uuid4(), timedelta(
            days=settings.token_settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    @classmethod
    def decode_access_token(cls, token: str) -> dict[str, str | int]:
        """Decode and verify a JWT token.

        :param token: JWT token string to decode
        :return: Dictionary containing decoded token claims
        """
        try:
            decoded_jwt: dict[str, str | int] = jwt.decode(
                token=token,
                key=settings.token_settings.SECRET_KEY,
                algorithms=settings.token_settings.ALGORITHM,
            )
        except JWTError:
            raise WrongCredentialsException from None
        return decoded_jwt

    @classmethod
    def validate_access_token_expired(
        cls,
        decoded: dict[str, str | int],
    ) -> None:
        """Check if the access token has expired.

        :param decoded: Dictionary containing a decoded token claims
        :raises: AccessTokenExpiredException if the token has expired
        """
        jwt_exp_date: int = int(decoded.get('exp', 0))
        current_time: int = timegm(datetime.now(UTC).utctimetuple())
        if not jwt_exp_date or current_time >= jwt_exp_date:
            raise AccessTokenExpiredException

    @classmethod
    def validate_refresh_token_expired(
        cls,
        refresh_token_model: RefreshToken,
    ) -> None:
        """Check if the refresh token has expired.

        :param refresh_token_model: RefreshSessionModel instance
        containing token details
        :raises: RefreshTokenException if the token has not expired
        """
        current_date: datetime = datetime.now(UTC)
        refresh_token_expire_date: datetime = (
            refresh_token_model.created_at
            + timedelta(seconds=refresh_token_model.expires_in)
        )
        if current_date >= refresh_token_expire_date:
            raise RefreshTokenException
