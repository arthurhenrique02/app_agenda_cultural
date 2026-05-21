"""Event service — business logic for user event CRUD."""

import datetime as dt

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.event import Event, EventStatus
from app.models.user import User
from app.repositories import event as event_repo
from app.schemas.event import EventResponse, PublicEventResponse


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


async def list_my_events(
    session: AsyncSession,
    current_user: User,
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """Return events created by the authenticated user with pagination."""
    events, total, pages = await event_repo.list_events_by_creator_paginated(
        session, current_user.id, page, per_page
    )
    return {
        "items": [EventResponse.model_validate(e) for e in events],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages,
    }


def _public_status(event: Event) -> str:
    """Return display status for public endpoints."""
    if event.status == EventStatus.aprovado and event.date < dt.date.today():
        return "encerrado"
    return event.status.value


def _to_public_event_response(event: Event) -> PublicEventResponse:
    """Serialize Event to the public response model."""
    return PublicEventResponse(
        id=event.id,
        title=event.title,
        description=event.description,
        date=event.date,
        start_time=event.start_time,
        end_time=event.end_time,
        venue_name=event.venue_name,
        address=event.address,
        neighborhood=event.neighborhood,
        city=event.city,
        image_url=event.image_url,
        status=_public_status(event),
        rejection_reason=event.rejection_reason,
        category_id=event.category_id,
        created_by=event.created_by,
        reviewed_by=event.reviewed_by,
        reviewed_at=event.reviewed_at,
        created_at=event.created_at,
        updated_at=event.updated_at,
    )


async def list_public_events(
    session: AsyncSession,
    *,
    page: int,
    per_page: int,
    category_id: int | None,
    date_from: dt.date | None,
    date_to: dt.date | None,
    neighborhood: str | None,
) -> dict:
    """List approved events with public filters and pagination contract."""
    events, total, pages = await event_repo.list_approved_events_paginated(
        session,
        page=page,
        per_page=per_page,
        category_id=category_id,
        date_from=date_from,
        date_to=date_to,
        neighborhood=neighborhood,
    )
    return {
        "items": [_to_public_event_response(event) for event in events],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages,
    }


async def get_public_event(
    session: AsyncSession,
    *,
    event_id: int,
) -> PublicEventResponse:
    """Return a single approved event visible to public users."""
    event = await event_repo.get_event_by_id(session, event_id)
    if event is None or event.status != EventStatus.aprovado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found.",
        )
    return _to_public_event_response(event)


async def search_public_events(
    session: AsyncSession,
    *,
    q: str,
    category_id: int | None,
    page: int,
    per_page: int,
) -> dict:
    """Search approved events by title/description with pagination contract."""
    events, total, pages = await event_repo.search_approved_events_paginated(
        session,
        q=q,
        category_id=category_id,
        page=page,
        per_page=per_page,
    )
    return {
        "items": [_to_public_event_response(event) for event in events],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages,
    }


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
