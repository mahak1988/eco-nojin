# Root Migration — Week 2 Cleanup

## Archived (17 orphan skeleton files)
`apps/api/`: router.py, repository.py, service.py, schemas.py, schemas_file.py
`apps/shared_core/`: router.py, repository.py, service.py, dependencies.py, token_store.py, schemas.py, crud.py, security_init.py, security_config.py, security_extended.py, models.py

## Celery
`apps/shared_ai/celery_app.py` → merged into `apps/shared_core/celery_app.py`
`docker-compose.prod.yml` → celery path fixed

## Root docs → docs/
Reports: `PHASE*.md`, `SECURITY_AUDIT*.md`, `TECHNICAL_REPORT*.md`, `ECONOJIN_*.md` → `docs/`
Keep: README.md, CHANGELOG.md, License, .gitignore, Dockerfile, docker-compose*.yml
