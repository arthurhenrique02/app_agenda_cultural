"""User repository — all direct DB access for the users table."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    """Return the User with the given email, or None if not found."""
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    name: str,
    email: str,
    hashed_password: str,
) -> User:
    """Persist a new user and return the created instance."""
    user = User(name=name, email=email, hashed_password=hashed_password)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
