# Frontend structure (post-expansion)

Added layers (2026-07-26):

- `src/api/` — domain HTTP clients
- `src/hooks/` — React Query data hooks
- `src/stores/` — Zustand auth/ui
- `src/types/` — shared TypeScript types
- `src/features/auth` — LoginForm, RequireAuth
- `src/features/admin` — AdminShell
- `src/features/dashboard` — HealthWidget
- `src/pages/admin/*` — admin panel pages
- `src/pages/LoginPage.tsx`
- `src/components/ui/*` — Badge, EmptyState, PageHeader, Spinner, DataSourceBadge
- `src/lib/format.ts`, `cn.ts`

Wire admin routes in `App.tsx`:

```tsx
<Route path="login" element={<LoginPage />} />
<Route path="admin" element={<AdminShell />}>
  <Route index element={<AdminOverviewPage />} />
  <Route path="users" element={<AdminUsersPage />} />
  <Route path="modules" element={<AdminModulesPage />} />
  <Route path="health" element={<AdminHealthPage />} />
  <Route path="settings" element={<AdminSettingsPage />} />
</Route>
```
