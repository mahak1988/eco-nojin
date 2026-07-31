
"""Spider Web Security - Central Configuration."""
from __future__ import annotations

import os


class SecurityConfig:
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
    PASSWORD_MIN_LENGTH = 8
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30
    RATE_LIMIT_API = 60
    RATE_LIMIT_LOGIN = 5
    RATE_LIMIT_AI_CHAT = 20
    ALLOWED_ORIGINS = [
        "https://econojin.com", "https://www.econojin.com",
        "http://localhost:5173", "http://localhost:3000",
    ]
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS = {".png",".jpg",".jpeg",".gif",".pdf",".csv",".json"}
    HSTS_MAX_AGE = 31536000
