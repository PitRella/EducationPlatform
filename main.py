import re
import uuid

from fastapi import FastAPI, APIRouter
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, field_validator, ConfigDict
from sqlalchemy import Column, String, Boolean
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import UUID

import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    future=True,
    echo=True
)
async_db_session = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession

)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean(), default=True)


class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.__db_session: AsyncSession = db_session

    async def create_user(self,
                          name: str, surname: str, email: str):
        new_user = User(
            name=name,
            surname=surname,
            email=email,
        )
        self.__db_session.add(new_user)
        await self.__db_session.flush()
        return new_user


LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-яa-zA-Z\-]+$]")


class TunedModel(BaseModel):
    class Config:
        model_config = ConfigDict(from_attributes=True)


class ShowUser(TunedModel):
    user_id: uuid.UUID
    name: str
    surname: str
    email: str
    is_active: bool


class CreateUser(BaseModel):
    name: str
    surname: str
    email: str

    @classmethod
    @field_validator("name")
    def validate_name(cls, value: str):
        if not value in LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Name should contain only letters."
            )
        return value

    @classmethod
    @field_validator("surname")
    def validate_surname(cls, value: str):
        if not value in LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Surname should contain only letters."
            )
        return value


app = FastAPI(title="EducationPlatform")
user_router = APIRouter()


async def _create_new_user(user: CreateUser) -> ShowUser:
    async with async_db_session() as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.create_user(
                name=user.name,
                surname=user.surname,
                email=user.email
            )
            return ShowUser(
                user_id=user.user_id,
                name=user.name,
                surname=user.surname,
                email=user.email,
                is_active=user.is_active,
            )


@user_router.post("/", response_model=ShowUser)
async def create_user(user: CreateUser) -> ShowUser:
    return await _create_new_user(user)


main_api_router = APIRouter()
main_api_router.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(main_api_router)
