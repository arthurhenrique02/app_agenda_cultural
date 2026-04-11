"""Tests for authenticated user event CRUD endpoints (US-017 to US-021)."""

from datetime import UTC, date, datetime, time

import app.database as db_module
from app.models.category import Category
from app.models.event import Event, EventStatus
from app.models.user import User
from app.security.jwt import create_access_token


def _auth_header_for(user_id: int) -> dict[str, str]:
    token = create_access_token(str(user_id))
    return {"Authorization": f"Bearer {token}"}


async def _seed_user_and_category(
    *,
    email: str = "owner@example.com",
    name: str = "Owner",
) -> tuple[User, Category]:
    async with db_module.AsyncSessionLocal() as session:
        user = User(name=name, email=email, hashed_password="hashed_pw")
        category = Category(name="show", description="Eventos musicais")
        session.add(user)
        session.add(category)
        await session.commit()
        await session.refresh(user)
        await session.refresh(category)
        return user, category


async def _seed_user(*, email: str, name: str) -> User:
    async with db_module.AsyncSessionLocal() as session:
        user = User(name=name, email=email, hashed_password="hashed_pw")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def _seed_event(
    *,
    creator_id: int,
    category_id: int,
    title: str = "Evento Teste",
    status: EventStatus = EventStatus.pendente,
    reviewed_by: int | None = None,
    reviewed_at: datetime | None = None,
    rejection_reason: str | None = None,
) -> Event:
    async with db_module.AsyncSessionLocal() as session:
        event = Event(
            title=title,
            description="Descricao do evento",
            date=date(2026, 6, 1),
            start_time=time(19, 0),
            end_time=time(21, 0),
            venue_name="Teatro Municipal",
            address="Rua Central, 123",
            neighborhood="Centro",
            city="Sao Paulo",
            category_id=category_id,
            created_by=creator_id,
            status=status,
            reviewed_by=reviewed_by,
            reviewed_at=reviewed_at,
            rejection_reason=rejection_reason,
        )
        session.add(event)
        await session.commit()
        await session.refresh(event)
        return event


class TestCreateEvent:
    async def test_create_event_requires_authentication(self, async_client_with_tables):
        payload = {
            "title": "Show de Jazz",
            "description": "Noite de jazz",
            "date": "2026-07-15",
            "start_time": "20:00:00",
            "end_time": "22:00:00",
            "venue_name": "Casa da Musica",
            "address": "Rua A, 100",
            "neighborhood": "Centro",
            "city": "Sao Paulo",
            "category_id": 1,
        }

        response = await async_client_with_tables.post("/api/events", json=payload)

        assert response.status_code == 401

    async def test_create_event_sets_pending_and_creator(
        self, async_client_with_tables
    ):
        user, category = await _seed_user_and_category()
        payload = {
            "title": "Show de Jazz",
            "description": "Noite de jazz",
            "date": "2026-07-15",
            "start_time": "20:00:00",
            "end_time": "22:00:00",
            "venue_name": "Casa da Musica",
            "address": "Rua A, 100",
            "neighborhood": "Centro",
            "city": "Sao Paulo",
            "category_id": category.id,
        }

        response = await async_client_with_tables.post(
            "/api/events",
            json=payload,
            headers=_auth_header_for(user.id),
        )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "pendente"
        assert data["created_by"] == user.id
        assert data["category_id"] == category.id


class TestMyEvents:
    async def test_get_my_events_requires_authentication(
        self, async_client_with_tables
    ):
        response = await async_client_with_tables.get("/api/events/me")

        assert response.status_code == 401

    async def test_get_my_events_returns_only_current_user_events(
        self, async_client_with_tables
    ):
        owner, category = await _seed_user_and_category()
        other_user = await _seed_user(email="other@example.com", name="Other")

        await _seed_event(
            creator_id=owner.id,
            category_id=category.id,
            title="Meu evento 1",
            status=EventStatus.rejeitado,
            rejection_reason="Faltam detalhes",
        )
        await _seed_event(
            creator_id=owner.id,
            category_id=category.id,
            title="Meu evento 2",
            status=EventStatus.pendente,
        )
        await _seed_event(
            creator_id=other_user.id,
            category_id=category.id,
            title="Evento de outro usuario",
            status=EventStatus.pendente,
        )

        response = await async_client_with_tables.get(
            "/api/events/me",
            headers=_auth_header_for(owner.id),
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert {item["title"] for item in data} == {"Meu evento 1", "Meu evento 2"}
        assert all(item["created_by"] == owner.id for item in data)

        rejected_item = next(item for item in data if item["title"] == "Meu evento 1")
        assert rejected_item["status"] == "rejeitado"
        assert rejected_item["rejection_reason"] == "Faltam detalhes"


class TestUpdateEvent:
    async def test_non_owner_cannot_update_event(self, async_client_with_tables):
        owner, category = await _seed_user_and_category()
        intruder = await _seed_user(email="intruder@example.com", name="Intruder")
        event = await _seed_event(creator_id=owner.id, category_id=category.id)

        response = await async_client_with_tables.put(
            f"/api/events/{event.id}",
            json={"title": "Titulo alterado"},
            headers=_auth_header_for(intruder.id),
        )

        assert response.status_code == 403

    async def test_owner_update_approved_event_resets_review_metadata(
        self, async_client_with_tables
    ):
        owner, category = await _seed_user_and_category()
        reviewer = await _seed_user(email="admin@example.com", name="Admin")
        event = await _seed_event(
            creator_id=owner.id,
            category_id=category.id,
            status=EventStatus.aprovado,
            reviewed_by=reviewer.id,
            reviewed_at=datetime.now(UTC),
        )

        response = await async_client_with_tables.put(
            f"/api/events/{event.id}",
            json={"title": "Evento atualizado"},
            headers=_auth_header_for(owner.id),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Evento atualizado"
        assert data["status"] == "pendente"
        assert data["reviewed_by"] is None
        assert data["reviewed_at"] is None


class TestDeleteEvent:
    async def test_non_owner_cannot_delete_event(self, async_client_with_tables):
        owner, category = await _seed_user_and_category()
        intruder = await _seed_user(email="intruder@example.com", name="Intruder")
        event = await _seed_event(creator_id=owner.id, category_id=category.id)

        response = await async_client_with_tables.delete(
            f"/api/events/{event.id}",
            headers=_auth_header_for(intruder.id),
        )

        assert response.status_code == 403

    async def test_owner_delete_marks_event_as_cancelado(
        self, async_client_with_tables
    ):
        owner, category = await _seed_user_and_category()
        event = await _seed_event(creator_id=owner.id, category_id=category.id)

        response = await async_client_with_tables.delete(
            f"/api/events/{event.id}",
            headers=_auth_header_for(owner.id),
        )

        assert response.status_code == 204

        async with db_module.AsyncSessionLocal() as session:
            persisted = await session.get(Event, event.id)
            assert persisted is not None
            assert persisted.status == EventStatus.cancelado
