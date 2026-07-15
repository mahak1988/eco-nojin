# shared_core | ماژول shared_core

Part of the **Eco Nojin** platform.

## Overview

This module provides shared_core functionality for the Econojin platform.
It follows the standard layered architecture:

```
shared_core/
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
| GET    | `/shared_core`         | List with pagination |
| GET    | `/shared_core/{id}`  | Get by ID            |
| POST   | `/shared_core`         | Create               |
| PATCH  | `/shared_core/{id}`  | Update               |
| DELETE | `/shared_core/{id}`  | Delete               |

## Development

```bash
# Run tests
pytest apps/shared_core/tests/ -v

# Run the dev server (from repo root)
uvicorn apps.main:app --reload
```

## Auto-scaffolded

This module was auto-scaffolded by `scripts/phase1_complete_apps.py`.
Adjust the templates to match your actual domain model.
