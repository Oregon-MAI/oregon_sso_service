from uuid import UUID

import structlog
from fastapi import APIRouter, Depends
from opentelemetry import trace

from src.data.schemas.user import UserConnectRoleDto, UserDeleteDto, UserDto
from src.services.security_service import get_access_tokens_data
from src.services.user_service import change_role as update_user_role
from src.services.user_service import delete_user
from src.services.user_service import user as get_user
from src.services.user_service import users as get_users

router = APIRouter(prefix="/api/v1/user", tags=["User"])

logger = structlog.get_logger(__name__)


@router.get(
    "/users",
    summary="Get all users",
    description="Retrieve a list of all registered users in the system. Requires valid access token.",
    response_description="List of user objects",
)
async def users(_current_user: UUID = Depends(get_access_tokens_data)) -> list[UserDto]:
    span = trace.get_current_span()
    logger.info(
        "users",
        method="GET",
        trace_id=f"{span.get_span_context().trace_id:032x}",
        endpoint="/api/v1/user/users",
    )
    return await get_users()


@router.get(
    "/user",
    summary="Get user by ID",
    description="Retrieve detailed information about a specific user by their UUID. Requires valid access token.",
    response_description="User",
)
async def user(id: UUID, _current_user: UUID = Depends(get_access_tokens_data)) -> UserDto:
    span = trace.get_current_span()
    logger.info(
        "user",
        method="GET",
        trace_id=f"{span.get_span_context().trace_id:032x}",
        endpoint="/api/v1/user/user",
    )
    return await get_user(id)


@router.post(
    "/change_role",
    summary="Change user role",
    description="Assign an additional role to a user. Requires admin privileges. User retains existing roles.",
    response_description="Operation result",
)
async def change_role(
    data: UserConnectRoleDto, current_user: UUID = Depends(get_access_tokens_data)
) -> dict[str, str]:
    span = trace.get_current_span()
    logger.info(
        "change_role",
        method="POST",
        trace_id=f"{span.get_span_context().trace_id:032x}",
        endpoint="/api/v1/user/change_role",
    )
    return await update_user_role(data, current_user)


@router.delete(
    "/delete_user",
    summary="Delete user",
    description="Permanently delete a user account by ID. Requires admin privileges.",
    response_description="Operation result",
)
async def delete(
    deleted_user: UserDeleteDto, current_user: UUID = Depends(get_access_tokens_data)
) -> dict[str, str]:
    span = trace.get_current_span()
    logger.info(
        "delete_user",
        method="DELETE",
        trace_id=f"{span.get_span_context().trace_id:032x}",
        endpoint="/api/v1/user/delete_user",
    )
    return await delete_user(deleted_user, current_user)
