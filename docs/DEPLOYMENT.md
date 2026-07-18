# Deployment Guide

This project supports development and production deployment with Docker Compose, local Strapi CMS, and optional Supabase support.

## Recommended deployment flow

1. Provision infrastructure for your backend, database, CMS, and hosting platform.
2. Configure environment variables for the Python backend, Strapi, and frontend.
3. Deploy the monorepo services:
   - API backend from `apps/main.py`
   - Web frontend from `apps/web/`
   - Optional Strapi CMS from `apps/cms/`
4. Connect Supabase only if you need auth, storage, or tenant-based real-time flows.
5. Expose public routes through a reverse proxy, load balancer, or hosting platform.

## Strapi CMS deployment

`apps/cms` is a Strapi v5 headless CMS package for optional marketing and content management.

### Local startup

```bash
cd apps/cms
pnpm install
pnpm dev
```

### Production startup

```bash
cd apps/cms
pnpm install
pnpm build
pnpm start
```

### Required environment variables

- `PUBLIC_URL` — public URL of the Strapi service, used for content links and media URLs.
- `DATABASE_URL` — database connection string for Strapi (PostgreSQL recommended in production).
- `ADMIN_JWT_SECRET` — admin auth secret for the Strapi admin panel.
- `STRAPI_TOKEN` — optional internal token for webhooks and service integrations.
- `STRAPI_HOST` — host binding for Strapi (`0.0.0.0` for container deployment).
- `STRAPI_PORT` — HTTP port for Strapi (default `1337`).

### Deployment notes

- Run Strapi as a separate container or process from the main backend.
- In production, `DATABASE_URL` should point to a managed PostgreSQL instance or cloud database.
- Set `PUBLIC_URL` to the public-facing Strapi address, not the internal container hostname.
- Use a secure random value for `ADMIN_JWT_SECRET` and rotate it when needed.

## Docker Compose guidance

### `docker-compose.apps.yml`

This file is the primary local development stack for the `web` and API services.

- `db` — PostgreSQL database for backend development.
- `redis` — Redis cache.
- `api` — Python backend container built from `docker/Dockerfile.api`.
- `web` — Node frontend container running Vite.

Use:

```bash
docker compose -f docker-compose.apps.yml up --build
```

### `infrastructure/docker-compose.yml`

This file provides optional support services for the monorepo:

- `n8n` — automation/workflow engine stub.
- `postgres` — additional PostgreSQL service.
- `supabase-studio` — Supabase Studio UI for local debugging.

> Note: `infrastructure/docker-compose.yml` is not a full Supabase stack. It is a support composition for local and exploratory use.

### `docker-compose.prod.yml`

The production compose file is intended for a production-ready stack with environment-protected Postgres credentials.

## Supabase integration

The frontend uses Supabase only when the following environment variables are set.

- `VITE_SUPABASE_URL` — your Supabase project URL.
- `VITE_SUPABASE_ANON_KEY` — the public anon key used by client-side Supabase.

### Frontend behavior

`apps/web/src/services/supabase.ts` reads `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`. If these values are not present, Supabase client construction falls back to placeholder values, but actual auth/storage functionality requires valid Supabase credentials.

### Recommended deployment pattern

- Use a dedicated Supabase project for production auth, storage, and realtime features.
- Keep the anon key public but never expose service keys in frontend code.
- If you need Supabase in backend workflows, configure service keys only in server-side environment variables and secrets.

## Environment configuration

1. Copy `.env.example` to `.env` for the backend runtime.
2. Copy `apps/web/.env.example` to `apps/web/.env.local` for the frontend.
3. Set Strapi-specific values for `apps/cms` in a local `apps/cms/.env`, in your container environment, or in deployment secrets.

## Deployment checklist

- [ ] `DATABASE_URL` configured for the Python API.
- [ ] Backend env values set: `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `LLM_PROVIDER`.
- [ ] Strapi env values set: `PUBLIC_URL`, `DATABASE_URL`, `ADMIN_JWT_SECRET`, `STRAPI_HOST`, `STRAPI_PORT`.
- [ ] Frontend env values set: `VITE_API_BASE_URL`, optional `VITE_SUPABASE_URL`, and `VITE_SUPABASE_ANON_KEY`.
- [ ] Reverse proxy or platform routes configured for API, frontend, and CMS.
- [ ] Static or media hosting for Strapi uploads if required.
