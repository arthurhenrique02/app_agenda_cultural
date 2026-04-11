"""Admin router — /api/admin event management endpoints."""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import require_admin
from app.dependencies.database import get_db
from app.models.event import EventStatus
from app.models.user import User
from app.schemas.event import (
    EventResponse,
    EventUpdateRequest,
    PaginatedEventsResponse,
    RejectEventRequest,
)
from app.services import admin as admin_service

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/events/pending", response_model=PaginatedEventsResponse)
async def get_pending_events(
    page: int = 1,
    per_page: int = 20,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> PaginatedEventsResponse:
    """List pending events for moderation."""
    payload = await admin_service.list_pending_events(
        session,
        page=page,
        per_page=per_page,
    )
    return PaginatedEventsResponse(
        items=[EventResponse.model_validate(event) for event in payload["items"]],
        total=payload["total"],
        page=payload["page"],
        per_page=payload["per_page"],
        pages=payload["pages"],
    )


@router.patch("/events/{event_id}/approve", response_model=EventResponse)
async def approve_event(
    event_id: int,
    admin_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> EventResponse:
    """Approve a pending event."""
    event = await admin_service.approve_event(
        session,
        event_id=event_id,
        admin_user=admin_user,
    )
    return EventResponse.model_validate(event)


@router.patch("/events/{event_id}/reject", response_model=EventResponse)
async def reject_event(
    event_id: int,
    body: RejectEventRequest,
    admin_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> EventResponse:
    """Reject a pending event with reason."""
    event = await admin_service.reject_event(
        session,
        event_id=event_id,
        reason=body.reason,
        admin_user=admin_user,
    )
    return EventResponse.model_validate(event)


@router.get("/events", response_model=PaginatedEventsResponse)
async def get_all_events(
    status: EventStatus | None = None,
    page: int = 1,
    per_page: int = 20,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> PaginatedEventsResponse:
    """List all events with optional status filter."""
    payload = await admin_service.list_all_events(
        session,
        status_filter=status,
        page=page,
        per_page=per_page,
    )
    return PaginatedEventsResponse(
        items=[EventResponse.model_validate(event) for event in payload["items"]],
        total=payload["total"],
        page=payload["page"],
        per_page=payload["per_page"],
        pages=payload["pages"],
    )


@router.put("/events/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    body: EventUpdateRequest,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> EventResponse:
    """Update any event as admin."""
    event = await admin_service.update_event(
        session,
        event_id=event_id,
        title=body.title,
        description=body.description,
        date=body.date,
        start_time=body.start_time,
        end_time=body.end_time,
        venue_name=body.venue_name,
        address=body.address,
        neighborhood=body.neighborhood,
        city=body.city,
        category_id=body.category_id,
        image_url=body.image_url,
    )
    return EventResponse.model_validate(event)


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Response:
    """Delete any event as admin."""
    await admin_service.delete_event(session, event_id=event_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
