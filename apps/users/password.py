"""Password hashing — bcrypt native (avoids passlib + bcrypt 4.1+ break)."""

from __future__ import annotations

import bcrypt


def get_password_hash(password: str) -> str:
    # bcrypt limit 72 bytes
    raw = password.encode("utf-8")[:72]
    return bcrypt.hashpw(raw, bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        raw = plain_password.encode("utf-8")[:72]
        return bcrypt.checkpw(raw, hashed_password.encode("utf-8"))
    except Exception:
        return False
