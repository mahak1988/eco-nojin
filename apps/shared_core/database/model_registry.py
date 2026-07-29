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
    "apps.crops.models",
    "apps.planting.models",
    "apps.inventory.models",
    "apps.monitoring.models",
    "apps.simulation.models_runs",
]

# Public alias for Alembic env.py compatibility
MODEL_MODULES = _MODEL_MODULES


def import_all_models(module_list=None) -> List[str]:
    loaded: List[str] = []
    modules = module_list if module_list is not None else _MODEL_MODULES
    for mod in modules:
        try:
            __import__(mod)
            loaded.append(mod)
        except Exception as e:
            logger.debug("model import skip %s: %s", mod, e)
    return loaded
