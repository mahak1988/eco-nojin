# Infrastructure Upgrade Documentation

**Project:** Econojin Platform (econojin.com)
**Date:** 2026-08-03
**Type:** DevOps & Backend Infrastructure Upgrade

---

## Overview

This document catalogs all infrastructure changes made to upgrade the Econojin platform from a SQLite-based development setup to a production-ready PostgreSQL + PostGIS architecture with improved Docker, Celery, logging, and security configurations.

---

## 1. Database: SQLite → PostgreSQL 16 + PostGIS

### 1.1 PostgreSQL Docker Compose

**File:** `docker/docker-compose.postgres.yml`

Standalone Docker Compose for local PostgreSQL development:

- **PostgreSQL 16 + PostGIS 3.4** (`postgis/postgis:16-3.4`)
  - Database: `econojin`
  - User: `econojin`
  - Password: via `POSTGRES_PASSWORD` env (default: `econojin_dev`)
  - Port: `5432` (configurable via `POSTGRES_PORT`)
  - Volume: `econojin_postgres_data`
  - Healthcheck: `pg_isready`

- **pgAdmin 4** (`dpage/pgadmin4:8`)
  - Port: `5050` (configurable via `PGADMIN_PORT`)
  - Email/Password: via env vars
  - Volume: `econojin_pgadmin_data`

**Usage:**
```bash
docker compose -f docker/docker-compose.postgres.yml up -d
```

### 1.2 Initial Database Schema

**File:** `docker/init-db.sql`

Executed automatically on first PostgreSQL container start. Creates:

| Extension | Purpose |
|-----------|---------|
| `postgis` | Geospatial support |
| `uuid-ossp` | UUID generation |
| `btree_gin` | GIN index support |
| `pg_trgm` | Trigram text search |
| `pg_stat_statements` | Query monitoring |

**Tables created:**
- `users` — Authentication and profile
- `refresh_tokens` — JWT refresh tokens
- `farms` — With `geography(Point, 4326)` spatial column
- `crops` — Crop management
- `weather_records` — Weather data
- `simulation_runs` — ML simulation history
- `audit_logs` — Security audit trail
- `rate_limit_entries` — Rate limiting storage
- `celery_taskmeta` — Celery task tracking

**Features:**
- Automatic geometry population via `update_farm_geom()` trigger
- `updated_at` triggers on `users`, `farms`, `crops`
- Spatial indexes (GIST on `farms.geom`)
- Composite indexes on common query patterns

### 1.3 Database Session (`session.py`)

**File:** `apps/shared_core/database/session.py`

**Changes:**
- **PostgreSQL connection pool tuning** via env vars:
  - `DB_POOL_SIZE` (default: 20)
  - `DB_MAX_OVERFLOW` (default: 40)
  - `DB_POOL_TIMEOUT` (default: 30s)
  - `DB_POOL_RECYCLE` (default: 3600s / 1 hour)
- PostgreSQL `connect_args` with `application_name` and `timezone`
- Added `autoflush=False` to session maker
- Added `is_postgres()` utility function
- `init_db()` skips `create_all` in production/staging (use Alembic)
- Better fallback chain: Postgres → SQLite with clear logging

### 1.4 Configuration (`config.py`)

**File:** `apps/shared_core/config.py`

**New fields:**
| Field | Default | Description |
|-------|---------|-------------|
| `DB_POOL_SIZE` | 20 | PostgreSQL pool size |
| `DB_MAX_OVERFLOW` | 40 | Max overflow connections |
| `DB_POOL_TIMEOUT` | 30 | Connection wait timeout |
| `DB_POOL_RECYCLE` | 3600 | Connection recycle (seconds) |
| `CELERY_RESULT_BACKEND` | None | Celery result backend URL |
| `LOG_LEVEL` | INFO | Logging level |
| `LOG_FORMAT` | json | `json` or `text` |
| `LOG_FILE` | None | Log file path |

**New properties:**
- `is_postgres` — Returns `True` if DATABASE_URL uses PostgreSQL
- `celery_broker` — Resolved broker URL
- `celery_backend` — Resolved backend URL

**Validation enhancements:**
- Production now warns if not using PostgreSQL
- Staging warns if not using PostgreSQL

---

## 2. Docker Improvements

### 2.1 Production Docker Compose

**File:** `docker-compose.prod.yml` (overwritten)

Full production stack:

| Service | Image | Purpose |
|---------|-------|---------|
| `postgres` | `postgis/postgis:16-3.4` | Database |
| `redis` | `redis:7-alpine` | Cache + Message Broker |
| `api` | Built from `docker/Dockerfile.backend` | FastAPI backend |
| `celery-worker` | Built from `docker/Dockerfile.backend` | Async task worker |
| `celery-beat` | Built from `docker/Dockerfile.backend` | Periodic scheduler |
| `nginx` | `nginx:1.25-alpine` | Reverse proxy |
| `prometheus` | `prom/prometheus:v2.47` | Metrics collection |
| `grafana` | `grafana/grafana:10.2` | Dashboards |
| `pgadmin` | `dpage/pgadmin4:8` | DB management (profile: management) |

**Features:**
- All services have `healthcheck` blocks
- YAML anchors for shared logging and healthcheck configs
- Resource limits on all services
- Redis with password auth and `allkeys-lru` eviction
- API with `--workers 4`, `--proxy-headers`, `--limit-concurrency 200`
- Celery worker with `--max-tasks-per-child=100`
- `ulimits: nofile 65536` on API service
- Isolated `backend` bridge network with fixed subnet
- `127.0.0.1` binding on database ports (no external exposure)

### 2.2 Production Dockerfile

**File:** `docker/Dockerfile.backend` (new)

Multi-stage build:
- **Stage 1 (builder):** Compiles Python wheels for fast rebuilds
- **Stage 2 (runtime):** Minimal image with only runtime deps

**Security features:**
- Runs as non-root `app` user (UID 1000)
- Uses `tini` as init for proper signal handling
- No build tools in final image
- `PYTHONDONTWRITEBYTECODE=1`
- `EXPOSE 8000`

**Includes:**
- `psycopg2-binary` + `asyncpg` for PostgreSQL
- `celery[redis]` for async tasks
- `prometheus-fastapi-instrumentator` for metrics
- `structlog` for structured logging

---

## 3. Celery & Redis Improvements

### 3.1 Celery Application (`celery_app.py`)

**File:** `apps/shared_core/celery_app.py`

**Changes:**
- **Task timeouts:**
  - `task_time_limit=1800` (30 min, configurable via `CELERY_TASK_TIME_LIMIT`)
  - `task_soft_time_limit=1500` (25 min, configurable via `CELERY_TASK_SOFT_TIME_LIMIT`)
- **Task reliability:**
  - `task_acks_late=True` (re-deliver on worker crash)
  - `task_reject_on_worker_lost=True`
- **Worker management:**
  - `worker_max_tasks_per_child=100` (configurable)
  - `worker_max_memory_per_child=256000` (256 MB)
- **Redis configuration:**
  - `redis_max_connections=50` (configurable)
  - Connection timeouts configured
- **Rate limiting:**
  - `task_default_rate_limit="100/m"` (configurable)
- **Compression:**
  - `task_compression="gzip"`
  - `result_compression="gzip"`
- **Extended result storage** (`result_extended=True`)

**Built-in periodic tasks:**
| Task | Schedule | Purpose |
|------|----------|---------|
| `satellite.weekly_vegetation_check` | Every 7 days | Vegetation monitoring |
| `shared_core.cleanup_expired_tokens` | Every 6 hours | Token cleanup |
| `shared_core.health_check_database` | Every hour | DB health check |

**Signal handlers:**
- `after_setup_logger` → structured logging for Celery logger
- `after_setup_task_logger` → structured logging for task logger

**Stub improvements:**
- Added `ready()`, `successful()`, `failed()`, `state` properties
- Added `.s()` signature support for chaining
- `send_task()` stub

---

## 4. Structured Logging

### 4.1 Logging Configuration (`logging_config.py`)

**File:** `apps/shared_core/logging_config.py` (new)

**Features:**

- **JSON log formatter** with fields:
  - `timestamp` (ISO 8601 UTC)
  - `level`, `logger`, `service`, `environment`
  - `message`, `module`, `function`
  - `request_id`, `client_ip`, `duration_ms` (when available)
  - `exception` (type + message)
  - Custom `_structured_fields` from adapters

- **Log rotation:**
  - `RotatingFileHandler` (size-based, 10 MB default)
  - `TimedRotatingFileHandler` (daily rotation, 30-day retention)
  - Separate error log file

- **Third-party noise reduction:**
  - `sqlalchemy.engine` → WARNING
  - `uvicorn.access` → WARNING
  - `httpx`, `httpcore`, `urllib3` → WARNING
  - `aiosqlite`, `asyncio` → WARNING

- **Celery integration:**
  - `configure_celery_logging()` 
  - `configure_celery_task_logging()`

- **Structured logger adapter:**
  ```python
  from apps.shared_core.logging_config import get_structured_logger
  logger = get_structured_logger(__name__, request_id="abc123")
  logger.info("Processing", extra={"farm_id": "f1", "duration_ms": 45.2})
  ```

**Configuration via settings:**
| Setting | Default | Description |
|---------|---------|-------------|
| `LOG_LEVEL` | INFO | Root log level |
| `LOG_FORMAT` | json | `json` or `text` |
| `LOG_FILE` | None | Log file path |

**Usage in `main.py`:**
```python
from apps.shared_core.logging_config import configure_logging
# In lifespan:
configure_logging()
```

---

## 5. Security Improvements

### 5.1 Security Headers Middleware

**File:** `apps/shared_core/middleware/security_headers.py` (new)

Helmet-like security headers middleware with environment-aware configuration:

**Production headers:**
- `Content-Security-Policy` (strict)
- `X-Frame-Options: SAMEORIGIN`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Strict-Transport-Security` (HSTS, 1 year)
- `Permissions-Policy` (restricts camera, mic, USB, etc.)
- `Cross-Origin-Opener-Policy: same-origin`
- `Cross-Origin-Resource-Policy: same-origin`
- `Cross-Origin-Embedder-Policy: require-corp`

**Development headers:**
- Relaxed CSP (allows `unsafe-inline`, `unsafe-eval`, WebSocket)
- No HSTS
- No COOP/CORP/COEP

**Smart handling:**
- Static assets exempt from `Cache-Control: no-store`
- HSTS skipped for non-HTTPS connections
- Server fingerprint headers stripped (`server`, `X-Powered-By`, `X-AspNet-Version`)
- Non-overriding: respects headers already set by application

### 5.2 Rate Limit Middleware (verified)

**File:** `apps/shared_core/middleware/rate_limit.py` (existing, verified active)

Already registered in `main.py` via:
```python
from apps.shared_core.middleware.rate_limit import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware)
```

Configuration via settings:
- `AUTH_RATE_LIMIT_MAX` (default: 10)
- `AUTH_RATE_LIMIT_WINDOW_SECONDS` (default: 60)

### 5.3 SpiderGuard & SecurityMiddleware (verified)

**Files:** `apps/shared_core/middleware/security_middleware.py`, `apps/shared_core/security_init.py`

- `SecurityMiddleware` injects security headers on every response
- `SpiderGuardMiddleware` blocks malicious user agents and SQL injection patterns
- Both active via `initialize_security(app)` in `main.py` lifespan

---

## 6. Integration in main.py

The following integrations should be added to `apps/main.py`:

### Logging bootstrap
```python
try:
    from apps.shared_core.logging_config import configure_logging
    configure_logging()
except Exception as e:
    logger.debug("Structured logging unavailable: %s", e)
```

### Security headers middleware
```python
try:
    from apps.shared_core.middleware.security_headers import SecurityHeadersMiddleware
    app.add_middleware(SecurityHeadersMiddleware, environment=settings.ENVIRONMENT)
    logger.info("SecurityHeadersMiddleware enabled")
except Exception as e:
    logger.debug("SecurityHeadersMiddleware unavailable: %s", e)
```

---

## Files Created/Modified

### Created
| File | Purpose |
|------|---------|
| `docker/docker-compose.postgres.yml` | Standalone PostgreSQL + pgAdmin |
| `docker/init-db.sql` | Initial database schema |
| `docker/Dockerfile.backend` | Production multi-stage Dockerfile |
| `docker-compose.prod.yml` | Full production stack (overwritten) |
| `apps/shared_core/logging_config.py` | Structured logging |
| `apps/shared_core/middleware/security_headers.py` | Helmet-like headers |
| `docs/INFRA_UPGRADE.md` | This document |

### Modified
| File | Changes |
|------|---------|
| `apps/shared_core/database/session.py` | PostgreSQL pool tuning, better fallback, `is_postgres()` |
| `apps/shared_core/config.py` | New DB pool fields, Celery backend, logging settings |
| `apps/shared_core/celery_app.py` | Timeouts, reliability, built-in tasks, structured logging |

---

## Quick Start

### Local PostgreSQL
```bash
# Start PostgreSQL + pgAdmin
docker compose -f docker/docker-compose.postgres.yml up -d

# Set environment
set DATABASE_URL=postgresql+asyncpg://econojin:econojin_dev@localhost:5432/econojin
set FORCE_POSTGRES=1

# Run the app
python -m uvicorn apps.main:app --reload
```

### Full Production Stack
```bash
# Build and start everything
docker compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker compose -f docker-compose.prod.yml exec api alembic upgrade head

# Check health
curl http://localhost:8000/health
```

### Structured Logging
```bash
# JSON logs to file
set LOG_FILE=logs/app.log
set LOG_FORMAT=json

# Human-readable logs
set LOG_FORMAT=text
```

---

## Next Steps

1. **Run Alembic migrations** against PostgreSQL (instead of `create_all`)
2. **Set up SSL certificates** for nginx (Let's Encrypt or managed)
3. **Configure secrets** (DB password, Redis password, JWT keys) via Docker secrets or HashiCorp Vault
4. **Set up database backups** (pg_dump cron job)
5. **Configure Prometheus alerting rules** in `monitoring/prometheus/`
6. **Set up Grafana dashboards** for database metrics, API latency, Celery queue depth
