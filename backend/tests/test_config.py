import pytest

from app.config import Settings


def test_settings_defaults():
    s = Settings()
    assert s.app_name == "Agenda Cultural"
    assert s.access_token_expire_minutes == 15
    assert s.refresh_token_expire_days == 7
    assert s.storage_bucket == "agenda-cultural"


def test_settings_override_via_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SECRET_KEY", "super-secret")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

    s = Settings()
    assert s.secret_key == "super-secret"
    assert s.debug is True
    assert s.access_token_expire_minutes == 30


def test_settings_database_url_override(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@db:5432/mydb")

    s = Settings()
    assert s.database_url == "postgresql+asyncpg://user:pass@db:5432/mydb"
