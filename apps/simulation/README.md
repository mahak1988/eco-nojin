# simulation | ماژول simulation

Part of the **Eco Nojin** platform.

## Overview

This module provides simulation functionality for the Econojin platform.
It follows the standard layered architecture:

```
simulation/
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
| GET    | `/simulation`         | List with pagination |
| GET    | `/simulation/{id}`  | Get by ID            |
| POST   | `/simulation`         | Create               |
| PATCH  | `/simulation/{id}`  | Update               |
| DELETE | `/simulation/{id}`  | Delete               |

## Development

```bash
# Run tests
pytest apps/simulation/tests/ -v

# Run the dev server (from repo root)
uvicorn apps.main:app --reload
```

## Auto-scaffolded

This module was auto-scaffolded by `scripts/phase1_complete_apps.py`.
Adjust the templates to match your actual domain model.
