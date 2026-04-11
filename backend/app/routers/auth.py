"""Auth router — /api/auth endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.schemas.auth import RegisterRequest
from app.schemas.user import UserResponse
from app.services import auth as auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    body: RegisterRequest,
    session: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Create a new user account."""
    user = await auth_service.register_user(
        session,
        name=body.name,
        email=body.email,
        password=body.password,
    )
    return UserResponse.model_validate(user)
