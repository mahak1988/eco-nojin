# ai_agents | ماژول ai_agents

Part of the **Eco Nojin** platform.

## Overview

This module provides ai_agents functionality for the Econojin platform.
It follows the standard layered architecture:

```
ai_agents/
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
| GET    | `/ai_agents`         | List with pagination |
| GET    | `/ai_agents/{id}`  | Get by ID            |
| POST   | `/ai_agents`         | Create               |
| PATCH  | `/ai_agents/{id}`  | Update               |
| DELETE | `/ai_agents/{id}`  | Delete               |

## Development

```bash
# Run tests
pytest apps/ai_agents/tests/ -v

# Run the dev server (from repo root)
uvicorn apps.main:app --reload
```

## Auto-scaffolded

This module was auto-scaffolded by `scripts/phase1_complete_apps.py`.
Adjust the templates to match your actual domain model.
