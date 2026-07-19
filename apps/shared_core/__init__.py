"""
Eco Nojin - Shared Core Module
================================
Central module providing configuration, security, database, CRUD, and DI utilities
adapted from fastapi/full-stack-fastapi-template and fastapi-best-practices.

Usage:
    from apps.shared_core.config import settings
    from apps.shared_core.security import create_access_token, verify_password
    from apps.shared_core.deps import SessionDep, CurrentUser, get_current_user
    from apps.shared_core.crud import CRUDBase
"""

__version__ = "2.0.0"