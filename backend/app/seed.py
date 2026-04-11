"""Database seeding utilities for Agenda Cultural."""

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import UserRole
from app.repositories.user import create_user, get_user_by_email
from app.security.password import hash_password


async def seed_admin(session: AsyncSession) -> None:
    """Create the first admin user if it does not already exist.

    Idempotent: safe to call multiple times without creating duplicates.
    The admin password is read from settings.admin_default_password
    (env var ADMIN_DEFAULT_PASSWORD).
    """
    email = "admin@agendacultural.com"
    existing = await get_user_by_email(session, email)
    if existing is not None:
        return

    hashed = hash_password(settings.admin_default_password)
    user = await create_user(
        session,
        name="Administrador",
        email=email,
        hashed_password=hashed,
    )
    # Promote to admin role after creation
    user.role = UserRole.admin
    session.add(user)
    await session.commit()


async def _run() -> None:  # pragma: no cover
    """Entry point for running seed from the command line."""
    from app.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        await seed_admin(session)
        print("Admin user seeded successfully.")


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(_run())
