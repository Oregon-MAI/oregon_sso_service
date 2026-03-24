from uuid import UUID

from app.data.models.user import User
from app.data.repositories.user_repository import delete_user as delete
from app.data.repositories.user_repository import get_user_by_id, get_users
from app.data.repositories.user_repository import insert_user as insert
from app.data.repositories.user_repository import update_user as update
from app.data.schemas.role import RoleConnectDto
from app.data.schemas.user import UserConnectRoleDto, UserCreateDto, UserDeleteDto, UserUpdateDto
from constants import ADMIN_USERNAME


async def users() -> list[User] | dict[str, str]:
    try:
        return await get_users()
    except Exception:
        return {"error": "something went wrong"}


async def user(id: UUID) -> User | dict[str, str]:
    try:
        return await get_user_by_id(id)
    except Exception:
        return {"error": "something went wrong"}


async def create_user(user_in: UserCreateDto, current_user: UUID) -> dict[str, str]:
    try:
        auth_user: User = await get_user_by_id(current_user)
        if any(role.name == ADMIN_USERNAME for role in list(auth_user.roles)):
            user: User = User(user_in.login, user_in.password, user_in.name, user_in.surname, user_in.email)
            await insert(user)
            return {"Info": user_in.dict()}
        return {"error": "you not have permission"}
    except Exception:
        return {"error": "something went wrong"}


async def change_role(data: UserConnectRoleDto, current_user: UUID) -> dict[str, str]:
    try:
        auth_user: User = await get_user_by_id(current_user)
        if any(role.name == ADMIN_USERNAME for role in list(auth_user.roles)):
            user: User =  await get_user_by_id(data.user_id)
            roles:list[RoleConnectDto] = [RoleConnectDto(id=el.id) for el in user.roles]
            roles.append(RoleConnectDto(id=data.role_id))
            user_to_update:UserUpdateDto = UserUpdateDto(id = user.id,password=user.password_hash, name = user.first_name, surname = user.last_name, email = user.email, roles = roles)
            await update(user_to_update)
            return {"Info": str(user)}
        return {"error": "you not have permission"}
    except Exception as e:
        return {"error": "something went wrong" + str(e)}


async def update_user(user_in: UserUpdateDto, current_user: UUID) -> dict[str, str]:
    try:
        auth_user: User = await get_user_by_id(current_user)
        if any(role.name == ADMIN_USERNAME for role in list(auth_user.roles)):
            await update(user_in)
            return {"Info": user_in.dict()}
        return {"error": "you not have permission"}
    except Exception:
        return {"error": "something went wrong"}


async def delete_user(user_in: UserDeleteDto, current_user: UUID) -> dict[str, str]:
    try:
        auth_user: User = await get_user_by_id(current_user)
        if any(role.name == ADMIN_USERNAME for role in list(auth_user.roles)):
            await delete(user_in.id)
            return {"Info": user_in.dict()}
        return {"error": "you not have permission"}
    except Exception:
        return {"error": "something went wrong"}
