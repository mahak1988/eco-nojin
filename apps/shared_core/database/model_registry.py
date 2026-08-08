"""Import all ORM models so metadata is complete for create_all / Alembic."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# Explicit list of every module that defines SQLAlchemy models.
# Keep this in sync when adding new domain packages.
_MODEL_MODULES = [
    # Core auth & RBAC
    "apps.users.models",
    "apps.shared_core.rbac.models",
    "apps.shared_core.models",
    # Domain
    "apps.farms.models",
    "apps.crops.models",
    "apps.planting.models",
    "apps.inventory.models",
    "apps.monitoring.models",
    "apps.economics.models",
    # Simulation family
    "apps.simulation.models",
    "apps.simulation.models_runs",
    "apps.simulation.models_swat",
    "apps.simulation.runs.models",
    "apps.simulation.scenario.models",
    # AI / knowledge / agents
    "apps.ai_agents.models",
    "apps.shared_ai.models",
    "apps.shared_ai.ai.rag.models",
    "apps.shared_knowledge.models",
    "apps.shared_knowledge.knowledge.models",
    "apps.shared_sim.models",
    # API / product modules
    "apps.api.models.education",
    "apps.api.models.accounting",
    "apps.api.models.community",
    "apps.api.models.games",
    "apps.api.models.ecocoin",
    "apps.api.models.library",
    "apps.api.models.agriculture_school",
    "apps.api.models.api",
]

# Public alias for Alembic env.py compatibility
MODEL_MODULES = _MODEL_MODULES


def import_all_models(module_list: list[str] | None = None) -> list[str]:
    """Import every model module so Base.metadata is fully populated.

    Returns the list of modules that imported successfully.
    Failures are logged at debug level and skipped (missing optional deps).
    """
    loaded: list[str] = []
    modules = module_list if module_list is not None else _MODEL_MODULES
    for mod in modules:
        try:
            __import__(mod)
            loaded.append(mod)
        except Exception as e:
            logger.debug("model import skip %s: %s", mod, e)
    return loaded
