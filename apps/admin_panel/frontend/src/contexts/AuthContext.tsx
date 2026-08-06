import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'

export interface AuthUser {
  id: number
  email: string
  full_name?: string | null
  is_superuser?: boolean
  is_active?: boolean
  role?: string
  permissions?: string[]
}

interface AuthContextValue {
  user: AuthUser | null
  loading: boolean
  isAuthenticated: boolean
  permissions: string[]
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  refresh: () => Promise<void>
  error: string | null
  clearError: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

/** Phase 4: when true, never persist tokens in localStorage (cookie-only). */
const COOKIE_ONLY =
  String(import.meta.env.VITE_COOKIE_ONLY || '').toLowerCase() === 'true' ||
  import.meta.env.PROD === true

function clearTokens() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('accessToken')
  localStorage.removeItem('token')
}

function storeTokenIfAllowed(token: string | undefined) {
  if (!token || COOKIE_ONLY) return
  localStorage.setItem('access_token', token)
}

/**
 * Cookie-first auth. In production / VITE_COOKIE_ONLY=true: no localStorage tokens.
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [permissions, setPermissions] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const clearError = useCallback(() => setError(null), [])

  const hydrate = useCallback(async () => {
    try {
      let me: AuthUser | null = null
      const endpoints = ['/api/v1/users/me', '/api/v1/auth/me']
      for (const url of endpoints) {
        try {
          const res = await fetch(url, { credentials: 'include' })
          if (res.ok) {
            me = await res.json()
            break
          }
        } catch {
          /* next */
        }
      }

      // Soft session only in non-cookie-only hybrid mode
      if (!me && !COOKIE_ONLY) {
        const token =
          localStorage.getItem('access_token') ||
          localStorage.getItem('accessToken') ||
          localStorage.getItem('token')
        if (token) {
          me = { id: 0, email: 'admin@session', is_superuser: true }
        }
      }

      if (me) {
        try {
          const pr = await fetch('/api/v1/admin/me/permissions', { credentials: 'include' })
          if (pr.ok) {
            const pdata = await pr.json()
            const perms = pdata.permissions || []
            setPermissions(perms)
            me = { ...me, permissions: perms, role: pdata.role || me.role }
          }
        } catch {
          /* optional */
        }
      } else {
        setPermissions([])
      }

      setUser(me)
    } catch {
      setUser(null)
      setPermissions([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    hydrate()
  }, [hydrate])

  const login = useCallback(
    async (email: string, password: string) => {
      setError(null)
      setLoading(true)
      try {
        const tryLogin = async (url: string) => {
          const res = await fetch(url, {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
          })
          return res
        }

        let res = await tryLogin('/api/v1/auth/login')
        if (!res.ok) res = await tryLogin('/api/v1/users/login')
        if (!res.ok) {
          const detail = await res.json().catch(() => ({}))
          throw new Error(detail?.detail || 'ورود ناموفق بود')
        }
        const data = await res.json().catch(() => ({}))
        storeTokenIfAllowed(data.access_token || data.accessToken || data.token)
        await hydrate()
      } catch (e: any) {
        setError(e?.message || 'خطا در ورود')
        setUser(null)
        throw e
      } finally {
        setLoading(false)
      }
    },
    [hydrate]
  )

  const logout = useCallback(async () => {
    try {
      await fetch('/api/v1/auth/logout', { method: 'POST', credentials: 'include' }).catch(() => null)
    } finally {
      clearTokens()
      setUser(null)
      setPermissions([])
    }
  }, [])

  const value = useMemo(
    () => ({
      user,
      loading,
      isAuthenticated: !!user,
      permissions,
      login,
      logout,
      refresh: hydrate,
      error,
      clearError,
    }),
    [user, loading, permissions, login, logout, hydrate, error, clearError]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
