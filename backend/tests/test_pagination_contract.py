"""Contract tests for pagination metadata (US-049)."""

import pytest
from httpx import AsyncClient

from app.models.category import Category
from app.models.event import Event, EventStatus
from app.models.user import User, UserRole
from datetime import date, time
from app.security.password import hash_password
import app.database as db_module

async def _seed_data():
    async with db_module.AsyncSessionLocal() as session:
        # Create admin
        hashed_pw = hash_password("pw")
        admin = User(name="Admin", email="admin@example.com", hashed_password=hashed_pw, role=UserRole.admin)
        # Create user
        user = User(name="User", email="user@example.com", hashed_password=hashed_pw, role=UserRole.user)
        # Create categories
        cat = Category(name="show", description="Shows")
        session.add_all([admin, user, cat])
        await session.commit()
        await session.refresh(admin)
        await session.refresh(user)
        await session.refresh(cat)

        # Create some events
        for i in range(5):
            e = Event(
                title=f"Event {i}",
                description="Desc",
                date=date(2026, 5, 21),
                start_time=time(19, 0),
                venue_name="Local",
                address="Rua X",
                neighborhood="Centro",
                city="SP",
                category_id=cat.id,
                created_by=user.id,
                status=EventStatus.aprovado if i % 2 == 0 else EventStatus.pendente
            )
            session.add(e)
        await session.commit()
        return admin, user, cat

@pytest.mark.asyncio
async def test_public_events_pagination_contract(async_client_with_tables: AsyncClient):
    await _seed_data()
    res = await async_client_with_tables.get("/api/events")
    assert res.status_code == 200
    data = res.json()
    for field in ["items", "total", "page", "per_page", "pages"]:
        assert field in data, f"Missing {field} in public events response"
    assert isinstance(data["items"], list)

@pytest.mark.asyncio
async def test_search_events_pagination_contract(async_client_with_tables: AsyncClient):
    await _seed_data()
    res = await async_client_with_tables.get("/api/events/search?q=Event")
    assert res.status_code == 200
    data = res.json()
    for field in ["items", "total", "page", "per_page", "pages"]:
        assert field in data, f"Missing {field} in search events response"

@pytest.mark.asyncio
async def test_admin_events_pagination_contract(async_client_with_tables: AsyncClient):
    admin, _, _ = await _seed_data()
    # Login as admin (simulate auth by using fixture that would handle it or manual token)
    # Actually our fixtures use get_current_user override, but here we need a token or mock
    # For simplicity, let's assume we can use a helper to get token
    login_res = await async_client_with_tables.post("/api/auth/login", json={
        "email": "admin@example.com",
        "password": "pw"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = await async_client_with_tables.get("/api/admin/events", headers=headers)
    assert res.status_code == 200
    data = res.json()
    for field in ["items", "total", "page", "per_page", "pages"]:
        assert field in data, f"Missing {field} in admin events response"

@pytest.mark.asyncio
async def test_admin_pending_events_pagination_contract(async_client_with_tables: AsyncClient):
    await _seed_data()
    login_res = await async_client_with_tables.post("/api/auth/login", json={
        "email": "admin@example.com",
        "password": "pw"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = await async_client_with_tables.get("/api/admin/events/pending", headers=headers)
    assert res.status_code == 200
    data = res.json()
    for field in ["items", "total", "page", "per_page", "pages"]:
        assert field in data, f"Missing {field} in admin pending events response"

@pytest.mark.asyncio
async def test_admin_users_pagination_contract(async_client_with_tables: AsyncClient):
    await _seed_data()
    login_res = await async_client_with_tables.post("/api/auth/login", json={
        "email": "admin@example.com",
        "password": "pw"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = await async_client_with_tables.get("/api/admin/users", headers=headers)
    assert res.status_code == 200
    data = res.json()
    for field in ["items", "total", "page", "per_page", "pages"]:
        assert field in data, f"Missing {field} in admin users response"

@pytest.mark.asyncio
async def test_user_my_events_pagination_contract(async_client_with_tables: AsyncClient):
    # This test is expected to FAIL currently as /api/events/me returns list[EventResponse]
    await _seed_data()
    login_res = await async_client_with_tables.post("/api/auth/login", json={
        "email": "user@example.com",
        "password": "pw"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = await async_client_with_tables.get("/api/events/me", headers=headers)
    assert res.status_code == 200
    data = res.json()
    
    # Check if it follows the pagination contract
    fields = ["items", "total", "page", "per_page", "pages"]
    missing = [f for f in fields if f not in data]
    assert not missing, f"User 'my events' endpoint missing pagination fields: {missing}"
