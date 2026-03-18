from pydantic import BaseModel, EmailStr

from app.data.schemas.Role import RoleDto

class UserCreateDto(BaseModel):
    login: str
    password: str
    name: str
    surname: str
    email: EmailStr
    role: RoleDto

class UserLoginDto(BaseModel):
    login: str
    password: str

class UserDto(BaseModel):
    id: int
    login: str
    name: str
    surname: str
    email: EmailStr
    role:RoleDto