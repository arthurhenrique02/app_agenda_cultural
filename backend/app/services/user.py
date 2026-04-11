"""User service — business logic for profile management."""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories import user as user_repo


async def update_profile(
    session: AsyncSession,
    current_user: User,
    name: str | None,
    email: str | None,
) -> User:
    """Update the current user's name and/or email.

    Raises HTTP 400 if the new email is already taken by another user.
    """
    if email is not None and email != current_user.email:
        existing = await user_repo.get_user_by_email(session, email)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use.",
            )

    return await user_repo.update_user(session, current_user, name=name, email=email)
