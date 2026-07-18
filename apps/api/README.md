# api | ماژول api

Part of the **Eco Nojin** platform.

## Overview

This package contains a generic backend API module scaffold.
It is designed to work with the main FastAPI application located in `apps/main.py`.

## Structure

```
api/
├── __init__.py        # package init
├── router.py          # FastAPI router for API endpoints
├── schemas.py         # Pydantic request/response models
├── service.py         # Business logic layer
├── repository.py      # Database access logic
├── models.py          # SQLAlchemy ORM models
├── dependencies.py    # FastAPI dependencies
└── tests/             # Pytest tests for the API module
```

## Running

From the repository root:

```bash
uvicorn apps.main:app --reload
```

The primary backend server is defined in `apps/main.py`, which loads application routers and shared services.

## Notes

- `apps/main.py` is the canonical FastAPI entrypoint for this workspace.
- This package provides a template for API CRUD behavior and can be extended by other modules.
