# web | اپلیکیشن web

Front-end application of the **Eco Nojin** platform.

## Overview

This app is built with:
- React 18
- TypeScript
- Vite
- Tailwind CSS
- Axios
- `@supabase/supabase-js`
- `@tanstack/react-query`

## Structure

```
web/
├── public/             # Static assets
├── src/
│   ├── api/            # Axios API clients
│   ├── components/     # Reusable UI components
│   ├── hooks/          # Custom React hooks
│   ├── lib/            # Utility functions and helpers
│   ├── services/       # service clients (Supabase, API integration)
│   ├── types/          # shared TypeScript types
│   └── pages/          # route-level components
└── __tests__/          # test files
```

## Environment

Copy `apps/web/.env.example` to `apps/web/.env.local` and configure:
- `VITE_API_BASE_URL`
- `VITE_DEFAULT_LANG`
- Optional: `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`
- Optional: `VITE_SENTRY_DSN`, `VITE_GA_MEASUREMENT_ID`

## Development

```bash
# Install dependencies from repo root
pnpm install

# Run the frontend
pnpm --filter @econojin/web dev

# Build for production
pnpm --filter @econojin/web build

# Lint TypeScript and files
pnpm --filter @econojin/web lint
```

## Notes

- API calls are configured through `VITE_API_BASE_URL`.
- Supabase client is implemented in `src/services/supabase.ts`.
- The app uses alias imports configured in `vite.config.ts`.
