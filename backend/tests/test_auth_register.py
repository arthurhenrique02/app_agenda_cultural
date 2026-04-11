"""Tests for POST /api/auth/register endpoint (US-008)."""


class TestRegisterEndpoint:
    """Tests for POST /api/auth/register."""

    async def test_register_creates_user_and_returns_201(
        self, async_client_with_tables
    ):
        """POST /api/auth/register with valid data returns 201 and user info."""
        response = await async_client_with_tables.post(
            "/api/auth/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "securepassword123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "john@example.com"
        assert data["name"] == "John Doe"
        assert data["is_active"] is True
        assert data["role"] == "user"
        assert "id" in data
        assert "created_at" in data

    async def test_register_does_not_expose_password_hash(
        self, async_client_with_tables
    ):
        """Response must not contain hashed_password field."""
        response = await async_client_with_tables.post(
            "/api/auth/register",
            json={
                "name": "Jane Doe",
                "email": "jane@example.com",
                "password": "somepassword",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "hashed_password" not in data
        assert "password" not in data

    async def test_register_duplicate_email_returns_400(self, async_client_with_tables):
        """Duplicate email returns a 400 (or 409) validation error."""
        payload = {
            "name": "Alice",
            "email": "alice@example.com",
            "password": "password123",
        }
        first = await async_client_with_tables.post("/api/auth/register", json=payload)
        assert first.status_code == 201

        second = await async_client_with_tables.post("/api/auth/register", json=payload)
        assert second.status_code in (400, 409)

    async def test_register_missing_email_returns_422(self, async_client_with_tables):
        """Missing required field returns 422 Unprocessable Entity."""
        response = await async_client_with_tables.post(
            "/api/auth/register",
            json={"name": "Bob", "password": "password123"},
        )
        assert response.status_code == 422

    async def test_register_missing_password_returns_422(
        self, async_client_with_tables
    ):
        """Missing password field returns 422."""
        response = await async_client_with_tables.post(
            "/api/auth/register",
            json={"name": "Bob", "email": "bob@example.com"},
        )
        assert response.status_code == 422

    async def test_register_user_is_active_by_default(self, async_client_with_tables):
        """Newly registered user must be active."""
        response = await async_client_with_tables.post(
            "/api/auth/register",
            json={
                "name": "Carol",
                "email": "carol@example.com",
                "password": "mypassword",
            },
        )
        assert response.status_code == 201
        assert response.json()["is_active"] is True

    async def test_register_user_role_is_user(self, async_client_with_tables):
        """Newly registered user must have role 'user'."""
        response = await async_client_with_tables.post(
            "/api/auth/register",
            json={
                "name": "Dave",
                "email": "dave@example.com",
                "password": "mypassword",
            },
        )
        assert response.status_code == 201
        assert response.json()["role"] == "user"
