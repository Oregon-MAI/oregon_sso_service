from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

import src.services.role_service as service
from src.data.models.role import Role
from src.data.models.user import User
from src.data.schemas.role import RoleCreateDto, RoleDeleteDto, RoleDto, RoleUpdateDto


@pytest.fixture
def admin_user() -> MagicMock:
    user = MagicMock(spec=User)
    user.id = uuid4()
    admin_role = MagicMock(spec=Role)
    admin_role.name = "admin"
    user.roles = [admin_role]
    return user


@pytest.fixture
def regular_user() -> MagicMock:
    user = MagicMock(spec=User)
    user.id = uuid4()
    regular_role = MagicMock(spec=Role)
    regular_role.name = "user"
    user.roles = [regular_role]
    return user


@pytest.fixture
def db_role() -> MagicMock:
    role = MagicMock(spec=Role)
    role.id = uuid4()
    role.name = "test_role"
    role.description = "Test Description"
    return role


@pytest.mark.asyncio
async def test_get_roles_success(db_role: MagicMock) -> None:
    with patch.object(service, "get_roles", new_callable=AsyncMock, return_value=[db_role]):
        result = await service.roles()
        assert len(result) == 1
        assert isinstance(result[0], RoleDto)
        assert result[0].name == "test_role"


@pytest.mark.asyncio
async def test_get_roles_empty_list() -> None:
    with patch.object(service, "get_roles", new_callable=AsyncMock, return_value=[]):
        result = await service.roles()
        assert result == []


@pytest.mark.asyncio
async def test_get_roles_none_raises_500() -> None:
    with patch.object(service, "get_roles", new_callable=AsyncMock, return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            await service.roles()
        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_get_role_success(db_role: MagicMock) -> None:
    role_id = uuid4()
    db_role.id = role_id
    with patch.object(service, "get_role", new_callable=AsyncMock, return_value=db_role):
        result = await service.role(role_id)
        assert isinstance(result, RoleDto)
        assert result.id == role_id


@pytest.mark.asyncio
async def test_get_role_not_found() -> None:
    role_id = uuid4()
    with patch.object(service, "get_role", new_callable=AsyncMock, return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            await service.role(role_id)
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_create_role_success(admin_user: MagicMock) -> None:
    role_in = RoleCreateDto(name="new_role", description="New Role")
    user_id = uuid4()
    with (
        patch.object(service, "get_user_by_id", new_callable=AsyncMock, return_value=admin_user),
        patch.object(service, "ADMIN_USERNAME", "admin"),
        patch.object(service, "insert", new_callable=AsyncMock) as mock_insert,
    ):
        result = await service.create_role(role_in, user_id)
        assert result == {"Info": "Success"}
        mock_insert.assert_called_once()


@pytest.mark.asyncio
async def test_create_role_forbidden(regular_user: MagicMock) -> None:
    role_in = RoleCreateDto(name="new_role", description="New Role")
    user_id = uuid4()
    with (
        patch.object(service, "get_user_by_id", new_callable=AsyncMock, return_value=regular_user),
        patch.object(service, "ADMIN_USERNAME", "admin"),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await service.create_role(role_in, user_id)
        assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_create_role_user_not_found() -> None:
    role_in = RoleCreateDto(name="new_role", description="New Role")
    user_id = uuid4()
    with patch.object(service, "get_user_by_id", new_callable=AsyncMock, return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            await service.create_role(role_in, user_id)
        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_update_role_success(admin_user: MagicMock) -> None:
    role_in = RoleUpdateDto(id=uuid4(), name="updated", description="Updated")
    user_id = uuid4()
    with (
        patch.object(service, "get_user_by_id", new_callable=AsyncMock, return_value=admin_user),
        patch.object(service, "ADMIN_USERNAME", "admin"),
        patch.object(service, "update", new_callable=AsyncMock) as mock_update,
    ):
        result = await service.update_role(role_in, user_id)
        assert result == {"Info": "Success"}
        mock_update.assert_called_once_with(role_in)


@pytest.mark.asyncio
async def test_update_role_forbidden(regular_user: MagicMock) -> None:
    role_in = RoleUpdateDto(id=uuid4(), name="updated", description="Updated")
    user_id = uuid4()
    with (
        patch.object(service, "get_user_by_id", new_callable=AsyncMock, return_value=regular_user),
        patch.object(service, "ADMIN_USERNAME", "admin"),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await service.update_role(role_in, user_id)
        assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_update_role_user_not_found() -> None:
    role_in = RoleUpdateDto(id=uuid4(), name="updated", description="Updated")
    user_id = uuid4()
    with patch.object(service, "get_user_by_id", new_callable=AsyncMock, return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            await service.update_role(role_in, user_id)
        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_delete_role_success(admin_user: MagicMock) -> None:
    role_id = uuid4()
    role_in = RoleDeleteDto(id=role_id)
    user_id = uuid4()
    with (
        patch.object(service, "get_user_by_id", new_callable=AsyncMock, return_value=admin_user),
        patch.object(service, "ADMIN_USERNAME", "admin"),
        patch.object(service, "delete", new_callable=AsyncMock) as mock_delete,
    ):
        result = await service.delete_role(role_in, user_id)
        assert result == {"Info": "Success"}
        mock_delete.assert_called_once_with(role_id)


@pytest.mark.asyncio
async def test_delete_role_forbidden(regular_user: MagicMock) -> None:
    role_in = RoleDeleteDto(id=uuid4())
    user_id = uuid4()
    with (
        patch.object(service, "get_user_by_id", new_callable=AsyncMock, return_value=regular_user),
        patch.object(service, "ADMIN_USERNAME", "admin"),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await service.delete_role(role_in, user_id)
        assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_delete_role_user_not_found() -> None:
    role_in = RoleDeleteDto(id=uuid4())
    user_id = uuid4()
    with patch.object(service, "get_user_by_id", new_callable=AsyncMock, return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            await service.delete_role(role_in, user_id)
        assert exc_info.value.status_code == 500
