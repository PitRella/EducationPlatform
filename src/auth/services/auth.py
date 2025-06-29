import uuid
from typing import Optional, Union, cast

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dao import AuthDAO
from src.auth.exceptions import WrongCredentialsException, RefreshTokenException
from src.auth.models import RefreshSessionModel
from src.auth.schemas import Token
from src.auth.services.token import TokenManager
from src.hashing import Hasher
from src.users.dao import UserDAO
from src.users.models import User


class AuthService:
    def __init__(
        self,
        db_session: AsyncSession,
        auth_dao: Optional[AuthDAO] = None,
        user_dao: Optional[UserDAO] = None,
    ) -> None:
        self._session: AsyncSession = db_session
        self._auth_dao: AuthDAO = auth_dao or AuthDAO(db_session)
        self._user_dao: UserDAO = user_dao or UserDAO(db_session)

    @property
    def auth_dao(self) -> AuthDAO:
        return self._auth_dao

    @property
    def user_dao(self) -> UserDAO:
        return self._user_dao

    @property
    def session(self) -> AsyncSession:
        return self._session

    @staticmethod
    def _verify_user_password(user: Optional[User], password: str) -> None:
        if not user or not Hasher.verify_password(password, user.password):
            raise WrongCredentialsException

    async def auth_user(self, email: str, password: str) -> User:
        async with self.session.begin():
            user: Optional[User] = await self.user_dao.get_user_by_email(email)
        self._verify_user_password(user, password)
        return cast(User, user)

    @staticmethod
    def _get_user_id_from_jwt(decoded_jwt: dict[str, str | int]) -> str:
        user_id: Optional[int | str] = decoded_jwt.get("sub", None)
        if not user_id or isinstance(user_id, int):
            raise WrongCredentialsException
        return user_id

    async def validate_token(self, user_jwt_token: str) -> User:
        decoded_jwt: dict[str, str | int] = TokenManager.decode_access_token(
            token=user_jwt_token
        )
        TokenManager.validate_access_token_expired(decoded_jwt)
        user_id: Union[uuid.UUID, str] = self._get_user_id_from_jwt(decoded_jwt)
        async with self.session.begin():
            user: Optional[User] = await self.user_dao.get_user_by_id(user_id)
        if not user:
            raise WrongCredentialsException
        return user

    async def create_token(self, user_id: uuid.UUID) -> Token:
        access_token: str = TokenManager.generate_access_token(user_id=user_id)
        refresh_token, tm_delta = TokenManager.generate_refresh_token()
        async with self.session.begin():
            await self.auth_dao.delete_old_tokens(
                user_id=user_id,
            )
            await self.auth_dao.create_token(
                user_id, refresh_token, tm_delta.total_seconds()
            )
        return Token(
            access_token=access_token, refresh_token=str(refresh_token)
        )

    async def refresh_token(self, refresh_token: uuid.UUID) -> Token:
        async with self.session.begin():
            refresh_token_model: Optional[
                RefreshSessionModel
            ] = await self.auth_dao.get_refresh_token(
                refresh_token=refresh_token
            )
            if not refresh_token_model:
                raise RefreshTokenException
            TokenManager.validate_refresh_token_expired(
                refresh_token_model=refresh_token_model,
            )
            user_id: uuid.UUID = refresh_token_model.user_id
            user: Optional[User] = await self.user_dao.get_user_by_id(
                user_id=user_id
            )
            if not user:
                raise RefreshTokenException
            access_token: str = TokenManager.generate_access_token(
                user_id=user_id
            )
            updated_refresh_token, tm_delta = (
                TokenManager.generate_refresh_token()
            )
            updated_refresh_token_model: Optional[
                RefreshSessionModel
            ] = await self.auth_dao.update_refresh_token(
                refresh_token_id=refresh_token_model.id,
                refresh_token=updated_refresh_token,
                expires_at=tm_delta.total_seconds(),
            )
            if not updated_refresh_token_model:
                raise RefreshTokenException
            return Token(
                access_token=access_token,
                refresh_token=str(updated_refresh_token),
            )

    async def logout_user(
        self,
        refresh_token: Optional[str],
    ) -> None:
        if not refresh_token:
            raise RefreshTokenException
        async with self.session.begin():
            refresh_token_model: Optional[
                RefreshSessionModel
            ] = await self.auth_dao.get_refresh_token(
                refresh_token=refresh_token
            )
            if not refresh_token_model:
                raise RefreshTokenException
            await self.auth_dao.delete_refresh_token(
                refresh_token_id=refresh_token_model.id
            )
