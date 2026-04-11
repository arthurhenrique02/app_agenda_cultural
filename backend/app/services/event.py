"""Event service — business logic for user event CRUD."""

import datetime as dt

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.event import Event, EventStatus
from app.models.user import User
from app.repositories import event as event_repo


async def create_user_event(
    session: AsyncSession,
    current_user: User,
    *,
    title: str,
    description: str,
    date: dt.date,
    start_time: dt.time,
    end_time: dt.time | None,
    venue_name: str,
    address: str,
    neighborhood: str,
    city: str,
    category_id: int,
    image_url: str | None,
) -> Event:
    """Create a new event linked to the authenticated user."""
    category = await session.get(Category, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid category_id.",
        )

    event = Event(
        title=title,
        description=description,
        date=date,
        start_time=start_time,
        end_time=end_time,
        venue_name=venue_name,
        address=address,
        neighborhood=neighborhood,
        city=city,
        category_id=category_id,
        image_url=image_url,
        status=EventStatus.pendente,
        created_by=current_user.id,
        reviewed_by=None,
        reviewed_at=None,
        rejection_reason=None,
    )
    return await event_repo.create_event(session, event)


async def list_my_events(session: AsyncSession, current_user: User) -> list[Event]:
    """Return events created by the authenticated user."""
    return await event_repo.list_events_by_creator(session, current_user.id)


async def _get_owned_event_or_raise(
    session: AsyncSession,
    *,
    event_id: int,
    current_user: User,
) -> Event:
    """Load event and enforce owner-only access at service layer."""
    event = await event_repo.get_event_by_id(session, event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found.",
        )

    if event.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions.",
        )

    return event


async def update_my_event(
    session: AsyncSession,
    current_user: User,
    *,
    event_id: int,
    title: str | None,
    description: str | None,
    date: dt.date | None,
    start_time: dt.time | None,
    end_time: dt.time | None,
    venue_name: str | None,
    address: str | None,
    neighborhood: str | None,
    city: str | None,
    category_id: int | None,
    image_url: str | None,
) -> Event:
    """Update an event owned by the authenticated user."""
    event = await _get_owned_event_or_raise(
        session,
        event_id=event_id,
        current_user=current_user,
    )

    if category_id is not None:
        category = await session.get(Category, category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid category_id.",
            )

    if title is not None:
        event.title = title
    if description is not None:
        event.description = description
    if date is not None:
        event.date = date
    if start_time is not None:
        event.start_time = start_time
    if end_time is not None:
        event.end_time = end_time
    if venue_name is not None:
        event.venue_name = venue_name
    if address is not None:
        event.address = address
    if neighborhood is not None:
        event.neighborhood = neighborhood
    if city is not None:
        event.city = city
    if category_id is not None:
        event.category_id = category_id
    if image_url is not None:
        event.image_url = image_url

    # Business rule: editing an approved event sends it back to moderation.
    if event.status == EventStatus.aprovado:
        event.status = EventStatus.pendente
        event.reviewed_by = None
        event.reviewed_at = None

    return await event_repo.save_event(session, event)


async def delete_my_event(
    session: AsyncSession,
    current_user: User,
    *,
    event_id: int,
) -> None:
    """Cancel (soft-delete) an event owned by the authenticated user."""
    event = await _get_owned_event_or_raise(
        session,
        event_id=event_id,
        current_user=current_user,
    )
    event.status = EventStatus.cancelado
    await event_repo.save_event(session, event)
