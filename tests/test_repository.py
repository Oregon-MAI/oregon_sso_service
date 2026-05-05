from typing import cast
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pytest
from sqlalchemy.exc import NoResultFound

from src.data.models.role import Role
from src.data.models.token import Token
from src.data.models.user import User
from src.data.repositories import auth_repository, role_repository, user_repository
from src.data.schemas.user import UserUpdateDto


@pytest.mark.asyncio
@patch.object(auth_repository, "async_session")
async def test_get_token_success(
    mock_session_factory: MagicMock,
    mock_session: MagicMock,
    mock_query: MagicMock,
    sample_token: Token,
) -> None:
    mock_session_factory.return_value.__aenter__.return_value = mock_session

    mock_result = MagicMock()
    mock_result.scalar_one.return_value = sample_token
    mock_session.execute.return_value = mock_result

    with patch.object(auth_repository, "select", return_value=mock_query):
        result = await auth_repository.get_token(cast(UUID, sample_token.id))

    assert result == sample_token
    mock_session.execute.assert_awaited_once()
    mock_session.begin.assert_called_once()


@pytest.mark.asyncio
@patch.object(auth_repository, "async_session")
async def test_get_token_not_found(
    mock_session_factory: MagicMock,
    mock_session: MagicMock,
    mock_query: MagicMock,
) -> None:
    mock_session_factory.return_value.__aenter__.return_value = mock_session

    mock_result = MagicMock()
    mock_result.scalar_one.side_effect = NoResultFound
    mock_session.execute.return_value = mock_result

    with (
        patch.object(auth_repository, "select", return_value=mock_query),
        pytest.raises(NoResultFound),
    ):
        await auth_repository.get_token(uuid4())


@pytest.mark.asyncio
@patch.object(auth_repository, "async_session")
async def test_insert_token_success(
    mock_session_factory: MagicMock,
    mock_session: MagicMock,
    sample_token: Token,
) -> None:
    mock_session_factory.return_value.__aenter__.return_value = mock_session

    await auth_repository.insert_token(sample_token)

    mock_session.add.assert_called_once_with(sample_token)
    mock_session.begin.assert_called_once()


@pytest.mark.asyncio
@patch.object(auth_repository, "async_session")
async def test_update_token_success(
    mock_session_factory: MagicMock,
    mock_session: MagicMock,
    mock_query: MagicMock,
    sample_token: Token,
) -> None:
    mock_session_factory.return_value.__aenter__.return_value = mock_session

    existing_token = Token(id=cast(UUID, sample_token.id), token="old", status=True)
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = existing_token
    mock_session.execute.return_value = mock_result

    with patch.object(auth_repository, "select", return_value=mock_query):
        sample_token.status = False
        await auth_repository.update_token(sample_token)

    assert existing_token.status is False


@pytest.mark.asyncio
@patch.object(role_repository, "async_session")
async def test_get_roles_success(
    mock_session_factory: MagicMock,
    mock_session: MagicMock,
    mock_query: MagicMock,
    sample_role: Role,
) -> None:
    mock_session_factory.return_value.__aenter__.return_value = mock_session

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [sample_role]

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    with patch.object(role_repository, "select", return_value=mock_query):
        result = await role_repository.get_roles()

    assert len(result) == 1
    assert result[0] == sample_role


@pytest.mark.asyncio
@patch.object(role_repository, "async_session")
async def test_get_role_success(
    mock_session_factory: MagicMock,
    mock_session: MagicMock,
    mock_query: MagicMock,
    sample_role: Role,
) -> None:
    mock_session_factory.return_value.__aenter__.return_value = mock_session

    mock_result = MagicMock()
    mock_result.scalar_one.return_value = sample_role
    mock_session.execute.return_value = mock_result

    with patch.object(role_repository, "select", return_value=mock_query):
        result = await role_repository.get_role(cast(UUID, sample_role.id))

    assert result == sample_role


@pytest.mark.asyncio
@patch.object(role_repository, "async_session")
async def test_get_role_not_found(
    mock_session_factory: MagicMock,
    mock_session: MagicMock,
    mock_query: MagicMock,
) -> None:
    mock_session_factory.return_value.__aenter__.return_value = mock_session

    mock_result = MagicMock()
    mock_result.scalar_one.side_effect = NoResultFound
    mock_session.execute.return_value = mock_result

    with (
        patch.object(role_repository, "select", return_value=mock_query),
        pytest.raises(NoResultFound),
    ):
        await role_repository.get_role(uuid4())


@pytest.mark.asyncio
@patch.object(role_repository, "async_session")
async def test_insert_role_success(
    mock_session_factory: MagicMock,
    mock_session: MagicMock,
    sample_role: Role,
) -> None:
    mock_session_factory.return_value.__aenter__.return_value = mock_session

    await role_repository.insert_role(sample_role)
    mock_session.add.assert_called_once_with(sample_role)


@pytest.mark.asyncio
@patch.object(role_repository, "async_session")
@patch.object(role_repository, "delete")
async def test_delete_role_success(
    mock_delete_stmt: MagicMock,
    mock_session_factory: MagicMock,
    mock_session: MagicMock,
) -> None:
    mock_session_factory.return_value.__aenter__.return_value = mock_session
    mock_delete_stmt.return_value = MagicMock()

    role_id = uuid4()
    await role_repository.delete_role(role_id)

    mock_delete_stmt.assert_called_once()
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
@patch.object(user_repository, "async_session")
async def test_get_users_success(
    mock_session_factory: MagicMock,
    mock_session: MagicMock,
    mock_query: MagicMock,
    sample_user: User,
) -> None:
    mock_session_factory.return_value.__aenter__.return_value = mock_session

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [sample_user]

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    with patch.object(user_repository, "select", return_value=mock_query):
        result = await user_repository.get_users()

    assert len(result) == 1
    assert result[0] == sample_user


@pytest.mark.asyncio
@patch.object(user_repository, "async_session")
async def test_get_user_by_id_success(
    mock_session_factory: MagicMock,
    mock_session: MagicMock,
    mock_query: MagicMock,
    sample_user: User,
) -> None:
    mock_session_factory.return_value.__aenter__.return_value = mock_session

    mock_result = MagicMock()
    mock_result.scalar_one.return_value = sample_user
    mock_session.execute.return_value = mock_result

    with patch.object(user_repository, "select", return_value=mock_query):
        result = await user_repository.get_user_by_id(cast(UUID, sample_user.id))

    assert result == sample_user


@pytest.mark.asyncio
@patch.object(user_repository, "async_session")
async def test_get_user_by_id_not_found(
    mock_session_factory: MagicMock,
    mock_session: MagicMock,
    mock_query: MagicMock,
) -> None:
    mock_session_factory.return_value.__aenter__.return_value = mock_session

    mock_result = MagicMock()
    mock_result.scalar_one.side_effect = NoResultFound
    mock_session.execute.return_value = mock_result

    with (
        patch.object(user_repository, "select", return_value=mock_query),
        pytest.raises(NoResultFound),
    ):
        await user_repository.get_user_by_id(uuid4())


@pytest.mark.asyncio
@patch.object(user_repository, "async_session")
async def test_get_user_by_login_success(
    mock_session_factory: MagicMock,
    mock_session: MagicMock,
    mock_query: MagicMock,
    sample_user: User,
) -> None:
    mock_session_factory.return_value.__aenter__.return_value = mock_session

    mock_result = MagicMock()
    mock_result.scalar_one.return_value = sample_user
    mock_session.execute.return_value = mock_result

    with patch.object(user_repository, "select", return_value=mock_query):
        result = await user_repository.get_user_by_login(cast(str, sample_user.login))

    assert result == sample_user


@pytest.mark.asyncio
@patch.object(user_repository, "async_session")
async def test_get_user_by_login_not_found(
    mock_session_factory: MagicMock,
    mock_session: MagicMock,
    mock_query: MagicMock,
) -> None:
    mock_session_factory.return_value.__aenter__.return_value = mock_session

    mock_result = MagicMock()
    mock_result.scalar_one.side_effect = NoResultFound
    mock_session.execute.return_value = mock_result

    with (
        patch.object(user_repository, "select", return_value=mock_query),
        pytest.raises(NoResultFound),
    ):
        await user_repository.get_user_by_login("nonexistent")


@pytest.mark.asyncio
@patch.object(user_repository, "async_session")
async def test_insert_user_success(
    mock_session_factory: MagicMock,
    mock_session: MagicMock,
    sample_user: User,
) -> None:
    mock_session_factory.return_value.__aenter__.return_value = mock_session

    await user_repository.insert_user(sample_user)
    mock_session.add.assert_called_once_with(sample_user)


@pytest.mark.asyncio
@patch.object(user_repository, "async_session")
async def test_update_user_not_found(
    mock_session_factory: MagicMock,
    mock_session: MagicMock,
    mock_query: MagicMock,
) -> None:
    mock_session_factory.return_value.__aenter__.return_value = mock_session

    mock_result = MagicMock()
    mock_result.scalar_one.side_effect = NoResultFound
    mock_session.execute.return_value = mock_result

    update_dto = UserUpdateDto(
        id=uuid4(), password="hash", name="T", surname="U", email="t@t.com", roles=[]
    )

    with (
        patch.object(user_repository, "select", return_value=mock_query),
        pytest.raises(Exception),  # noqa: B017
    ):
        await user_repository.update_user(update_dto)


@pytest.mark.asyncio
@patch.object(user_repository, "async_session")
@patch.object(user_repository, "delete")
async def test_delete_user_success(
    mock_delete_stmt: MagicMock,
    mock_session_factory: MagicMock,
    mock_session: MagicMock,
) -> None:
    mock_session_factory.return_value.__aenter__.return_value = mock_session
    mock_delete_stmt.return_value = MagicMock()

    user_id = uuid4()
    await user_repository.delete_user(user_id)

    mock_delete_stmt.assert_called_once()
    mock_session.execute.assert_awaited_once()
