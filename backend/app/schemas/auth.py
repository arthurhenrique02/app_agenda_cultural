"""Auth-related Pydantic schemas."""

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    """Payload for POST /api/auth/register."""

    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """Payload for POST /api/auth/login."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response for successful authentication."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Payload for POST /api/auth/refresh."""

    refresh_token: str


class AccessTokenResponse(BaseModel):
    """Response for token refresh — contains only the new access token."""

    access_token: str
    token_type: str = "bearer"
