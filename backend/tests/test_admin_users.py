"""Tests for admin users list and promote endpoints (US-034)."""

import app.database as db_module
from app.models.user import User, UserRole
from app.security.jwt import create_access_token


def _auth_header_for(user_id: int) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(str(user_id))}"}


async def _seed_users() -> tuple[User, User, User]:
    """Seed an admin and two regular users for tests."""
    async with db_module.AsyncSessionLocal() as session:
        admin = User(
            name="Admin",
            email="admin_users@example.com",
            hashed_password="pw",
            role=UserRole.admin,
        )
        user1 = User(
            name="User One",
            email="user1@example.com",
            hashed_password="pw",
            role=UserRole.user,
        )
        user2 = User(
            name="User Two",
            email="user2@example.com",
            hashed_password="pw",
            role=UserRole.user,
        )
        session.add_all([admin, user1, user2])
        await session.commit()
        await session.refresh(admin)
        await session.refresh(user1)
        await session.refresh(user2)
        return admin, user1, user2


class TestAdminUsersList:
    async def test_unauthenticated_receives_401(self, async_client_with_tables):
        response = await async_client_with_tables.get("/api/admin/users")
        assert response.status_code == 401

    async def test_non_admin_receives_403(self, async_client_with_tables):
        _, user1, _ = await _seed_users()
        response = await async_client_with_tables.get(
            "/api/admin/users",
            headers=_auth_header_for(user1.id),
        )
        assert response.status_code == 403

    async def test_admin_lists_all_users(self, async_client_with_tables):
        admin, user1, user2 = await _seed_users()
        response = await async_client_with_tables.get(
            "/api/admin/users",
            headers=_auth_header_for(admin.id),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3
        assert "page" in data
        assert "per_page" in data
        assert "pages" in data

    async def test_users_list_is_paginated(self, async_client_with_tables):
        admin, _, _ = await _seed_users()
        response = await async_client_with_tables.get(
            "/api/admin/users?page=1&per_page=2",
            headers=_auth_header_for(admin.id),
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 3
        assert data["pages"] == 2

    async def test_users_response_excludes_password(self, async_client_with_tables):
        admin, _, _ = await _seed_users()
        response = await async_client_with_tables.get(
            "/api/admin/users",
            headers=_auth_header_for(admin.id),
        )
        data = response.json()
        for item in data["items"]:
            assert "hashed_password" not in item


class TestAdminPromoteUser:
    async def test_unauthenticated_receives_401(self, async_client_with_tables):
        response = await async_client_with_tables.patch("/api/admin/users/1/promote")
        assert response.status_code == 401

    async def test_non_admin_receives_403(self, async_client_with_tables):
        _, user1, _ = await _seed_users()
        response = await async_client_with_tables.patch(
            f"/api/admin/users/{user1.id}/promote",
            headers=_auth_header_for(user1.id),
        )
        assert response.status_code == 403

    async def test_promote_user_to_admin(self, async_client_with_tables):
        admin, user1, _ = await _seed_users()
        response = await async_client_with_tables.patch(
            f"/api/admin/users/{user1.id}/promote",
            headers=_auth_header_for(admin.id),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "admin"
        assert data["id"] == user1.id

    async def test_promote_nonexistent_user_returns_404(self, async_client_with_tables):
        admin, _, _ = await _seed_users()
        response = await async_client_with_tables.patch(
            "/api/admin/users/9999/promote",
            headers=_auth_header_for(admin.id),
        )
        assert response.status_code == 404

    async def test_promote_already_admin_is_idempotent(self, async_client_with_tables):
        admin, _, _ = await _seed_users()
        response = await async_client_with_tables.patch(
            f"/api/admin/users/{admin.id}/promote",
            headers=_auth_header_for(admin.id),
        )
        assert response.status_code == 200
        assert response.json()["role"] == "admin"
