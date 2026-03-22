from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.data.schemas.role import RoleCreateDto, RoleDto


class UserCreateDto(BaseModel):
    login: str
    password: str
    name: str
    surname: str
    email: EmailStr
    roles: list[RoleCreateDto]

class UserUpdateDto(BaseModel):
    id: UUID
    password: str
    name: str
    surname: str
    email: EmailStr
    roles: list[RoleCreateDto]

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
