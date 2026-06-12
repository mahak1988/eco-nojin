# Packages

This directory contains shared packages used across the monorepo.

## Structure

### `@econojin/lib`
Shared utilities, API clients, hooks, and validation schemas.

### `@econojin/features`
Feature-specific components and logic (GIS, Analysis, IoT, etc.).

### `@econojin/ui`
Shared UI components (shadcn/ui based).

### `@econojin/types`
Shared TypeScript type definitions.

### `config-eslint`
Shared ESLint configuration.

### `config-typescript`
Shared TypeScript configuration.

## Usage

In your app's `package.json`:

```json
{
  "dependencies": {
    "@econojin/lib": "workspace:*",
    "@econojin/features": "workspace:*"
  }
}
```

Then import in your code:

```typescript
import { useAuth } from "@econojin/lib/hooks";
import { GisMap } from "@econojin/features/gis";
```