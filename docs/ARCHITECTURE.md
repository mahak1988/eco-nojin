# Architecture Overview

This repository now follows a modern composable FOSS monorepo architecture for a multi-tenant SaaS dashboard.

## Workspace layout

- `apps/web/` - Next.js frontend app with App Router, Supabase integration, Strapi CMS support, real-time dashboard pages, file uploads, and notification plumbing.
- `apps/cms/` - Strapi v5 headless CMS for content management and marketing content.
- `apps/admin/` - Optional internal admin dashboard stub for future multi-tenant admin features.
- `packages/ui/` - Shared UI primitives and Shadcn-compatible component library.
- `packages/types/` - Shared TypeScript types for tenant, user, and API contracts.
- `packages/config-eslint/` - Shared ESLint configuration.
- `packages/config-typescript/` - Shared TypeScript config for Web and admin apps.
- `infrastructure/` - Deployment and self-hosted infrastructure artifacts for Coolify, Docker Compose, and optional Terraform.
- `docs/` - Architecture, deployment, API, and contribution documentation.

## Core stack

- Frontend: Next.js 16, React 19, TypeScript, Tailwind CSS v4
- Backend: Supabase for Auth, DB, Storage, Real-time updates
- CMS: Strapi v5
- Automation: n8n self-hosted automation workflows
- State: Zustand + TanStack Query
- Forms: React Hook Form + Zod
- Testing: Vitest + Playwright
- Deployment: Coolify + Cloudflare Pages
- CI/CD: GitHub Actions + Turborepo
- Monitoring: Sentry + Grafana (planned)

## Multitenancy

The monorepo is prepared to support tenant-aware routes, RLS-enabled Supabase policies, role-based pages, and separate internal admin experiences.
