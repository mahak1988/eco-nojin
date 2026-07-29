# Contributing

Thanks for contributing to the Econojin SaaS monorepo.

## Getting started

1. Fork the repository.
2. Run `pnpm install`.
3. Use `pnpm dev:web` and `pnpm dev:cms` to boot the frontend and CMS locally.
4. Open a pull request against `main` with a clear description.

## Coding standards

- Use TypeScript for all frontend code.
- Use Tailwind CSS and shared UI components from `packages/ui`.
- Keep shared types in `packages/types`.
- Write tests for new features with Vitest and Playwright.

## Review process

- All contributions must pass lint, type-check, unit tests, and E2E tests.
- Keep commits focused and use meaningful messages.
