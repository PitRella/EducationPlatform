import logging
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app
from src.users.dependencies import get_service
from src.users.models import User
from src.users.service import UserService
from tests.conftest import MockUserDAO

logger = logging.getLogger(__name__)

client = TestClient(app)


@pytest.fixture(autouse=True)
def override_get_service(
    default_user_obj: User, db_session: AsyncSession
) -> Generator[None]:
    def _mocked_service() -> Generator[UserService]:
        mocker_user_service = UserService(
            db_session=db_session,
            dao=MockUserDAO(default_user_obj),  # type: ignore
        )
        yield mocker_user_service

    app.dependency_overrides[get_service] = _mocked_service
    yield
    app.dependency_overrides = {}


class TestUsersRouter:
    @pytest.mark.asyncio
    async def test_create_user(self) -> None:
        data = {
            'name': 'TestName',
            'surname': 'TestSurName',
            'email': 'test_user@tmail.com',
            'password': 'Qwerty@123',
            'roles': ['user'],
        }
        response: dict[str, str] = client.post(
            '/api/v1/user/', json=data
        ).json()
        assert response.get('name') == data.get('name')
        assert response.get('surname') == data.get('surname')
        assert response.get('email') == data.get('email')
        assert response.get('roles') == data.get('roles')
