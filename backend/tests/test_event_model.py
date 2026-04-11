"""Tests for the Event model - US-016."""

from datetime import UTC, date, datetime, time

import pytest
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.category import Category
from app.models.event import Event, EventStatus
from app.models.user import User

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


async def _create_user_and_category(session: AsyncSession) -> tuple[User, Category]:
    user = User(
        name="Event Owner",
        email="owner@example.com",
        hashed_password="hashed_pw",
    )
    category = Category(name="show", description="Eventos musicais")
    session.add(user)
    session.add(category)
    await session.commit()
    await session.refresh(user)
    await session.refresh(category)
    return user, category


def test_event_status_enum_values() -> None:
    """EventStatus enum must expose all lifecycle values."""
    assert EventStatus.pendente.value == "pendente"
    assert EventStatus.aprovado.value == "aprovado"
    assert EventStatus.rejeitado.value == "rejeitado"
    assert EventStatus.cancelado.value == "cancelado"


def test_event_model_has_required_fields() -> None:
    """Event model must declare all required columns."""
    mapper = inspect(Event)
    columns = {c.key for c in mapper.columns}
    required = {
        "id",
        "title",
        "description",
        "date",
        "start_time",
        "end_time",
        "venue_name",
        "address",
        "neighborhood",
        "city",
        "image_url",
        "status",
        "rejection_reason",
        "category_id",
        "created_by",
        "reviewed_by",
        "reviewed_at",
        "created_at",
        "updated_at",
    }
    assert required.issubset(columns), f"Missing columns: {required - columns}"


def test_event_table_name() -> None:
    """Events table must be named 'events'."""
    assert Event.__tablename__ == "events"


def test_event_model_has_required_indexes() -> None:
    """Event model must index status/date/category_id/created_by columns."""
    indexed_columns = {
        tuple(index.columns.keys())
        for index in Event.__table__.indexes
    }

    assert ("status",) in indexed_columns
    assert ("date",) in indexed_columns
    assert ("category_id",) in indexed_columns
    assert ("created_by",) in indexed_columns


async def test_event_can_be_created_with_pending_default(session: AsyncSession) -> None:
    """New events are persisted with default status 'pendente'."""
    user, category = await _create_user_and_category(session)

    event = Event(
        title="Show no Parque",
        description="Apresentacao ao ar livre",
        date=date(2026, 5, 20),
        start_time=time(18, 0),
        end_time=time(20, 0),
        venue_name="Parque Central",
        address="Rua A, 100",
        neighborhood="Centro",
        city="Sao Paulo",
        category_id=category.id,
        created_by=user.id,
    )
    session.add(event)
    await session.commit()
    await session.refresh(event)

    assert event.id is not None
    assert event.status == EventStatus.pendente
    assert event.rejection_reason is None
    assert event.reviewed_by is None
    assert event.reviewed_at is None
    assert event.created_at is not None
    assert event.updated_at is not None


async def test_event_can_store_review_metadata(session: AsyncSession) -> None:
    """Reviewed event stores reviewer and review timestamp fields."""
    creator, category = await _create_user_and_category(session)

    reviewer = User(
        name="Admin Reviewer",
        email="reviewer@example.com",
        hashed_password="hashed_pw",
    )
    session.add(reviewer)
    await session.commit()
    await session.refresh(reviewer)

    event = Event(
        title="Exposicao de Arte",
        description="Mostra coletiva",
        date=date(2026, 6, 10),
        start_time=time(14, 0),
        venue_name="Galeria X",
        address="Rua B, 42",
        neighborhood="Vila Nova",
        city="Sao Paulo",
        status=EventStatus.aprovado,
        category_id=category.id,
        created_by=creator.id,
        reviewed_by=reviewer.id,
        reviewed_at=datetime.now(UTC),
    )
    session.add(event)
    await session.commit()
    await session.refresh(event)

    assert event.status == EventStatus.aprovado
    assert event.reviewed_by == reviewer.id
    assert event.reviewed_at is not None
