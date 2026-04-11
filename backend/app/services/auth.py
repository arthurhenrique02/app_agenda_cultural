"""Auth service — business logic for registration and authentication."""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories import user as user_repo
from app.schemas.auth import TokenResponse
from app.security.jwt import create_access_token, create_refresh_token
from app.security.password import hash_password, verify_password


async def register_user(
    session: AsyncSession, name: str, email: str, password: str
) -> User:
    """Register a new user.

    Raises HTTP 400 if the email is already taken.
    """
    existing = await user_repo.get_user_by_email(session, email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )

    hashed = hash_password(password)
    return await user_repo.create_user(
        session, name=name, email=email, hashed_password=hashed
    )


async def login_user(session: AsyncSession, email: str, password: str) -> TokenResponse:
    """Authenticate a user and return access + refresh tokens.

    Raises HTTP 401 if credentials are invalid.
    """
    user = await user_repo.get_user_by_email(session, email)
    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )

    subject = str(user.id)
    return TokenResponse(
        access_token=create_access_token(subject),
        refresh_token=create_refresh_token(subject),
    )
