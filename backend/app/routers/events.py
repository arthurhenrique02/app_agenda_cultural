"""Events router — /api/events endpoints for authenticated user CRUD."""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.event import EventCreateRequest, EventResponse, EventUpdateRequest
from app.services import event as event_service

router = APIRouter(prefix="/api/events", tags=["events"])


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    body: EventCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> EventResponse:
    """Create a new event owned by the authenticated user."""
    event = await event_service.create_user_event(
        session,
        current_user,
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


@router.get("/me", response_model=list[EventResponse])
async def get_my_events(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[EventResponse]:
    """Return events created by the authenticated user."""
    events = await event_service.list_my_events(session, current_user)
    return [EventResponse.model_validate(event) for event in events]


@router.put("/{event_id}", response_model=EventResponse)
async def update_my_event(
    event_id: int,
    body: EventUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> EventResponse:
    """Update an event owned by the authenticated user."""
    event = await event_service.update_my_event(
        session,
        current_user,
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


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Response:
    """Cancel (soft-delete) an event owned by the authenticated user."""
    await event_service.delete_my_event(
        session,
        current_user,
        event_id=event_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
