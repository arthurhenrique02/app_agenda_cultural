"""Tests for public events endpoints (US-022 to US-026)."""

from datetime import date, time

import app.database as db_module
from app.models.category import Category
from app.models.event import Event, EventStatus
from app.models.user import User


async def _seed_base_data() -> tuple[User, Category, Category]:
    async with db_module.AsyncSessionLocal() as session:
        user = User(name="Creator", email="creator@example.com", hashed_password="pw")
        c1 = Category(name="show", description="Shows")
        c2 = Category(name="festival", description="Festivals")
        session.add_all([user, c1, c2])
        await session.commit()
        await session.refresh(user)
        await session.refresh(c1)
        await session.refresh(c2)
        return user, c1, c2


async def _seed_event(
    *,
    creator_id: int,
    category_id: int,
    title: str,
    description: str,
    date_value: date,
    neighborhood: str,
    status: EventStatus,
) -> Event:
    async with db_module.AsyncSessionLocal() as session:
        event = Event(
            title=title,
            description=description,
            date=date_value,
            start_time=time(18, 0),
            end_time=time(20, 0),
            venue_name="Local",
            address="Rua X, 1",
            neighborhood=neighborhood,
            city="Sao Paulo",
            category_id=category_id,
            created_by=creator_id,
            status=status,
        )
        session.add(event)
        await session.commit()
        await session.refresh(event)
        return event


class TestPublicEventsList:
    async def test_list_returns_only_approved_with_pagination_metadata(
        self, async_client_with_tables
    ):
        user, c1, _ = await _seed_base_data()
        await _seed_event(
            creator_id=user.id,
            category_id=c1.id,
            title="Evento aprovado",
            description="Descricao",
            date_value=date(2030, 1, 1),
            neighborhood="Centro",
            status=EventStatus.aprovado,
        )
        await _seed_event(
            creator_id=user.id,
            category_id=c1.id,
            title="Evento pendente",
            description="Descricao",
            date_value=date(2030, 1, 2),
            neighborhood="Centro",
            status=EventStatus.pendente,
        )

        response = await async_client_with_tables.get("/api/events?page=1&per_page=20")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["page"] == 1
        assert data["per_page"] == 20
        assert data["pages"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Evento aprovado"

    async def test_list_supports_category_date_and_neighborhood_filters(
        self, async_client_with_tables
    ):
        user, c1, c2 = await _seed_base_data()
        await _seed_event(
            creator_id=user.id,
            category_id=c1.id,
            title="Jazz Centro",
            description="Noite de jazz",
            date_value=date(2030, 5, 10),
            neighborhood="Centro",
            status=EventStatus.aprovado,
        )
        await _seed_event(
            creator_id=user.id,
            category_id=c2.id,
            title="Rock Norte",
            description="Show de rock",
            date_value=date(2030, 5, 20),
            neighborhood="Zona Norte",
            status=EventStatus.aprovado,
        )

        response = await async_client_with_tables.get(
            f"/api/events?category_id={c1.id}&date_from=2030-05-01&"
            "date_to=2030-05-15&neighborhood=centro"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Jazz Centro"

    async def test_past_approved_events_are_marked_as_encerrado(
        self, async_client_with_tables
    ):
        user, c1, _ = await _seed_base_data()
        await _seed_event(
            creator_id=user.id,
            category_id=c1.id,
            title="Evento passado",
            description="Descricao",
            date_value=date(2020, 1, 1),
            neighborhood="Centro",
            status=EventStatus.aprovado,
        )
        await _seed_event(
            creator_id=user.id,
            category_id=c1.id,
            title="Evento futuro",
            description="Descricao",
            date_value=date(2035, 1, 1),
            neighborhood="Centro",
            status=EventStatus.aprovado,
        )

        response = await async_client_with_tables.get("/api/events")

        assert response.status_code == 200
        by_title = {item["title"]: item for item in response.json()["items"]}
        assert by_title["Evento passado"]["status"] == "encerrado"
        assert by_title["Evento futuro"]["status"] == "aprovado"


class TestPublicEventDetailAndSearch:
    async def test_event_detail_returns_approved_event(self, async_client_with_tables):
        user, c1, _ = await _seed_base_data()
        event = await _seed_event(
            creator_id=user.id,
            category_id=c1.id,
            title="Detalhe publico",
            description="Descricao completa",
            date_value=date(2030, 7, 1),
            neighborhood="Centro",
            status=EventStatus.aprovado,
        )

        response = await async_client_with_tables.get(f"/api/events/{event.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == event.id
        assert data["title"] == "Detalhe publico"

    async def test_event_detail_hides_non_public_event(self, async_client_with_tables):
        user, c1, _ = await _seed_base_data()
        event = await _seed_event(
            creator_id=user.id,
            category_id=c1.id,
            title="Nao publico",
            description="Descricao",
            date_value=date(2030, 7, 1),
            neighborhood="Centro",
            status=EventStatus.pendente,
        )

        response = await async_client_with_tables.get(f"/api/events/{event.id}")

        assert response.status_code == 404

    async def test_event_detail_nonexistent_returns_404(self, async_client_with_tables):
        response = await async_client_with_tables.get("/api/events/9999")

        assert response.status_code == 404

    async def test_search_requires_q_and_searches_title_and_description(
        self, async_client_with_tables
    ):
        user, c1, _ = await _seed_base_data()
        await _seed_event(
            creator_id=user.id,
            category_id=c1.id,
            title="Jazz Night",
            description="Musica ao vivo",
            date_value=date(2030, 8, 1),
            neighborhood="Centro",
            status=EventStatus.aprovado,
        )
        await _seed_event(
            creator_id=user.id,
            category_id=c1.id,
            title="Classica",
            description="Concerto de jazz sinfonico",
            date_value=date(2030, 8, 2),
            neighborhood="Centro",
            status=EventStatus.aprovado,
        )

        too_short = await async_client_with_tables.get("/api/events/search?q=a")
        assert too_short.status_code == 422

        response = await async_client_with_tables.get(
            "/api/events/search?q=jazz&page=1&per_page=10"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["page"] == 1
        assert data["per_page"] == 10
        assert data["pages"] == 1
