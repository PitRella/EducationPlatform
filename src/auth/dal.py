import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import RefreshSessionModel


class AuthDAL:
    def __init__(self, db_session: AsyncSession):
        self.__db_session: AsyncSession = db_session

    async def create_token(
            self,
            user_id: uuid.UUID,
            refresh_token:uuid.UUID,
            refresh_token_expires_total_seconds: float
    ) -> Optional[RefreshSessionModel]:
        new_token = RefreshSessionModel(
            refresh_token=refresh_token,
            expires_in=refresh_token_expires_total_seconds,
            user_id=user_id,
        )
        self.__db_session.add(new_token)
        await self.__db_session.flush()
        return new_token
