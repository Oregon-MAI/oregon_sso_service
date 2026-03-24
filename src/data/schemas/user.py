from uuid import UUID

from pydantic import BaseModel, EmailStr

from src.data.schemas.role import RoleConnectDto, RoleDto


class UserCreateDto(BaseModel):
    login: str
    password: str
    name: str
    surname: str
    email: EmailStr


class UserUpdateDto(BaseModel):
    id: UUID
    password: str
    name: str
    surname: str
    email: EmailStr
    roles: list[RoleConnectDto]


class UserConnectRoleDto(BaseModel):
    user_id: UUID
    role_id: UUID


class UserDeleteDto(BaseModel):
    id: UUID


class UserLoginDto(BaseModel):
    login: str
    password: str


class UserDto(BaseModel):
    id: UUID
    login: str
    name: str
    surname: str
    email: EmailStr
    roles: list[RoleDto]
