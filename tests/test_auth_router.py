from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.routers.auth_router import router
from src.data.models.token import Token
from src.services.security_service import get_refresh_tokens_data, validate_token

app = FastAPI()
app.include_router(router)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.mark.asyncio
def test_auth_login(client: TestClient) -> None:
    login_data = {"login": "testuser", "password": "password"}

    with patch("src.api.routers.auth_router.security_login", new_callable=AsyncMock) as mock_login:
        mock_login.return_value = {"access_token": "token", "refresh_token": "refresh"}

        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 200
        assert response.json() == {"access_token": "token", "refresh_token": "refresh"}
        mock_login.assert_awaited_once()


@pytest.mark.asyncio
def test_validate_token(client: TestClient) -> None:
    user_id = uuid4()
    app.dependency_overrides[validate_token] = lambda: {"sub": str(user_id)}

    response = client.post("/api/v1/auth/validate")

    assert response.status_code == 200
    assert response.json() == {"sub": str(user_id)}
    app.dependency_overrides = {}


@pytest.mark.asyncio
def test_refresh_token(client: TestClient) -> None:
    user_id = uuid4()
    mock_token = MagicMock(spec=Token)

    async def override_get_refresh_tokens_data() -> tuple[Token, str]:
        return mock_token, str(user_id)

    app.dependency_overrides[get_refresh_tokens_data] = override_get_refresh_tokens_data

    with patch(
        "src.api.routers.auth_router.security_refresh", new_callable=AsyncMock
    ) as mock_refresh:
        mock_refresh.return_value = {"access_token": "new_token"}

        response = client.post("/api/v1/auth/refresh")

        assert response.status_code == 200
        assert response.json() == {"access_token": "new_token"}
        mock_refresh.assert_awaited_once_with(str(user_id), mock_token)

    app.dependency_overrides = {}


@pytest.mark.asyncio
def test_register_user(client: TestClient) -> None:
    user_data = {
        "login": "newuser",
        "password": "password",
        "name": "Test",
        "surname": "User",
        "email": "test@example.com",
    }

    with patch("src.api.routers.auth_router.create_user", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = {"status": "created"}

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 200
        assert response.json() == {"status": "created"}
        mock_create.assert_awaited_once()
