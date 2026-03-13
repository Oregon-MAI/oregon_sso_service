import jwt
import datetime
from fastapi import Depends, HTTPException
from typing import Dict
from starlette import status

from app.data.repositories.Repository import get_user, get_users
from app.data.schemas.User import UserDto
from constants import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SCHEME, REFRESH_TOKEN_EXPIRE_MINUTES

def login(user_in: UserDto):
    for user in get_users():
        if user_in.login == user.get("login") and user_in.password == user.get("password"):
            access_token = create_jwt({"sub": user.get("login")},"access")
            refresh_token = create_jwt({"sub": user.get("login")},"refresh")
            return {"access_token": access_token, "token_type": "bearer","refresh_token": refresh_token}
    return {"error": "Invalid credentials"}

def get_role(current_user: str):
    user = get_user(current_user)
    if user:
        return user
    return {"error": "User not found"}

def create_jwt(data: Dict,type:str):
    encode_data = data.copy()
    time = datetime.datetime.utcnow()
    if type == "access":
        time+=datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        time+=datetime.timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    encode_data.update({"exp":time })
    return jwt.encode(encode_data, SECRET_KEY, algorithm=ALGORITHM)

def get_tokens_data(token: str = Depends(SCHEME)):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        print(data)
        return data.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="The token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")