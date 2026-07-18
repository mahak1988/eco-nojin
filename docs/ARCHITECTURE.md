# Architecture Overview

This repository is a composable monorepo for the Eco Nojin platform. It combines:

- Python backend services under `apps/`
- A Vite-based React frontend in `apps/web/`
- A Strapi CMS package in `apps/cms/`
- Shared TypeScript packages in `packages/`
- Deployment and infrastructure artifacts in `infrastructure/` and `docker/`

## Workspace layout

- `apps/main.py` - FastAPI application entrypoint and router composition.
- `apps/api/` - Backend module scaffold with CRUD route templates and shared API utilities.
- `apps/users/` - User management, authentication, and user-facing API endpoints.
- `apps/ai_agents/` - AI agent endpoints and streaming response handlers.
- `apps/simulation/` - Simulation API endpoints and domain logic.
- `apps/shared_core/`, `apps/shared_ai/`, `apps/shared_knowledge/`, `apps/shared_sim/`, `apps/shared/` - Shared backend modules, database session and reusable services.
- `apps/web/` - Frontend app built with Vite, React, TypeScript, Tailwind CSS, and Axios.
- `apps/cms/` - Strapi v5 headless CMS package for marketing and content management.
- `packages/` - Shared libraries, types, and configuration packages consumed by frontend modules.

## Backend architecture

- `apps/main.py` is the canonical FastAPI server entrypoint.
- Environment variables are loaded from `.env` using `dotenv`.
- Routers are registered in `apps/main.py` for:
  - `/api/v1/users`
  - `/api/v1/auth`
  - `/api/v1/ai-agents`
  - `/api/v1/simulation`
- Backend modules use async SQLAlchemy via `apps/shared_core/database/session.py`.
- The backend exposes health and root endpoints at:
  - `/`
  - `/health`
- Global middleware includes CORS and request timing.

## Frontend architecture

- `apps/web/` is a Vite-powered React app.
- Source code is organized into `src/components`, `src/hooks`, `src/api`, `src/services`, `src/lib`, and `src/types`.
- API integration is handled through Axios clients in `src/api/index.ts` and `src/lib/api-client.ts`.
- Supabase authentication and session handling live in `src/services/supabase.ts`.
- Frontend environment configuration is sourced from `apps/web/.env.example` and `VITE_API_BASE_URL`.

## Data flow

- The frontend calls backend APIs through the configured `VITE_API_BASE_URL`.
- The backend reads data from an async SQLAlchemy session and may use local SQLite or Postgres via `DATABASE_URL`.
- Strapi in `apps/cms/` is an optional content source for marketing pages and CMS-managed content.
- AI-related requests route through `apps/ai_agents/` and shared AI modules under `apps/shared_ai/`.

## Libraries and technology stack

### Frontend
- React 18.3.1
- Vite 5.4.21
- TypeScript 5.5.4
- Tailwind CSS 3.4.19
- Axios 1.17.0
- `@supabase/supabase-js` 2.108.2
- `@tanstack/react-query` 5.101.2
- `react-router-dom` 6.30.4
- `zustand` 5.0.14

### Backend
- FastAPI
- Python async SQLAlchemy
- Pydantic
- python-dotenv
- Uvicorn

### CMS and tooling
- Strapi v5
- pnpm workspace
- Turbo repo pipeline
- ESLint and TypeScript shared config packages

## Repository tooling

- Root `package.json` defines monorepo scripts and Turbo tasks.
- `pnpm-workspace.yaml` includes `apps/*` and `packages/*`.
- `turbo.json` configures build, lint, type-check, and dev task behavior.

## Notes

- The current workspace does not include a dedicated `apps/admin/` application.
- `apps/main.py` is the actual FastAPI entrypoint, not `api/main.py`.
- Backend module composition is dynamic and may import optional routers if present.
- `apps/web/` is the active frontend app, while `apps/cms/` is the current CMS package.
