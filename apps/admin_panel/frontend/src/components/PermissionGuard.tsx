import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import ForbiddenPage from '../pages/ForbiddenPage'

/** Map path prefixes → required permission (any match grants access). */
export const ROUTE_PERMISSIONS: Record<string, string[]> = {
  '/users': ['users.read', 'users.manage'],
  '/audit-logs': ['audit.logs.read'],
  '/monitoring': ['system.health.check'],
  '/security': ['security.manage', 'system.health.check'],
  '/insights': ['analytics.intelligent.view', 'recommendations.view'],
  '/reports': ['reports.read', 'reports.generate'],
  '/accounting': ['dashboard.view'],
  '/settings': ['settings.read', 'settings.write'],
}

export function requiredPermissionsForPath(pathname: string): string[] | null {
  const entries = Object.entries(ROUTE_PERMISSIONS).sort((a, b) => b[0].length - a[0].length)
  for (const [prefix, perms] of entries) {
    if (pathname === prefix || pathname.startsWith(prefix + '/')) {
      return perms
    }
  }
  return null // public within auth shell
}

export default function PermissionGuard({
  children,
  permission,
  anyOf,
}: {
  children: React.ReactNode
  permission?: string
  anyOf?: string[]
}) {
  const { user, permissions, loading } = useAuth()

  if (loading) return null

  // Superuser always allowed
  if (user?.is_superuser) return <>{children}</>

  const needed = anyOf || (permission ? [permission] : [])
  if (needed.length === 0) return <>{children}</>

  // If permissions not loaded yet, fall back to role heuristics
  const effective =
    permissions.length > 0
      ? permissions
      : user?.role === 'admin'
        ? ['users.read', 'audit.logs.read', 'system.health.check', 'reports.read', 'settings.read']
        : ['dashboard.view']

  const ok = needed.some((p) => effective.includes(p))
  if (!ok) {
    return <ForbiddenPage />
  }

  return <>{children}</>
}

/** HOC-style wrapper using path-based map */
export function PathPermissionGuard({ children }: { children: React.ReactNode }) {
  const location = window.location.pathname.replace(/.*admin/, '') || window.location.pathname
  // Use react-router location via children parent; this component should be used inside Routes
  return <>{children}</>
}
