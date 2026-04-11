"""Database seeding utilities for Agenda Cultural."""

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.category import Category
from app.models.user import UserRole
from app.repositories.user import create_user, get_user_by_email
from app.security.password import hash_password

DEFAULT_CATEGORIES: tuple[tuple[str, str], ...] = (
    ("show", "Eventos musicais e apresentações ao vivo"),
    ("exposicao", "Exposições de arte, fotografia e instalações"),
    ("peca", "Peças de teatro e espetáculos cênicos"),
    ("festival", "Festivais culturais, gastronômicos e temáticos"),
    ("outro", "Outros tipos de eventos culturais"),
)


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


async def seed_default_categories(session: AsyncSession) -> None:
    """Create default event categories if they do not already exist.

    Idempotent: safe to call multiple times without creating duplicates.
    """
    result = await session.execute(select(Category.name))
    existing_names = set(result.scalars().all())

    created_any = False
    for name, description in DEFAULT_CATEGORIES:
        if name in existing_names:
            continue
        session.add(Category(name=name, description=description))
        created_any = True

    if created_any:
        await session.commit()


async def _run() -> None:  # pragma: no cover
    """Entry point for running seed from the command line."""
    from app.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        await seed_admin(session)
        await seed_default_categories(session)
        print("Admin user and default categories seeded successfully.")


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(_run())
