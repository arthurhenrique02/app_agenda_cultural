"""Event repository — direct DB access for events."""

import datetime as dt

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event, EventStatus


async def create_event(session: AsyncSession, event: Event) -> Event:
    """Persist a new event and return it."""
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


async def get_event_by_id(session: AsyncSession, event_id: int) -> Event | None:
    """Return an event by id, or None if not found."""
    result = await session.execute(select(Event).where(Event.id == event_id))
    return result.scalar_one_or_none()


async def list_events_by_creator(session: AsyncSession, creator_id: int) -> list[Event]:
    """Return events submitted by a specific user."""
    result = await session.execute(
        select(Event)
        .where(Event.created_by == creator_id)
        .order_by(Event.created_at.desc())
    )
    return list(result.scalars().all())


async def save_event(session: AsyncSession, event: Event) -> Event:
    """Commit and refresh a modified event instance."""
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


def _compute_pages(total: int, per_page: int) -> int:
    if total == 0:
        return 0
    return (total + per_page - 1) // per_page


async def list_approved_events_paginated(
    session: AsyncSession,
    *,
    page: int,
    per_page: int,
    category_id: int | None,
    date_from: dt.date | None,
    date_to: dt.date | None,
    neighborhood: str | None,
) -> tuple[list[Event], int, int]:
    """Return approved events with optional public filters and pagination."""
    stmt = select(Event).where(Event.status == EventStatus.aprovado)

    if category_id is not None:
        stmt = stmt.where(Event.category_id == category_id)
    if date_from is not None:
        stmt = stmt.where(Event.date >= date_from)
    if date_to is not None:
        stmt = stmt.where(Event.date <= date_to)
    if neighborhood is not None:
        stmt = stmt.where(Event.neighborhood.ilike(f"%{neighborhood}%"))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = int((await session.execute(count_stmt)).scalar_one())
    pages = _compute_pages(total, per_page)

    result = await session.execute(
        stmt.order_by(Event.date.asc(), Event.start_time.asc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    return list(result.scalars().all()), total, pages


async def search_approved_events_paginated(
    session: AsyncSession,
    *,
    q: str,
    category_id: int | None,
    page: int,
    per_page: int,
) -> tuple[list[Event], int, int]:
    """Search approved events by title/description with pagination."""
    stmt = select(Event).where(
        Event.status == EventStatus.aprovado,
        or_(
            Event.title.ilike(f"%{q}%"),
            Event.description.ilike(f"%{q}%"),
        ),
    )

    if category_id is not None:
        stmt = stmt.where(Event.category_id == category_id)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = int((await session.execute(count_stmt)).scalar_one())
    pages = _compute_pages(total, per_page)

    result = await session.execute(
        stmt.order_by(Event.date.asc(), Event.start_time.asc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    return list(result.scalars().all()), total, pages


async def list_admin_events_paginated(
    session: AsyncSession,
    *,
    status_filter: EventStatus | None,
    page: int,
    per_page: int,
) -> tuple[list[Event], int, int]:
    """Return all events for admin views with optional status filter."""
    stmt = select(Event)
    if status_filter is not None:
        stmt = stmt.where(Event.status == status_filter)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = int((await session.execute(count_stmt)).scalar_one())
    pages = _compute_pages(total, per_page)

    result = await session.execute(
        stmt.order_by(Event.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    return list(result.scalars().all()), total, pages


async def delete_event(session: AsyncSession, event: Event) -> None:
    """Permanently delete an event row."""
    await session.delete(event)
    await session.commit()
