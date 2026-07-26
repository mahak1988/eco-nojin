# Engineering Standards — Econojin

## Language
- **Code** (identifiers, comments, docstrings, commits): English
- **UI strings**: i18n (`fa` default product locale, `en` required)
- **Product docs for Iranian users**: `docs/*_FA.md` (Persian)
- **Technical docs** (architecture, security, deploy): English in `docs/`

## API
- All routes under `/api/v1/`
- OpenAPI is the contract source of truth
- Write operations require JWT when `REQUIRE_AUTH_FOR_WRITES=true`

## Frontend layout
```
apps/web/src/
  api/          # HTTP clients per domain
  hooks/        # React Query / data hooks
  stores/       # client state
  types/        # shared TS types
  features/     # feature-scoped modules
  pages/        # route pages
  pages/admin/  # admin panel
  components/   # presentational UI
  lib/          # pure utilities
```

## Git
- Branch: `feature/*` or `fix/*`
- Commit style: `type(scope): message` (feat, fix, chore, docs, security)
