from collections.abc import Generator
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.routers.user_router import router
from src.data.schemas.user import UserDto
from src.services.security_service import get_access_tokens_data

app = FastAPI()
app.include_router(router)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def auth_user_uuid() -> str:
    return str(uuid4())


@pytest.fixture
def _mock_auth(auth_user_uuid: str) -> Generator[None]:
    app.dependency_overrides[get_access_tokens_data] = lambda: auth_user_uuid
    yield
    app.dependency_overrides = {}


def test_get_users(client: TestClient, _mock_auth: None) -> None:
    with patch("src.api.routers.user_router.get_users", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = []

        response = client.get("/api/v1/user/users")

        assert response.status_code == 200
        assert response.json() == []
        mock_get.assert_awaited_once()


def test_get_user_by_id(client: TestClient, _mock_auth: None) -> None:
    user_id = uuid4()
    user_dto = UserDto(
        id=user_id,
        login="user1",
        name="Test",
        surname="Test",
        email="test@test.com",
        roles=[],
    )

    with patch("src.api.routers.user_router.get_user", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = user_dto

        response = client.get("/api/v1/user/user", params={"id": str(user_id)})

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(user_id)
        mock_get.assert_awaited_once_with(user_id)


def test_change_role(client: TestClient, _mock_auth: None) -> None:
    data = {"user_id": str(uuid4()), "role_id": str(uuid4())}

    with patch(
        "src.api.routers.user_router.update_user_role", new_callable=AsyncMock
    ) as mock_change:
        mock_change.return_value = {"status": "changed"}

        response = client.post("/api/v1/user/change_role", json=data)

        assert response.status_code == 200
        mock_change.assert_awaited_once()


def test_delete_user(client: TestClient, _mock_auth: None) -> None:
    user_id = uuid4()
    delete_data = {"id": str(user_id)}

    with patch("src.api.routers.user_router.delete_user", new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = {"status": "deleted"}

        response = client.request("DELETE", "/api/v1/user/delete_user", json=delete_data)

        assert response.status_code == 200
        mock_delete.assert_awaited_once()
