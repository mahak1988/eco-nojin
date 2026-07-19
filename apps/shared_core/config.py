"""
Econojin - Central Configuration Module
========================================
Adapted from fastapi/full-stack-fastapi-template (official FastAPI template)
with Pydantic v2 Settings, validation, and environment-aware defaults.
"""

import os
import secrets
import warnings
from typing import Annotated, Any, Literal, Self

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    """Parse CORS origins from comma-separated string or list."""
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    """
    Centralized settings for Econojin platform.
    
    Loads from .env file at project root with Pydantic validation.
    All secrets must be changed from defaults in production.
    """

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_ignore_empty=True,
        extra="ignore",
    )

    # ── API Configuration ──────────────────────────────────────
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Econojin API"
    VERSION: str = "2.0.0"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    DEBUG: bool = False

    # ── Security ───────────────────────────────────────────────
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REQUIRE_AUTH_FOR_WRITES: bool = False

    # ── CORS ───────────────────────────────────────────────────
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []
    FRONTEND_HOST: str = "http://localhost:5173"

    @computed_field
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    # ── Database ───────────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./apps/econojin.db"
    POSTGRES_SERVER: str | None = None
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Return the appropriate database URI based on configuration."""
        if self.POSTGRES_SERVER:
            return str(PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB or "econojin",
            ))
        return self.DATABASE_URL

    # ── LLM / AI ───────────────────────────────────────────────
    LLM_PROVIDER: Literal["groq", "gemini", "openrouter", "ollama", "fake"] = "fake"
    GROQ_API_KEY: str | None = None
    GOOGLE_API_KEY: str | None = None
    OPENROUTER_API_KEY: str | None = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # ── SMS ────────────────────────────────────────────────────
    SMS_PROVIDER: Literal["kavenegar", "twilio", "mock"] = "mock"
    KAVENEGAR_API_KEY: str | None = None
    TWILIO_ACCOUNT_SID: str | None = None
    TWILIO_AUTH_TOKEN: str | None = None
    TWILIO_PHONE_NUMBER: str | None = None

    # ── Email ──────────────────────────────────────────────────
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str | None = None

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEST_USER: EmailStr = "test@example.com"

    @computed_field
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    # ── Superuser (for initial setup) ──────────────────────────
    FIRST_SUPERUSER: EmailStr = "admin@econojin.com"
    FIRST_SUPERUSER_PASSWORD: str = "changethis"

    # ── Monitoring ─────────────────────────────────────────────
    SENTRY_DSN: HttpUrl | None = None
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # ── Feature Flags ──────────────────────────────────────────
    ENABLE_OTP: bool = True
    ENABLE_SIMULATION: bool = True
    ENABLE_ECOCOIN: bool = True
    ENABLE_GIS: bool = True

    # ── Validation ─────────────────────────────────────────────
    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value and value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )
        return self


# Singleton instance
settings = Settings()  # type: ignore[call-arg]