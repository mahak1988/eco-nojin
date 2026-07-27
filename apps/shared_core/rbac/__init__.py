"""RBAC package (F0.3)."""

from apps.shared_core.rbac.deps import require_permission
from apps.shared_core.rbac.seed import seed_rbac

__all__ = ["require_permission", "seed_rbac"]
