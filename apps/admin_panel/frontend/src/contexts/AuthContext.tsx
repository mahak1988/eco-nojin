import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { api } from '../api/adminApi'

export interface AuthUser {
  id: number
  email: string
  full_name?: string | null
  is_superuser?: boolean
  is_active?: boolean
  role?: string
}

interface AuthContextValue {
  user: AuthUser | null
  loading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  refresh: () => Promise<void>
  error: string | null
  clearError: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

/**
 * Cookie-first auth with optional Bearer fallback for hybrid backends.
 * Prefer HttpOnly cookies (withCredentials); store token only if API returns it.
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const clearError = useCallback(() => setError(null), [])

  const hydrate = useCallback(async () => {
    try {
      // Try admin-aware /auth/me then generic
      const endpoints = ['/api/v1/users/me', '/api/v1/auth/me', '/api/v1/users/auth/me']
      let me: AuthUser | null = null
      for (const url of endpoints) {
        try {
          const { data } = await api.get(url.replace('/api/v1/admin', '') || url, {
            baseURL: '',
            withCredentials: true,
          } as any)
          // Use raw axios via fetch for non-admin base
          const res = await fetch(url, { credentials: 'include' })
          if (res.ok) {
            me = await res.json()
            break
          }
        } catch {
          /* try next */
        }
      }
      // Fallback: if we still have a token, treat as soft-authenticated shell
      if (!me) {
        const token =
          localStorage.getItem('access_token') ||
          localStorage.getItem('accessToken') ||
          localStorage.getItem('token')
        if (token) {
          me = { id: 0, email: 'admin@session', is_superuser: true }
        }
      }
      setUser(me)
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    hydrate()
  }, [hydrate])

  const login = useCallback(async (email: string, password: string) => {
    setError(null)
    setLoading(true)
    try {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
      if (!res.ok) {
        // try alternate path
        const res2 = await fetch('/api/v1/users/login', {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        })
        if (!res2.ok) {
          const detail = await res2.json().catch(() => ({}))
          throw new Error(detail?.detail || 'ورود ناموفق بود')
        }
        const data = await res2.json()
        const token = data.access_token || data.accessToken || data.token
        if (token) {
          localStorage.setItem('access_token', token)
        }
      } else {
        const data = await res.json()
        const token = data.access_token || data.accessToken || data.token
        if (token) {
          // Hybrid: keep until cookie-only is fully enforced server-side
          localStorage.setItem('access_token', token)
        }
      }
      await hydrate()
    } catch (e: any) {
      setError(e?.message || 'خطا در ورود')
      setUser(null)
      throw e
    } finally {
      setLoading(false)
    }
  }, [hydrate])

  const logout = useCallback(async () => {
    try {
      await fetch('/api/v1/auth/logout', { method: 'POST', credentials: 'include' }).catch(() => null)
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('accessToken')
      localStorage.removeItem('token')
      setUser(null)
    }
  }, [])

  const value = useMemo(
    () => ({
      user,
      loading,
      isAuthenticated: !!user,
      login,
      logout,
      refresh: hydrate,
      error,
      clearError,
    }),
    [user, loading, login, logout, hydrate, error, clearError]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
