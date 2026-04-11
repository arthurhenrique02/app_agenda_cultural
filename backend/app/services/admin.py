"""Admin service — moderation and full event management logic."""

import datetime as dt

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.event import EventStatus
from app.models.user import User
from app.repositories import event as event_repo
from app.repositories import user as user_repo
from app.schemas.event import DashboardResponse


async def get_dashboard_stats(session: AsyncSession) -> DashboardResponse:
    """Compute dashboard counters for admin overview."""
    counts = await event_repo.count_events_by_status(session)
    total_users = await user_repo.count_users(session)
    return DashboardResponse(
        total_events=counts.get("total", 0),
        pendente=counts.get(EventStatus.pendente, 0),
        aprovado=counts.get(EventStatus.aprovado, 0),
        rejeitado=counts.get(EventStatus.rejeitado, 0),
        cancelado=counts.get(EventStatus.cancelado, 0),
        total_users=total_users,
    )


async def list_pending_events(
    session: AsyncSession,
    *,
    page: int,
    per_page: int,
) -> dict:
    """Return pending events with pagination metadata."""
    events, total, pages = await event_repo.list_admin_events_paginated(
        session,
        status_filter=EventStatus.pendente,
        page=page,
        per_page=per_page,
    )
    return {
        "items": events,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages,
    }


async def approve_event(
    session: AsyncSession,
    *,
    event_id: int,
    admin_user: User,
):
    """Approve an event and register moderation metadata."""
    event = await event_repo.get_event_by_id(session, event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found.",
        )

    event.status = EventStatus.aprovado
    event.rejection_reason = None
    event.reviewed_by = admin_user.id
    event.reviewed_at = dt.datetime.now(dt.UTC)
    return await event_repo.save_event(session, event)


async def reject_event(
    session: AsyncSession,
    *,
    event_id: int,
    reason: str,
    admin_user: User,
):
    """Reject an event with mandatory reason and moderation metadata."""
    event = await event_repo.get_event_by_id(session, event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found.",
        )

    event.status = EventStatus.rejeitado
    event.rejection_reason = reason
    event.reviewed_by = admin_user.id
    event.reviewed_at = dt.datetime.now(dt.UTC)
    return await event_repo.save_event(session, event)


async def list_all_events(
    session: AsyncSession,
    *,
    status_filter: EventStatus | None,
    page: int,
    per_page: int,
) -> dict:
    """Return all events with optional status filter and pagination metadata."""
    events, total, pages = await event_repo.list_admin_events_paginated(
        session,
        status_filter=status_filter,
        page=page,
        per_page=per_page,
    )
    return {
        "items": events,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages,
    }


async def update_event(
    session: AsyncSession,
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
):
    """Update any event record as admin."""
    event = await event_repo.get_event_by_id(session, event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found.",
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

    return await event_repo.save_event(session, event)


async def delete_event(session: AsyncSession, *, event_id: int) -> None:
    """Delete any event record as admin."""
    event = await event_repo.get_event_by_id(session, event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found.",
        )
    await event_repo.delete_event(session, event)
