"""
User Module Configuration
=========================
JWT and authentication settings with proper secret management.
All secrets are loaded from .env via shared_core.config.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import Literal
import warnings


class UserModuleSettings(BaseSettings):
    """User module-specific settings with security validation."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    
    # JWT Configuration
    JWT_ALGORITHM: Literal["HS256", "RS256"] = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Password Policy
    PASSWORD_MIN_LENGTH: int = 8
    
    @model_validator(mode="after")
    def _validate_production_secrets(self):
        """Warn about weak algorithms in production."""
        if self.JWT_ALGORITHM == "HS256":
            warnings.warn(
                "HS256 is not recommended for production. "
                "Use RS256 with proper key rotation.",
                stacklevel=1,
            )
        return self


# Singleton instance
user_settings = UserModuleSettings()