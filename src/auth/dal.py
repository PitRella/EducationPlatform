import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Result, Select, Update, Delete
from src.auth.models import RefreshSessionModel


class AuthDAL:
    def __init__(self, db_session: AsyncSession):
        self.__db_session: AsyncSession = db_session

    async def create_token(
            self,
            user_id: uuid.UUID,
            refresh_token: uuid.UUID,
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

    async def get_refresh_token(
            self,
            refresh_token: uuid.UUID
    ) -> Optional[RefreshSessionModel]:
        query: Select[RefreshSessionModel] = Select(RefreshSessionModel).where(
            RefreshSessionModel.refresh_token == refresh_token
        )
        result: Result = await self.__db_session.execute(query)
        token: Optional[RefreshSessionModel] = result.scalar_one_or_none()
        return token

    async def update_refresh_token(
            self,
            refresh_token_id: int,
            refresh_token: uuid.UUID,
            expires_at: float,
    ) -> Optional[RefreshSessionModel]:
        query: Update = Update(RefreshSessionModel).where(
            RefreshSessionModel.id == refresh_token_id).values(
            refresh_token=refresh_token,
            expires_in=expires_at
        ).returning(RefreshSessionModel.id)
        result: Result = await self.__db_session.execute(query)
        updated_token: Optional[
            RefreshSessionModel] = result.scalar_one_or_none()
        return updated_token

    async def delete_refresh_token(
            self,
            refresh_token_id: int
    ) -> None:
        query: Delete = Delete(RefreshSessionModel).where(
            RefreshSessionModel.id == refresh_token_id)
        await self.__db_session.execute(query)
