# Econojin Multi-tenant SaaS Monorepo

This repository has been upgraded to a modern composable SaaS monorepo architecture.

## Workspace structure

- `apps/web/` — Production-ready Next.js frontend using App Router.
- `apps/cms/` — Strapi v5 CMS for content and marketing pages.
- `apps/admin/` — Optional admin workspace for tenant and user operations.
- `packages/ui/` — Shared UI component library.
- `packages/types/` — Shared TypeScript definitions.
- `packages/config-eslint/` — Central ESLint config.
- `packages/config-typescript/` — Central TypeScript config for Next.js apps.
- `infrastructure/` — Deployment and infrastructure artifacts for Coolify, Docker Compose, and Terraform.
- `docs/` — Architecture, deployment, API, and contribution documentation.

## Quick start

```bash
pnpm install
pnpm dev:web
```

Run the CMS locally:

```bash
pnpm dev:cms
```

Start the optional admin workspace:

```bash
pnpm dev:admin
```

## Main commands

- `pnpm build` — Build the web frontend.
- `pnpm lint` — Run ESLint for the web app.
- `pnpm type-check` — Run TypeScript type checking.
- `pnpm test` — Run Vitest unit tests.
- `pnpm test:e2e` — Run Playwright end-to-end tests.

## Tech stack

- Frontend: Next.js 16, React 19, TypeScript, Tailwind CSS v4
- Backend: Supabase for Auth, DB, Storage, and Realtime
- CMS: Strapi v5
- Automation: n8n
- Deployment: Coolify + Cloudflare Pages
- CI/CD: GitHub Actions + Turborepo
- Testing: Vitest + Playwright

## Notes

This scaffold preserves the existing `apps/web` frontend while putting the codebase into a monorepo layout aligned with the requested architecture.
