"""Central settings (Pydantic v2)."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import List, Literal, Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


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

    @property
    def jwt_secret(self) -> str:
        return self.JWT_SECRET_KEY or self.SECRET_KEY

    @model_validator(mode="after")
    def validate_production_settings(self) -> Settings:
        if self.ENVIRONMENT == "production":
            if len(self.SECRET_KEY) < 32 or self.SECRET_KEY.startswith("local-dev"):
                raise ValueError("SECRET_KEY must be a strong random value in production")
            if self.ALGORITHM.upper().startswith("HS"):
                logger.warning("Production still on HS* — prefer RS256 with mounted keys")
            if self.REQUIRE_AUTH_FOR_WRITES is False:
                logger.warning("REQUIRE_AUTH_FOR_WRITES is False in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
