from uuid import UUID

import structlog
from fastapi import APIRouter, Depends
from opentelemetry import trace

from src.data.schemas.role import RoleCreateDto, RoleDeleteDto, RoleDto, RoleUpdateDto
from src.services.role_service import (
    create_role,
    delete_role,
    update_role,
)
from src.services.role_service import (
    role as get_role,
)
from src.services.role_service import (
    roles as get_roles,
)
from src.services.security_service import get_access_tokens_data

router = APIRouter(prefix="/api/v1/roles", tags=["Roles"])

logger = structlog.get_logger(__name__)


@router.get(
    "/roles",
    summary="Get all roles",
    description="Retrieve a list of all available roles in the system. Requires valid access token.",
    response_description="List of role objects",
)
async def roles(current_user: UUID = Depends(get_access_tokens_data)) -> list[RoleDto]:
    span = trace.get_current_span()
    logger.info(
        "roles",
        method="GET",
        user_id=str(current_user),
        trace_id=f"{span.get_span_context().trace_id:032x}",
        endpoint="/api/v1/roles/roles",
    )
    return await get_roles()


@router.get(
    "/role",
    summary="Get role by ID",
    description="Retrieve detailed information about a specific role by its UUID. Requires valid access token.",
    response_description="Role",
)
async def role(id: UUID, current_user: UUID = Depends(get_access_tokens_data)) -> RoleDto:
    span = trace.get_current_span()
    logger.info(
        "role",
        method="GET",
        user_id=str(current_user),
        trace_id=f"{span.get_span_context().trace_id:032x}",
        endpoint="/api/v1/roles/role",
    )
    return await get_role(id)


@router.post(
    "/create_role",
    summary="Create new role",
    description="Create a new role with specified name and description.",
    response_description="Operation result",
)
async def create(
    new_role: RoleCreateDto, current_user: UUID = Depends(get_access_tokens_data)
) -> dict[str, str]:
    span = trace.get_current_span()
    logger.info(
        "create_role",
        method="POST",
        user_id=str(current_user),
        trace_id=f"{span.get_span_context().trace_id:032x}",
        endpoint="/api/v1/roles/create_role",
    )
    return await create_role(new_role, current_user)


@router.patch(
    "/update_role",
    summary="Update existing role",
    description="Update name and/or description of an existing role. Requires admin privileges.",
    response_description="Operation result",
)
async def update(
    updated_role: RoleUpdateDto, current_user: UUID = Depends(get_access_tokens_data)
) -> dict[str, str]:
    span = trace.get_current_span()
    logger.info(
        "update_role",
        method="PATCH",
        user_id=str(current_user),
        trace_id=f"{span.get_span_context().trace_id:032x}",
        endpoint="/api/v1/roles/update_role",
    )
    return await update_role(updated_role, current_user)


@router.delete(
    "/delete_role",
    summary="Delete role",
    description="Permanently delete a role by its ID. Requires admin privileges. Use with caution.",
    response_description="Operation result",
)
async def delete(
    deleted_role: RoleDeleteDto, current_user: UUID = Depends(get_access_tokens_data)
) -> dict[str, str]:
    span = trace.get_current_span()
    logger.info(
        "delete_role",
        method="DELETE",
        user_id=str(current_user),
        trace_id=f"{span.get_span_context().trace_id:032x}",
        endpoint="/api/v1/roles/delete_role",
    )
    return await delete_role(deleted_role, current_user)
