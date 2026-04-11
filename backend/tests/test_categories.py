"""Tests for GET /api/categories endpoint (US-015)."""

import app.database as db_module
from app.models.category import Category


class TestCategoriesEndpoint:
    """Tests for public category listing endpoint."""

    async def test_get_categories_returns_public_list(self, async_client_with_tables):
        """GET /api/categories returns category list without authentication."""
        async with db_module.AsyncSessionLocal() as session:
            session.add(Category(name="show", description="Shows musicais"))
            session.add(Category(name="festival", description="Festivais locais"))
            await session.commit()

        response = await async_client_with_tables.get("/api/categories")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["name"] == "festival"
        assert data[1]["name"] == "show"
        assert "id" in data[0]
        assert "description" in data[0]
        assert "created_at" in data[0]

    async def test_get_categories_returns_empty_list_when_no_data(
        self, async_client_with_tables
    ):
        """GET /api/categories returns an empty list when no categories exist."""
        response = await async_client_with_tables.get("/api/categories")

        assert response.status_code == 200
        assert response.json() == []
