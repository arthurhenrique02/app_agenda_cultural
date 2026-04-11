"""Auth service — business logic for registration and authentication."""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories import user as user_repo
from app.security.password import hash_password


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
