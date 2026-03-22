import datetime
from uuid import UUID, uuid4

import jwt
from fastapi import Depends, HTTPException
from starlette import status

from app.data.models.token import Token
from app.data.models.user import User
from app.data.repositories.auth_repository import insert_token, update_token, get_token
from app.data.repositories.user_repository import get_user, get_users
from app.data.schemas.user import UserLoginDto
from constants import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    SCHEME,
    SECRET_KEY,
)


async def login(user_in: UserLoginDto):
    users: list[User] = await get_users()
    for user in users:
        if user_in.login == user.login and user.check_password(user_in.password):
            id_refresh: UUID = uuid4()
            access_token = await create_jwt({"id": str(user.id), "roles": [role.name for role in list(user.roles)]},
                                            "access")
            refresh_token = await create_jwt({"id": str(id_refresh), "user_id": str(user.id)}, "refresh")
            await insert_token(Token(id_refresh, refresh_token, True))
            return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}
    return {"error": "Invalid credentials"}


async def refresh(current_user: UUID, token: Token):
    user = await get_user(current_user)
    id_refresh: UUID = uuid4()
    access_token = await create_jwt({"id": str(user.id), "roles": [role.name for role in list(user.roles)]}, "access")
    refresh_token = await create_jwt({"id": str(id_refresh), "user_id": str(user.id)}, "refresh")
    token.status = False
    await update_token(token)
    await insert_token(Token(id_refresh, refresh_token, True))
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


async def create_jwt(data: dict, type: str):
    encode_data = data.copy()
    time = datetime.datetime.utcnow()
    if type == "access":
        time += datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        time += datetime.timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    encode_data.update({"exp": time})
    return jwt.encode(encode_data, SECRET_KEY, algorithm=ALGORITHM)


async def get_refresh_tokens_data(token: str = Depends(SCHEME)) -> tuple[Token, UUID]:
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        token_from_db = await get_token(UUID(data.get("id")))
        if token_from_db is None or token_from_db.status is False:
            raise jwt.InvalidTokenError
        return token_from_db, UUID(data.get("user_id"))

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="The token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_access_tokens_data(token: str = Depends(SCHEME)):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return data.get("id")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
