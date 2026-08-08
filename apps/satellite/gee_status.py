"""GEE readiness probe for ops."""

from __future__ import annotations

from typing import Any


def probe_gee() -> dict[str, Any]:
    try:
        import ee  # noqa: F401
    except ImportError:
        return {
            "installed": False,
            "initialized": False,
            "message": "pip install earthengine-api (see requirements-scientific.txt)",
        }

    from apps.satellite.providers.gee_provider import GEEProvider

    p = GEEProvider()
    ok = p.is_available
    return {
        "installed": True,
        "initialized": ok,
        "message": "ready"
        if ok
        else "set GEE_SERVICE_ACCOUNT + GEE_CREDENTIALS_FILE + register SA in EE",
    }
