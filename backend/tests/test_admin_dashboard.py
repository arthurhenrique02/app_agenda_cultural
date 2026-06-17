"""Tests for admin dashboard stats endpoint (US-033)."""

from datetime import date, time

import app.database as db_module
from app.models.category import Category
from app.models.event import Event, EventStatus
from app.models.user import User, UserRole
from app.security.jwt import create_access_token


def _auth_header_for(user_id: int) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(str(user_id))}"}


async def _seed_dashboard_data() -> tuple[User, User]:
    """Seed users, category, and events with various statuses for dashboard tests."""
    async with db_module.AsyncSessionLocal() as session:
        admin = User(
            name="Admin",
            email="dashboard_admin@example.com",
            hashed_password="pw",
            role=UserRole.admin,
        )
        regular = User(
            name="Regular",
            email="dashboard_regular@example.com",
            hashed_password="pw",
            role=UserRole.user,
        )
        category = Category(name="show", description="Shows")
        session.add_all([admin, regular, category])
        await session.commit()
        await session.refresh(admin)
        await session.refresh(regular)
        await session.refresh(category)

        events = [
            Event(
                title="Pendente 1",
                description="Desc",
                date=date(2030, 1, 1),
                start_time=time(18, 0),
                venue_name="Local",
                address="Rua X",
                neighborhood="Centro",
                city="SP",
                category_id=category.id,
                created_by=regular.id,
                status=EventStatus.pendente,
            ),
            Event(
                title="Pendente 2",
                description="Desc",
                date=date(2030, 2, 1),
                start_time=time(19, 0),
                venue_name="Local",
                address="Rua Y",
                neighborhood="Centro",
                city="SP",
                category_id=category.id,
                created_by=regular.id,
                status=EventStatus.pendente,
            ),
            Event(
                title="Aprovado 1",
                description="Desc",
                date=date(2030, 3, 1),
                start_time=time(20, 0),
                venue_name="Local",
                address="Rua Z",
                neighborhood="Centro",
                city="SP",
                category_id=category.id,
                created_by=regular.id,
                status=EventStatus.aprovado,
            ),
            Event(
                title="Rejeitado 1",
                description="Desc",
                date=date(2030, 4, 1),
                start_time=time(21, 0),
                venue_name="Local",
                address="Rua W",
                neighborhood="Centro",
                city="SP",
                category_id=category.id,
                created_by=regular.id,
                status=EventStatus.rejeitado,
                rejection_reason="Motivo",
            ),
            Event(
                title="Cancelado 1",
                description="Desc",
                date=date(2030, 5, 1),
                start_time=time(22, 0),
                venue_name="Local",
                address="Rua V",
                neighborhood="Centro",
                city="SP",
                category_id=category.id,
                created_by=regular.id,
                status=EventStatus.cancelado,
            ),
        ]
        session.add_all(events)
        await session.commit()

        return admin, regular


class TestAdminDashboard:
    async def test_non_admin_receives_403(self, async_client_with_tables):
        admin, regular = await _seed_dashboard_data()

        response = await async_client_with_tables.get(
            "/api/admin/dashboard",
            headers=_auth_header_for(regular.id),
        )
        assert response.status_code == 403

    async def test_unauthenticated_receives_401(self, async_client_with_tables):
        response = await async_client_with_tables.get("/api/admin/dashboard")
        assert response.status_code == 401

    async def test_dashboard_returns_correct_counters(self, async_client_with_tables):
        admin, regular = await _seed_dashboard_data()

        response = await async_client_with_tables.get(
            "/api/admin/dashboard",
            headers=_auth_header_for(admin.id),
        )

        assert response.status_code == 200
        data = response.json()

        # Total events = 5
        assert data["total_events"] == 5
        # Breakdown by status
        assert data["pendente"] == 2
        assert data["aprovado"] == 1
        assert data["rejeitado"] == 1
        assert data["cancelado"] == 1
        # Total users = 2 (admin + regular)
        assert data["total_users"] == 2

    async def test_dashboard_empty_database(self, async_client_with_tables):
        """Dashboard with no events and only the admin user."""
        async with db_module.AsyncSessionLocal() as session:
            admin = User(
                name="Admin",
                email="solo_admin@example.com",
                hashed_password="pw",
                role=UserRole.admin,
            )
            session.add(admin)
            await session.commit()
            await session.refresh(admin)

        response = await async_client_with_tables.get(
            "/api/admin/dashboard",
            headers=_auth_header_for(admin.id),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_events"] == 0
        assert data["pendente"] == 0
        assert data["aprovado"] == 0
        assert data["rejeitado"] == 0
        assert data["cancelado"] == 0
        assert data["total_users"] == 1
