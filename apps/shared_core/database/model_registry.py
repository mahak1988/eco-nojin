"""Central ORM model registration for metadata / Alembic / init_db (R11 support)."""

from __future__ import annotations

import logging
from typing import Iterable

logger = logging.getLogger(__name__)

# Expand this list as modules mature; import failures are non-fatal in local.
MODEL_MODULES: tuple[str, ...] = (
    "apps.users.models",
    "apps.api.models.education",
    "apps.api.models.accounting",
    "apps.api.models.community",
    "apps.api.models.agriculture_school",
    "apps.ai_agents.models",
    "apps.simulation.models",
    "apps.admin_panel.models",
)


def import_all_models(modules: Iterable[str] | None = None) -> list[str]:
    """Import model modules so tables register on Base.metadata. Returns loaded names."""
    loaded: list[str] = []
    for name in modules or MODEL_MODULES:
        try:
            __import__(name, fromlist=["*"])
            loaded.append(name)
        except Exception as e:
            logger.debug("model_registry skip %s: %s", name, e)
    return loaded
