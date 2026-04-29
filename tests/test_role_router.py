from collections.abc import Generator
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.routers.role_router import router
from src.data.schemas.role import RoleDto
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


def test_get_roles(client: TestClient, _mock_auth: None) -> None:
    with patch("src.api.routers.role_router.get_roles", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = []

        response = client.get("/api/v1/roles/roles")

        assert response.status_code == 200
        assert response.json() == []
        mock_get.assert_awaited_once()


def test_get_role_by_id(client: TestClient, _mock_auth: None) -> None:
    role_id = uuid4()
    role_dto = RoleDto(id=role_id, name="Admin", description="Desc")

    with patch("src.api.routers.role_router.get_role", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = role_dto

        response = client.get("/api/v1/roles/role", params={"id": str(role_id)})

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(role_id)
        assert data["name"] == "Admin"
        mock_get.assert_awaited_once_with(role_id)


def test_create_role(client: TestClient, _mock_auth: None, auth_user_uuid: str) -> None:
    role_data = {"name": "User", "description": "User role"}

    with patch("src.api.routers.role_router.create_role", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = {"status": "created"}

        response = client.post("/api/v1/roles/create_role", json=role_data)

        assert response.status_code == 200
        assert response.json() == {"status": "created"}
        call_args = mock_create.call_args
        assert call_args[0][1] == auth_user_uuid


def test_update_role(client: TestClient, _mock_auth: None) -> None:
    role_id = uuid4()
    update_data = {"id": str(role_id), "name": "Updated", "description": "New Desc"}

    with patch("src.api.routers.role_router.update_role", new_callable=AsyncMock) as mock_update:
        mock_update.return_value = {"status": "updated"}

        response = client.patch("/api/v1/roles/update_role", json=update_data)

        assert response.status_code == 200
        mock_update.assert_awaited_once()


def test_delete_role(client: TestClient, _mock_auth: None) -> None:
    role_id = uuid4()
    delete_data = {"id": str(role_id)}

    with patch("src.api.routers.role_router.delete_role", new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = {"status": "deleted"}

        response = client.request("DELETE", "/api/v1/roles/delete_role", json=delete_data)

        assert response.status_code == 200
        mock_delete.assert_awaited_once()
