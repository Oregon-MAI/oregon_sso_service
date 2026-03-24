import logging
from uuid import UUID

from fastapi import APIRouter, Depends

from src.data.models.token import Token
from src.data.schemas.user import UserLoginDto
from src.services.security_service import get_refresh_tokens_data, validate_token
from src.services.security_service import login as security_login
from src.services.security_service import refresh as security_refresh

router = APIRouter(prefix='')


@router.post("/login")
async def auth(user_in: UserLoginDto) -> dict[str, str]:
    logging.info('POST: /login.')
    return await security_login(user_in)


@router.get("/validate")
async def validate(data: dict[str, str] = Depends(validate_token)) -> dict[str, str]:
    logging.info('GET: /validate.')
    return data


@router.get("/refresh")
async def refresh(data: tuple[Token, UUID] = Depends(get_refresh_tokens_data)) -> dict[str, str]:
    logging.info('GET: /refresh.')
    return await security_refresh(data[1], data[0])
