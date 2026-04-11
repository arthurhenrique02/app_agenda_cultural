from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "Agenda Cultural"
    debug: bool = False
    secret_key: str = "change-me-in-production"

    # Database
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/agenda_cultural"
    )

    # JWT
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Storage (SeaweedFS / S3-compatible)
    storage_endpoint: str = "http://localhost:8333"
    storage_access_key: str = "minioadmin"
    storage_secret_key: str = "minioadmin"
    storage_bucket: str = "agenda-cultural"

    # Admin seed
    admin_default_password: str = "admin123"


settings = Settings()
