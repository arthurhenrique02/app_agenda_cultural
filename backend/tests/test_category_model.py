"""Tests for the Category model - US-014."""

import pytest
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.category import Category

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def session() -> AsyncSession:
    """Provide an in-memory SQLite session with all tables created."""
    from app.models.base import Base

    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as sess:
        yield sess

    await engine.dispose()


def test_category_model_has_required_fields() -> None:
    """Category model must declare all required columns."""
    mapper = inspect(Category)
    columns = {c.key for c in mapper.columns}
    required = {"id", "name", "description", "created_at"}
    assert required.issubset(columns), f"Missing columns: {required - columns}"


async def test_category_can_be_created(session: AsyncSession) -> None:
    """A category record can be inserted and retrieved."""
    category = Category(name="show", description="Eventos musicais")
    session.add(category)
    await session.commit()
    await session.refresh(category)

    assert category.id is not None
    assert category.name == "show"
    assert category.description == "Eventos musicais"
    assert category.created_at is not None


async def test_category_name_unique_constraint(session: AsyncSession) -> None:
    """Inserting two categories with the same name must raise integrity error."""
    from sqlalchemy.exc import IntegrityError

    category1 = Category(name="festival", description="A")
    category2 = Category(name="festival", description="B")
    session.add(category1)
    await session.commit()

    session.add(category2)
    with pytest.raises(IntegrityError):
        await session.commit()


def test_category_table_name() -> None:
    """Categories table must be named 'categories'."""
    assert Category.__tablename__ == "categories"
