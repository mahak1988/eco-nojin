# shared_ai | ماژول shared_ai

Part of the **Eco Nojin** platform.

## Overview

This module provides shared_ai functionality for the Econojin platform.
It follows the standard layered architecture:

```
shared_ai/
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
| GET    | `/shared_ai`         | List with pagination |
| GET    | `/shared_ai/{id}`  | Get by ID            |
| POST   | `/shared_ai`         | Create               |
| PATCH  | `/shared_ai/{id}`  | Update               |
| DELETE | `/shared_ai/{id}`  | Delete               |

## Development

```bash
# Run tests
pytest apps/shared_ai/tests/ -v

# Run the dev server (from repo root)
uvicorn apps.main:app --reload
```

## Auto-scaffolded

This module was auto-scaffolded by `scripts/phase1_complete_apps.py`.
Adjust the templates to match your actual domain model.
