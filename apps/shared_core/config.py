"""Central settings (Pydantic v2)."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import List, Literal, Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

_WEAK_SECRET_MARKERS = (
    "local-dev",
    "change-me",
    "changeme",
    "secret",
    "password",
    "123456",
    "econojin",
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    PROJECT_NAME: str = Field(default="Econojin Platform")
    VERSION: str = Field(default="2.0.0")
    ENVIRONMENT: Literal["local", "staging", "production"] = Field(default="local")
    API_V1_STR: str = Field(default="/api/v1")

    BACKEND_CORS_ORIGINS: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://localhost:8000"
    )

    @property
    def all_cors_origins(self) -> List[str]:
        return [o.strip() for o in self.BACKEND_CORS_ORIGINS.split(",") if o.strip()]

    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./apps/econojin.db")
    DB_ECHO: bool = Field(default=False)
    FORCE_POSTGRES: bool = Field(default=False)

    SECRET_KEY: str = Field(default="local-dev-only-change-me-use-secrets-token-urlsafe-48")
    JWT_SECRET_KEY: Optional[str] = Field(default=None)
    ALGORITHM: str = Field(default="HS256")
    JWT_PRIVATE_KEY_PATH: Optional[str] = Field(default=None)
    JWT_PUBLIC_KEY_PATH: Optional[str] = Field(default=None)
    JWT_PRIVATE_KEY: Optional[str] = Field(default=None)
    JWT_PUBLIC_KEY: Optional[str] = Field(default=None)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=14)
    JWT_COOKIE_NAME: str = Field(default="access_token")
    REFRESH_COOKIE_NAME: str = Field(default="refresh_token")
    COOKIE_SECURE: bool = Field(default=False)
    COOKIE_SAMESITE: str = Field(default="lax")

    REQUIRE_AUTH_FOR_WRITES: bool = Field(default=False)

    ENABLE_RATE_LIMIT: bool = Field(default=True)
    ENABLE_AUDIT_LOG: bool = Field(default=True)
    ENABLE_SPIDERGUARD: bool = Field(default=False)
    SPIDERGUARD_MAX_REQUESTS: int = Field(default=120)
    SPIDERGUARD_WINDOW_SECONDS: int = Field(default=60)
    AUTH_RATE_LIMIT_MAX: int = Field(default=10)
    AUTH_RATE_LIMIT_WINDOW_SECONDS: int = Field(default=60)

    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_BROKER_URL: Optional[str] = Field(default=None)

    GEE_SERVICE_ACCOUNT: Optional[str] = Field(default=None)
    GEE_CREDENTIALS_FILE: Optional[str] = Field(default=None)
    GEE_PROJECT_ID: Optional[str] = Field(default=None)
    COPERNICUS_USERNAME: Optional[str] = Field(default=None)
    COPERNICUS_PASSWORD: Optional[str] = Field(default=None)

    BLOCKCHAIN_RPC_URL: str = Field(default="https://rpc-amoy.polygon.technology/")
    BLOCKCHAIN_CHAIN_ID: int = Field(default=80002)
    ECOCONTRACT_ADDRESS: str = Field(default="0x0000000000000000000000000000000000000001")
    ORACLE_CONTRACT_ADDRESS: str = Field(default="0x0000000000000000000000000000000000000002")
    BACKEND_WALLET_PRIVATE_KEY: Optional[str] = Field(default=None)

    LLM_PROVIDER: Literal["groq", "openai", "gemini", "openrouter", "ollama", "fake"] = Field(
        default="fake"
    )
    LLM_API_KEY: Optional[str] = Field(default=None)
    LLM_MODEL: str = Field(default="llama3-8b-8192")
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434")

    OPEN_METEO_URL: str = Field(default="https://api.open-meteo.com/v1")
    FAO_API_KEY: Optional[str] = Field(default=None)
    OPENWEATHER_API_KEY: Optional[str] = Field(default=None)
    SENTRY_DSN: Optional[str] = Field(default=None)

    @property
    def jwt_secret(self) -> str:
        return self.JWT_SECRET_KEY or self.SECRET_KEY

    def _is_weak_secret(self, value: str) -> bool:
        v = (value or "").strip().lower()
        if len(v) < 32:
            return True
        return any(m in v for m in _WEAK_SECRET_MARKERS)

    @model_validator(mode="after")
    def validate_production_settings(self) -> Settings:
        if self.ENVIRONMENT == "production":
            if self._is_weak_secret(self.SECRET_KEY):
                raise ValueError(
                    "SECRET_KEY must be a strong random value (>=32 chars, not a dev placeholder) "
                    "when ENVIRONMENT=production. Generate: python -c \"import secrets; print(secrets.token_urlsafe(48))\""
                )
            if self.JWT_SECRET_KEY and self._is_weak_secret(self.JWT_SECRET_KEY):
                raise ValueError("JWT_SECRET_KEY is too weak for production")
            if self.ALGORITHM.upper().startswith("HS"):
                logger.warning("Production still on HS* — prefer RS256 with mounted keys")
            if self.REQUIRE_AUTH_FOR_WRITES is False:
                logger.warning("REQUIRE_AUTH_FOR_WRITES is False in production")
            if not self.ENABLE_RATE_LIMIT:
                logger.warning("ENABLE_RATE_LIMIT is False in production")
            if not self.COOKIE_SECURE:
                logger.warning("COOKIE_SECURE is False in production — set true behind HTTPS")
            if self.BACKEND_WALLET_PRIVATE_KEY:
                logger.info("BACKEND_WALLET_PRIVATE_KEY is set (ensure it comes from a secret store)")
        elif self.ENVIRONMENT == "staging":
            if self._is_weak_secret(self.SECRET_KEY):
                logger.warning("Staging uses a weak SECRET_KEY placeholder — rotate before shared demos")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
