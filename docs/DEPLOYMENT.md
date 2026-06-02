# Deployment Guide

This project is designed for self-hosted deployment with full control using Coolify, Docker Compose, and optional Terraform.

## Recommended deployment flow

1. Provision infrastructure for PostgreSQL, Supabase, Strapi, and app hosting.
2. Configure environment variables in Coolify or your deployment environment.
3. Deploy the frontend container from `apps/web/Dockerfile`.
4. Deploy `apps/cms` as a Strapi container.
5. Connect Supabase storage and auth, then enable RLS policies for multitenancy.
6. Configure Cloudflare Pages or a reverse proxy for public hosting.

## Local development

1. Install dependencies:
```bash
pnpm install
```
2. Start the web app:
```bash
pnpm dev:web
```
3. Start Strapi CMS:
```bash
pnpm dev:cms
```
4. Start optional admin UI:
```bash
pnpm dev:admin
```

## Self-hosted services

- `infrastructure/docker-compose.yml` includes n8n, PostgreSQL, and Supabase Studio stubs.
- `infrastructure/coolify/apps.json` contains a Coolify app configuration for the frontend.
- `infrastructure/terraform/main.tf` provides a starter template for optional IaC.
