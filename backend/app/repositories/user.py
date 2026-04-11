"""User repository — all direct DB access for the users table."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    """Return the User with the given id, or None if not found."""
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


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


async def count_users(session: AsyncSession) -> int:
    """Return total number of users."""
    result = await session.execute(select(func.count()).select_from(User))
    return int(result.scalar_one())


async def update_user(
    session: AsyncSession,
    user: User,
    name: str | None = None,
    email: str | None = None,
) -> User:
    """Update mutable profile fields on *user* and return the updated instance."""
    if name is not None:
        user.name = name
    if email is not None:
        user.email = email
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
