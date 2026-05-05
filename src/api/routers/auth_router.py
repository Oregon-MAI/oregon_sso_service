from typing import Any
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends
from opentelemetry import trace

from src.data.models.token import Token
from src.data.schemas.user import UserCreateDto, UserLoginDto
from src.services.security_service import get_refresh_tokens_data, validate_token
from src.services.security_service import login as security_login
from src.services.security_service import refresh as security_refresh
from src.services.user_service import create_user

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

logger = structlog.get_logger(__name__)


@router.post(
    "/login",
    summary="User authentication",
    description="Authenticate user with login and password. Returns user data and JWT tokens.",
    response_description="User profile with access and refresh tokens",
)
async def auth(user_in: UserLoginDto) -> dict[str, Any]:
    span = trace.get_current_span()
    logger.info(
        "Login",
        method="POST",
        trace_id=f"{span.get_span_context().trace_id:032x}",
        endpoint="/api/v1/auth/login",
    )
    return await security_login(user_in)


@router.post(
    "/validate",
    summary="Validate access token",
    description="Check if provided JWT access token is valid and not expired.",
    response_description="Token validation result",
)
async def validate(data: dict[str, str] = Depends(validate_token)) -> dict[str, Any]:
    span = trace.get_current_span()
    logger.info(
        "validate",
        method="POST",
        trace_id=f"{span.get_span_context().trace_id:032x}",
        endpoint="/api/v1/auth/validate",
    )
    return data


@router.post(
    "/refresh",
    summary="Refresh authentication tokens",
    description="Use valid refresh token to obtain new token. Old refresh token is invalidated.",
    response_description="New access and refresh tokens",
)
async def refresh(data: tuple[Token, UUID] = Depends(get_refresh_tokens_data)) -> dict[str, str]:
    span = trace.get_current_span()
    logger.info(
        "refresh",
        method="POST",
        trace_id=f"{span.get_span_context().trace_id:032x}",
        endpoint="/api/v1/auth/refresh",
    )
    return await security_refresh(data[1], data[0])


@router.post(
    "/register",
    summary="Register new user",
    description="Create new user account with provided credentials. Returns new user data.",
    response_description="Register for new user",
)
async def create(new_user: UserCreateDto) -> dict[str, str]:
    span = trace.get_current_span()
    logger.info(
        "register",
        method="POST",
        trace_id=f"{span.get_span_context().trace_id:032x}",
        endpoint="/api/v1/auth/register",
    )
    return await create_user(new_user)
