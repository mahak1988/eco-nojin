# shared_knowledge | ماژول shared_knowledge

Part of the **Eco Nojin** platform.

## Overview

This module provides shared_knowledge functionality for the Econojin platform.
It follows the standard layered architecture:

```
shared_knowledge/
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
| GET    | `/shared_knowledge`         | List with pagination |
| GET    | `/shared_knowledge/{id}`  | Get by ID            |
| POST   | `/shared_knowledge`         | Create               |
| PATCH  | `/shared_knowledge/{id}`  | Update               |
| DELETE | `/shared_knowledge/{id}`  | Delete               |

## Development

```bash
# Run tests
pytest apps/shared_knowledge/tests/ -v

# Run the dev server (from repo root)
uvicorn apps.main:app --reload
```

## Auto-scaffolded

This module was auto-scaffolded by `scripts/phase1_complete_apps.py`.
Adjust the templates to match your actual domain model.
