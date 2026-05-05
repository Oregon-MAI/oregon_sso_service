from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models.role import Role
from src.data.models.token import Token
from src.data.models.user import User


@pytest.fixture
def mock_session() -> MagicMock:
    session = MagicMock(spec=AsyncSession)

    begin_cm = AsyncMock()
    begin_cm.__aenter__ = AsyncMock(return_value=None)
    begin_cm.__aexit__ = AsyncMock(return_value=None)
    session.begin.return_value = begin_cm

    session.execute = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def sample_user() -> User:
    user = User(
        login="testuser",
        password="hashed_pwd",
        first_name="Test",
        last_name="User",
        email="test@example.com",
    )
    user.id = uuid4()
    return user


@pytest.fixture
def sample_role() -> Role:
    role = Role(name="admin", description="Admin role")
    role.id = uuid4()
    return role


@pytest.fixture
def sample_token() -> Token:
    return Token(id=uuid4(), token="jwt_token_here", status=True)


@pytest.fixture
def mock_query() -> MagicMock:
    query = MagicMock(spec=Select)
    query.where.return_value = query
    query.options.return_value = query
    return query
