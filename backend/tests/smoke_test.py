"""E2E Smoke Test for Agenda Cultural (US-050).

Simulates a full user journey:
1. Register/Login as regular user.
2. Create an event (initially pending).
3. Verify event is NOT in public listing yet.
4. Login as Admin.
5. Approve the event.
6. Verify event IS NOW in public listing.
7. Delete the event.
"""

import pytest
from httpx import AsyncClient
from datetime import date, time
import app.database as db_module
from app.models.user import User, UserRole
from app.models.category import Category
from app.security.password import hash_password

async def _get_admin_token(client: AsyncClient):
    async with db_module.AsyncSessionLocal() as session:
        hashed_pw = hash_password("adminpw")
        admin = User(name="Super Admin", email="superadmin@example.com", hashed_password=hashed_pw, role=UserRole.admin)
        session.add(admin)
        await session.commit()
    
    res = await client.post("/api/auth/login", json={"email": "superadmin@example.com", "password": "adminpw"})
    return res.json()["access_token"]

@pytest.mark.asyncio
async def test_full_user_journey_smoke_check(async_client_with_tables: AsyncClient):
    client = async_client_with_tables

    # 1. Setup Category
    async with db_module.AsyncSessionLocal() as session:
        cat = Category(name="Festival", description="Festivals")
        session.add(cat)
        await session.commit()
        await session.refresh(cat)
        cat_id = cat.id

    # 2. Register User
    reg_res = await client.post("/api/auth/register", json={
        "name": "Smoke User",
        "email": "smoke@example.com",
        "password": "smokepassword"
    })
    assert reg_res.status_code in (200, 201)
    
    # 3. Login User
    login_res = await client.post("/api/auth/login", json={
        "email": "smoke@example.com",
        "password": "smokepassword"
    })
    assert login_res.status_code == 200
    user_token = login_res.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # 4. Create Event
    event_data = {
        "title": "Smoke Event",
        "description": "This is a smoke test event",
        "date": "2026-12-31",
        "start_time": "20:00",
        "venue_name": "Smoke Venue",
        "address": "Smoke Road, 123",
        "neighborhood": "Techno",
        "city": "Cyber City",
        "category_id": cat_id
    }
    create_res = await client.post("/api/events", json=event_data, headers=user_headers)
    assert create_res.status_code in (200, 201)
    event_id = create_res.json()["id"]

    # 5. Verify NOT in public list
    public_res = await client.get("/api/events")
    assert not any(e["id"] == event_id for e in public_res.json()["items"])

    # 6. Admin Approval
    admin_token = await _get_admin_token(client)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    approve_res = await client.patch(f"/api/admin/events/{event_id}/approve", headers=admin_headers)
    assert approve_res.status_code == 200

    # 7. Verify NOW in public list
    public_res_after = await client.get("/api/events")
    assert any(e["id"] == event_id for e in public_res_after.json()["items"])

    # 8. User Deletes Event (Soft delete/Cancel)
    del_res = await client.delete(f"/api/events/{event_id}", headers=user_headers)
    assert del_res.status_code == 204

    # 9. Verify NOT in public list anymore
    public_res_final = await client.get("/api/events")
    assert not any(e["id"] == event_id for e in public_res_final.json()["items"])

    # 10. Smoke check for Rejection flow
    # Create another event
    res2 = await client.post("/api/events", json=event_data, headers=user_headers)
    event_id2 = res2.json()["id"]
    
    # Reject it
    reject_res = await client.patch(f"/api/admin/events/{event_id2}/reject", json={"reason": "Test rejection"}, headers=admin_headers)
    assert reject_res.status_code == 200
    assert reject_res.json()["status"] == "rejeitado"
    assert reject_res.json()["rejection_reason"] == "Test rejection"

    print("\n[SMOKE TEST] Success: Full user journey and rejection flow verified.")
