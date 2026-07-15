# api | ماژول api

Part of the **Eco Nojin** platform.

## Overview

This module provides api functionality for the Econojin platform.
It follows the standard layered architecture:

```
api/
├── __init__.py        # Module init
├── router.py          # FastAPI router (HTTP endpoints)
├── schemas.py         # Pydantic validation models
├── service.py         # Business logic
├── repository.py      # Database access (SQLAlchemy)
├── models.py          # ORM models
├── dependencies.py    # FastAPI dependencies (auth, etc.)
└── tests/             # Pytest tests
```

## Endpoints

| Method | Path                  | Description          |
|--------|-----------------------|----------------------|
| GET    | `/api`         | List with pagination |
| GET    | `/api/{id}`  | Get by ID            |
| POST   | `/api`         | Create               |
| PATCH  | `/api/{id}`  | Update               |
| DELETE | `/api/{id}`  | Delete               |

## Development

```bash
# Run tests
pytest apps/api/tests/ -v

# Run the dev server (from repo root)
uvicorn apps.main:app --reload
```

## Auto-scaffolded

This module was auto-scaffolded by `scripts/phase1_complete_apps.py`.
Adjust the templates to match your actual domain model.
