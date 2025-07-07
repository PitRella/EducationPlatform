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
type create_user_data = dict[str, str | list[str]]


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
    @staticmethod
    def _get_use_data() -> create_user_data:
        return {
            'name': 'TestName',
            'surname': 'TestSurName',
            'email': 'test_user@tmail.com',
            'password': 'Qwerty@123',
            'roles': ['user'],
        }

    @pytest.mark.asyncio
    async def test_create_user(self) -> None:
        """Correct user creates data."""
        data = self._get_use_data()
        response: dict[str, str] = client.post(
            '/api/v1/user/', json=data
        ).json()
        assert response.get('name') == data.get('name')
        assert response.get('surname') == data.get('surname')
        assert response.get('email') == data.get('email')
        assert response.get('roles') == data.get('roles')

    @pytest.mark.asyncio
    async def test_create_user_email_error(self) -> None:
        """Wrong email without @ should case an error."""
        data = self._get_use_data()
        data['email'] = 'wrong_email.com'
        response = client.post('/api/v1/user/', json=data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_user_password_error(self) -> None:
        # Weak password that does not meet the requirements should case an error

        data = self._get_use_data()
        data['password'] = 'qwerty3'
        response = client.post('/api/v1/user/', json=data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_user_name_with_numbers(self) -> None:
        """Username should not contain numbers."""
        data = self._get_use_data()
        data['name'] = 'John19'
        response = client.post('/api/v1/user/', json=data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_user_surname_with_numbers(self) -> None:
        """Surname should not contain numbers."""
        data = self._get_use_data()
        data['surname'] = 'Doe23'
        response = client.post('/api/v1/user/', json=data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_user_none_roles(self) -> None:
        """If roles not specified, a default role should be user."""
        data = self._get_use_data()
        data['roles'] = []
        response = client.post('/api/v1/user/', json=data).json()
        assert response.get('name') == data.get('name')
        assert response.get('surname') == data.get('surname')
        assert response.get('email') == data.get('email')
        assert response.get('roles') == ['user']
