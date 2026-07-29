# Alembic on local SQLite (create_all already ran)

Local `init_db()` uses `Base.metadata.create_all`, so tables exist before any
Alembic revision is recorded. Running `alembic upgrade head` then tries to
create `courses` again → `table already exists`.

## Recommended local path

```powershell
# Mark DB as fully migrated without re-running DDL
alembic stamp head

# Or only after mint migration is present:
alembic stamp 20260729_0002
```

Ensure `ecocoin_mint_events` exists (server restart runs create_all, or):

```powershell
python -c "from apps.shared_core.database.session import engine, Base; from apps.shared_core.database.model_registry import import_all_models; import_all_models(); import asyncio; async def m():
 async with engine.begin() as c: await c.run_sync(Base.metadata.create_all)
asyncio.run(m()); print('ok')"
```

## Fresh empty DB

```powershell
Remove-Item .\apps\econojin.db -ErrorAction SilentlyContinue
alembic upgrade head
```

Only works if all revisions are idempotent or the DB is empty.
