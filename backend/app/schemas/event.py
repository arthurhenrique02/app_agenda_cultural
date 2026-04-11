"""Event-related Pydantic schemas."""

import datetime as dt

from pydantic import BaseModel, ConfigDict

from app.models.event import EventStatus


class EventCreateRequest(BaseModel):
    """Payload for creating an event as an authenticated user."""

    title: str
    description: str
    date: dt.date
    start_time: dt.time
    end_time: dt.time | None = None
    venue_name: str
    address: str
    neighborhood: str
    city: str
    category_id: int
    image_url: str | None = None


class EventUpdateRequest(BaseModel):
    """Payload for updating an owned event."""

    title: str | None = None
    description: str | None = None
    date: dt.date | None = None
    start_time: dt.time | None = None
    end_time: dt.time | None = None
    venue_name: str | None = None
    address: str | None = None
    neighborhood: str | None = None
    city: str | None = None
    category_id: int | None = None
    image_url: str | None = None


class EventResponse(BaseModel):
    """Public response representation of an event row."""

    id: int
    title: str
    description: str
    date: dt.date
    start_time: dt.time
    end_time: dt.time | None
    venue_name: str
    address: str
    neighborhood: str
    city: str
    image_url: str | None
    status: EventStatus
    rejection_reason: str | None
    category_id: int
    created_by: int
    reviewed_by: int | None
    reviewed_at: dt.datetime | None
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = ConfigDict(from_attributes=True)
