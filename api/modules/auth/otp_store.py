import random
import time
from typing import Optional

_otp_cache: dict[str, tuple[str, float]] = {}


def generate_otp(phone: str, ttl_sec: int = 300) -> str:
    code = f"{random.randint(100000, 999999)}"
    _otp_cache[phone] = (code, time.time() + ttl_sec)
    return code


def verify_otp(phone: str, code: str) -> bool:
    entry = _otp_cache.get(phone)
    if not entry:
        return False
    stored, expires = entry
    if time.time() > expires:
        _otp_cache.pop(phone, None)
        return False
    if stored != code.strip():
        return False
    _otp_cache.pop(phone, None)
    return True


def peek_dev_code(phone: str) -> Optional[str]:
    entry = _otp_cache.get(phone)
    return entry[0] if entry else None
