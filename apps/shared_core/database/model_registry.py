"""Import all ORM models so metadata is complete for create_all / Alembic."""

from __future__ import annotations

import logging
from typing import List

logger = logging.getLogger(__name__)

_MODEL_MODULES = [
    "apps.users.models",
    "apps.shared_core.rbac.models",
    "apps.api.models.education",
    "apps.api.models.accounting",
    "apps.api.models.community",
    "apps.api.models.games",
    "apps.api.models.ecocoin",
    "apps.farms.models",
]


def import_all_models() -> List[str]:
    loaded: List[str] = []
    for mod in _MODEL_MODULES:
        try:
            __import__(mod)
            loaded.append(mod)
        except Exception as e:
            logger.debug("model import skip %s: %s", mod, e)
    return loaded
