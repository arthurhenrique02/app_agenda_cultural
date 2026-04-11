"""Event repository — direct DB access for events."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event


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
