# web | اپلیکیشن web

Part of the **Eco Nojin** platform.

## Overview

This is the web frontend application, built with:
- React 18
- TypeScript
- Vite
- Tailwind CSS
- TanStack Query (React Query)

## Structure

```
web/
├── src/
│   ├── pages/           # Route-level components
│   ├── components/      # Reusable UI components
│   ├── hooks/           # React Query hooks
│   ├── api/             # API client
│   ├── types/           # TypeScript types
│   └── lib/             # Utility functions
└── __tests__/           # Vitest tests
```

## Development

```bash
# Install dependencies (from repo root)
pnpm install

# Run dev server
pnpm --filter web dev

# Build for production
pnpm --filter web build

# Run tests
pnpm --filter web test
```

## Auto-scaffolded

This module was auto-scaffolded by `scripts/phase1_complete_apps.py`.
Adjust the templates to match your actual UI requirements.
