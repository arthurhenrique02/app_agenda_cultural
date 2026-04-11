"""Tests for the admin seed function (US-013)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models import Base
from app.models.user import UserRole
from app.repositories.user import get_user_by_email
from app.seed import seed_admin, seed_default_categories

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db() -> AsyncSession:
    """Isolated async session with all tables created."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


async def test_seed_creates_admin_user(db: AsyncSession) -> None:
    """seed_admin should create admin@agendacultural.com with role admin."""
    await seed_admin(db)
    user = await get_user_by_email(db, "admin@agendacultural.com")
    assert user is not None
    assert user.role == UserRole.admin
    assert user.is_active is True


async def test_seed_admin_password_is_hashed(db: AsyncSession) -> None:
    """Admin password must be stored as argon2 hash, not plaintext."""
    await seed_admin(db)
    user = await get_user_by_email(db, "admin@agendacultural.com")
    assert user is not None
    assert user.hashed_password.startswith("$argon2")


async def test_seed_is_idempotent(db: AsyncSession) -> None:
    """Calling seed_admin twice must not raise and must not duplicate the user."""
    await seed_admin(db)
    await seed_admin(db)  # should not raise or duplicate
    from sqlalchemy import func, select

    from app.models.user import User

    result = await db.execute(
        select(func.count()).where(User.email == "admin@agendacultural.com")
    )
    count = result.scalar_one()
    assert count == 1


async def test_seed_admin_uses_env_password(
    db: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    """seed_admin should use ADMIN_DEFAULT_PASSWORD env var for password."""
    import app.seed as seed_module
    from app.security.password import verify_password

    monkeypatch.setattr(seed_module.settings, "admin_default_password", "supersecret42")
    await seed_admin(db)
    user = await get_user_by_email(db, "admin@agendacultural.com")
    assert user is not None
    assert verify_password("supersecret42", user.hashed_password) is True


async def test_seed_admin_name_is_set(db: AsyncSession) -> None:
    """Seeded admin should have a non-empty name."""
    await seed_admin(db)
    user = await get_user_by_email(db, "admin@agendacultural.com")
    assert user is not None
    assert user.name  # non-empty


async def test_seed_default_categories_creates_expected_set(db: AsyncSession) -> None:
    """seed_default_categories must create PRD default category names."""
    from sqlalchemy import select

    from app.models.category import Category

    await seed_default_categories(db)

    result = await db.execute(select(Category.name))
    names = set(result.scalars().all())
    assert names == {"show", "exposicao", "peca", "festival", "outro"}


async def test_seed_default_categories_is_idempotent(db: AsyncSession) -> None:
    """Running category seed twice must not create duplicate category rows."""
    from sqlalchemy import func, select

    from app.models.category import Category

    await seed_default_categories(db)
    await seed_default_categories(db)

    result = await db.execute(select(func.count()).select_from(Category))
    count = result.scalar_one()
    assert count == 5
