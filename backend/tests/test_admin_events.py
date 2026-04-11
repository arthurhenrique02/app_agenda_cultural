"""Tests for admin events endpoints (US-027 to US-032)."""

from datetime import date, time

import app.database as db_module
from app.models.category import Category
from app.models.event import Event, EventStatus
from app.models.user import User, UserRole
from app.security.jwt import create_access_token


def _auth_header_for(user_id: int) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(str(user_id))}"}


async def _seed_users_category() -> tuple[User, User, Category]:
    async with db_module.AsyncSessionLocal() as session:
        admin = User(
            name="Admin",
            email="admin_events@example.com",
            hashed_password="pw",
            role=UserRole.admin,
        )
        regular = User(
            name="Regular",
            email="regular_events@example.com",
            hashed_password="pw",
            role=UserRole.user,
        )
        category = Category(name="show", description="Shows")
        session.add_all([admin, regular, category])
        await session.commit()
        await session.refresh(admin)
        await session.refresh(regular)
        await session.refresh(category)
        return admin, regular, category


async def _seed_event(
    *,
    creator_id: int,
    category_id: int,
    title: str,
    status: EventStatus,
) -> Event:
    async with db_module.AsyncSessionLocal() as session:
        event = Event(
            title=title,
            description="Descricao",
            date=date(2030, 1, 1),
            start_time=time(18, 0),
            end_time=time(20, 0),
            venue_name="Local",
            address="Rua X, 1",
            neighborhood="Centro",
            city="Sao Paulo",
            category_id=category_id,
            created_by=creator_id,
            status=status,
        )
        session.add(event)
        await session.commit()
        await session.refresh(event)
        return event


class TestAdminAccessControl:
    async def test_non_admin_receives_403(self, async_client_with_tables):
        admin, regular, category = await _seed_users_category()
        event = await _seed_event(
            creator_id=regular.id,
            category_id=category.id,
            title="Pendente",
            status=EventStatus.pendente,
        )

        endpoints = [
            ("get", "/api/admin/events/pending", None),
            ("get", "/api/admin/events", None),
            ("patch", f"/api/admin/events/{event.id}/approve", None),
            (
                "patch",
                f"/api/admin/events/{event.id}/reject",
                {"reason": "Nao atende"},
            ),
            ("put", f"/api/admin/events/{event.id}", {"title": "Novo"}),
            ("delete", f"/api/admin/events/{event.id}", None),
        ]

        for method, url, payload in endpoints:
            request = getattr(async_client_with_tables, method)
            kwargs = {"headers": _auth_header_for(regular.id)}
            if payload is not None:
                kwargs["json"] = payload
            response = await request(url, **kwargs)
            assert response.status_code == 403


class TestAdminEventsEndpoints:
    async def test_pending_endpoint_is_paginated_and_only_pending(
        self, async_client_with_tables
    ):
        admin, regular, category = await _seed_users_category()
        await _seed_event(
            creator_id=regular.id,
            category_id=category.id,
            title="Pendente 1",
            status=EventStatus.pendente,
        )
        await _seed_event(
            creator_id=regular.id,
            category_id=category.id,
            title="Aprovado 1",
            status=EventStatus.aprovado,
        )

        response = await async_client_with_tables.get(
            "/api/admin/events/pending?page=1&per_page=10",
            headers=_auth_header_for(admin.id),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "pendente"

    async def test_approve_sets_status_and_review_metadata(
        self, async_client_with_tables
    ):
        admin, regular, category = await _seed_users_category()
        event = await _seed_event(
            creator_id=regular.id,
            category_id=category.id,
            title="Pendente",
            status=EventStatus.pendente,
        )

        response = await async_client_with_tables.patch(
            f"/api/admin/events/{event.id}/approve",
            headers=_auth_header_for(admin.id),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "aprovado"
        assert data["reviewed_by"] == admin.id
        assert data["reviewed_at"] is not None

    async def test_reject_requires_reason(self, async_client_with_tables):
        admin, regular, category = await _seed_users_category()
        event = await _seed_event(
            creator_id=regular.id,
            category_id=category.id,
            title="Pendente",
            status=EventStatus.pendente,
        )

        response = await async_client_with_tables.patch(
            f"/api/admin/events/{event.id}/reject",
            headers=_auth_header_for(admin.id),
            json={},
        )

        assert response.status_code == 422

    async def test_reject_sets_status_reason_and_review_metadata(
        self, async_client_with_tables
    ):
        admin, regular, category = await _seed_users_category()
        event = await _seed_event(
            creator_id=regular.id,
            category_id=category.id,
            title="Pendente",
            status=EventStatus.pendente,
        )

        response = await async_client_with_tables.patch(
            f"/api/admin/events/{event.id}/reject",
            headers=_auth_header_for(admin.id),
            json={"reason": "Informacoes insuficientes"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejeitado"
        assert data["rejection_reason"] == "Informacoes insuficientes"
        assert data["reviewed_by"] == admin.id
        assert data["reviewed_at"] is not None

    async def test_admin_all_events_supports_status_filter(
        self, async_client_with_tables
    ):
        admin, regular, category = await _seed_users_category()
        await _seed_event(
            creator_id=regular.id,
            category_id=category.id,
            title="Pendente",
            status=EventStatus.pendente,
        )
        await _seed_event(
            creator_id=regular.id,
            category_id=category.id,
            title="Aprovado",
            status=EventStatus.aprovado,
        )

        response = await async_client_with_tables.get(
            "/api/admin/events?status=aprovado&page=1&per_page=10",
            headers=_auth_header_for(admin.id),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Aprovado"

    async def test_admin_update_and_delete_any_event(self, async_client_with_tables):
        admin, regular, category = await _seed_users_category()
        event = await _seed_event(
            creator_id=regular.id,
            category_id=category.id,
            title="Original",
            status=EventStatus.pendente,
        )

        updated = await async_client_with_tables.put(
            f"/api/admin/events/{event.id}",
            headers=_auth_header_for(admin.id),
            json={"title": "Atualizado pelo admin"},
        )
        assert updated.status_code == 200
        assert updated.json()["title"] == "Atualizado pelo admin"

        deleted = await async_client_with_tables.delete(
            f"/api/admin/events/{event.id}",
            headers=_auth_header_for(admin.id),
        )
        assert deleted.status_code == 204

        async with db_module.AsyncSessionLocal() as session:
            persisted = await session.get(Event, event.id)
            assert persisted is None
