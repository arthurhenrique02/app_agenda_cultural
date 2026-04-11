"""Tests for the User model — US-006."""

import pytest
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.user import User, UserRole

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def session() -> AsyncSession:
    """Provide an in-memory SQLite session with the users table created."""
    from app.models.base import Base

    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as sess:
        yield sess

    await engine.dispose()


def test_user_role_enum_values() -> None:
    """UserRole enum must have 'user' and 'admin' values."""
    assert UserRole.user.value == "user"
    assert UserRole.admin.value == "admin"


def test_user_model_has_required_fields() -> None:
    """User model must declare all required columns."""
    mapper = inspect(User)
    columns = {c.key for c in mapper.columns}
    required = {
        "id",
        "name",
        "email",
        "hashed_password",
        "role",
        "is_active",
        "created_at",
    }
    assert required.issubset(columns), f"Missing columns: {required - columns}"


async def test_user_can_be_created(session: AsyncSession) -> None:
    """A user record can be inserted and retrieved."""
    user = User(
        name="Alice",
        email="alice@example.com",
        hashed_password="hashed_pw",
        role=UserRole.user,
        is_active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    assert user.id is not None
    assert user.name == "Alice"
    assert user.email == "alice@example.com"
    assert user.role == UserRole.user
    assert user.is_active is True
    assert user.created_at is not None


async def test_user_default_role_is_user(session: AsyncSession) -> None:
    """Default role for a new user must be 'user'."""
    user = User(
        name="Bob",
        email="bob@example.com",
        hashed_password="hashed_pw",
        is_active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    assert user.role == UserRole.user


async def test_user_default_is_active_true(session: AsyncSession) -> None:
    """Default is_active must be True."""
    user = User(
        name="Carol",
        email="carol@example.com",
        hashed_password="hashed_pw",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    assert user.is_active is True


async def test_user_email_unique_constraint(session: AsyncSession) -> None:
    """Inserting two users with the same email must raise an integrity error."""
    from sqlalchemy.exc import IntegrityError

    user1 = User(name="Dave", email="dave@example.com", hashed_password="pw1")
    user2 = User(name="Dave2", email="dave@example.com", hashed_password="pw2")
    session.add(user1)
    await session.commit()

    session.add(user2)
    with pytest.raises(IntegrityError):
        await session.commit()


async def test_admin_user_can_be_created(session: AsyncSession) -> None:
    """A user can be assigned the admin role."""
    user = User(
        name="Admin",
        email="admin@example.com",
        hashed_password="hashed_pw",
        role=UserRole.admin,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    assert user.role == UserRole.admin


def test_user_table_name() -> None:
    """Users table must be named 'users'."""
    assert User.__tablename__ == "users"
