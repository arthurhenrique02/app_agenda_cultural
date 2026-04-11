"""Auth dependencies — get_current_user for protecting routes."""

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.user import User, UserRole
from app.repositories import user as user_repo
from app.security.jwt import decode_token

_bearer = HTTPBearer(auto_error=False)

_UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
    headers={"WWW-Authenticate": "Bearer"},
)

_FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not enough permissions.",
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    session: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate the Bearer token; return the authenticated User.

    Raises HTTP 401 when:
    - No Authorization header is present
    - The token is invalid or expired
    - The token is not an access token
    - The referenced user does not exist
    """
    if credentials is None:
        raise _UNAUTHORIZED

    token = credentials.credentials
    try:
        payload = decode_token(token)
    except jwt.PyJWTError:
        raise _UNAUTHORIZED

    if payload.get("token_type") != "access":
        raise _UNAUTHORIZED

    user_id_str: str | None = payload.get("sub")
    if not user_id_str:
        raise _UNAUTHORIZED

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise _UNAUTHORIZED

    user = await user_repo.get_user_by_id(session, user_id)
    if user is None:
        raise _UNAUTHORIZED

    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the authenticated user has admin role."""
    if current_user.role != UserRole.admin:
        raise _FORBIDDEN
    return current_user
