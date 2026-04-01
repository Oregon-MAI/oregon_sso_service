import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import jwt
import pytest
from fastapi import HTTPException
from starlette import status

from src.constants import ALGORITHM, SECRET_KEY
from src.data.models.token import Token
from src.data.models.user import User
from src.data.schemas.user import UserLoginDto
from src.services.security_service import (
    create_jwt,
    get_access_tokens_data,
    get_refresh_tokens_data,
    login,
    refresh,
    validate_token,
)


@pytest.fixture
def mock_user() -> MagicMock:
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.login = "testuser"
    user.first_name = "Test"
    user.last_name = "User"
    user.email = "test@example.com"

    role_mock = MagicMock()
    role_mock.name = "admin"
    user.roles = [role_mock]

    user.check_password = MagicMock(return_value=True)
    return user


@pytest.fixture
def mock_token() -> MagicMock:
    token = MagicMock(spec=Token)
    token.id = uuid4()
    token.token = "mock_refresh_token"
    token.status = True
    return token


@pytest.mark.asyncio
async def test_login_success(mock_user: MagicMock) -> None:
    user_in = UserLoginDto(login="testuser", password="correct_password")

    with (
        patch("src.services.security_service.get_user_by_login", AsyncMock(return_value=mock_user)),
        patch(
            "src.services.security_service.create_jwt",
            AsyncMock(side_effect=["access_123", "refresh_456"]),
        ),
        patch("src.services.security_service.insert_token", AsyncMock()),
    ):
        result = await login(user_in)

        assert result["access_token"] == "access_123"
        assert result["refresh_token"] == "refresh_456"
        assert result["id"] == str(mock_user.id)
        assert result["login"] == mock_user.login


@pytest.mark.asyncio
async def test_login_wrong_password(mock_user: MagicMock) -> None:
    user_in = UserLoginDto(login="testuser", password="wrong_password")
    mock_user.check_password.return_value = False

    with patch(
        "src.services.security_service.get_user_by_login", AsyncMock(return_value=mock_user)
    ):
        result = await login(user_in)
        assert result == {"Info": "Login Failed"}


@pytest.mark.asyncio
async def test_refresh_success(mock_user: MagicMock, mock_token: MagicMock) -> None:
    with (
        patch("src.services.security_service.get_user_by_id", AsyncMock(return_value=mock_user)),
        patch(
            "src.services.security_service.create_jwt",
            AsyncMock(side_effect=["new_access", "new_refresh"]),
        ),
        patch("src.services.security_service.update_token", AsyncMock()),
        patch("src.services.security_service.insert_token", AsyncMock()),
    ):
        result = await refresh(mock_user.id, mock_token)

        assert result["access_token"] == "new_access"
        assert result["refresh_token"] == "new_refresh"
        assert mock_token.status is False


@pytest.mark.asyncio
async def test_create_jwt_access_token() -> None:
    payload = {"id": str(uuid4()), "role": "admin"}
    token = await create_jwt(payload, "access")

    assert isinstance(token, str)
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["id"] == payload["id"]
    assert "exp" in decoded


@pytest.mark.asyncio
async def test_validate_token_valid(mock_token: MagicMock) -> None:
    token_id = uuid4()
    token_str = await create_jwt({"id": str(token_id)}, "access")
    mock_token.status = True

    with patch("src.services.security_service.get_token", AsyncMock(return_value=mock_token)):
        result = await validate_token(token_str)
        assert result == {"is_valid": "True"}


@pytest.mark.asyncio
async def test_validate_token_expired() -> None:
    expired_payload = {
        "id": str(uuid4()),
        "exp": datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=1),
    }
    expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as exc:
        await validate_token(expired_token)

    assert exc.value.status_code == 401
    assert exc.value.detail == {"is_valid": "False"}


@pytest.mark.asyncio
async def test_get_refresh_tokens_data_success(mock_token: MagicMock) -> None:
    user_id = uuid4()
    token_str = await create_jwt({"id": str(mock_token.id), "user_id": str(user_id)}, "refresh")

    with patch("src.services.security_service.get_token", AsyncMock(return_value=mock_token)):
        result_token, result_user_id = await get_refresh_tokens_data(token_str)

        assert result_token.id == mock_token.id
        assert result_user_id == user_id


@pytest.mark.asyncio
async def test_get_access_tokens_data_success() -> None:
    user_id = uuid4()
    token_str = await create_jwt({"id": str(user_id)}, "access")

    result = await get_access_tokens_data(token_str)
    assert result == user_id


@pytest.mark.asyncio
async def test_get_access_tokens_data_invalid() -> None:
    with pytest.raises(HTTPException) as exc:
        await get_access_tokens_data("invalid.token.payload")

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
