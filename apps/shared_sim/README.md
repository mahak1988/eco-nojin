# shared_sim | ماژول shared_sim

Part of the **Eco Nojin** platform.

## Overview

This module provides shared_sim functionality for the Econojin platform.
It follows the standard layered architecture:

```
shared_sim/
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
| GET    | `/shared_sim`         | List with pagination |
| GET    | `/shared_sim/{id}`  | Get by ID            |
| POST   | `/shared_sim`         | Create               |
| PATCH  | `/shared_sim/{id}`  | Update               |
| DELETE | `/shared_sim/{id}`  | Delete               |

## Development

```bash
# Run tests
pytest apps/shared_sim/tests/ -v

# Run the dev server (from repo root)
uvicorn apps.main:app --reload
```

## Auto-scaffolded

This module was auto-scaffolded by `scripts/phase1_complete_apps.py`.
Adjust the templates to match your actual domain model.
