import { FormEvent, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Loader2, LogIn } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

export default function LoginPage() {
  const { login, error, clearError, loading, isAuthenticated } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const from = (location.state as any)?.from || '/'

  if (isAuthenticated) {
    navigate(from, { replace: true })
  }

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    clearError()
    setSubmitting(true)
    try {
      await login(email.trim(), password)
      navigate(from, { replace: true })
    } catch {
      /* error in context */
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/30 p-4" dir="rtl">
      <div className="w-full max-w-md rounded-2xl border bg-card p-8 shadow-sm">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-eco-700">پنل مدیریت اکونوژین</h1>
          <p className="text-sm text-muted-foreground mt-1">ورود با حساب مدیر سیستم</p>
        </div>

        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-1 block">ایمیل</label>
            <input
              type="email"
              required
              autoComplete="username"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2.5 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-eco-500"
              placeholder="admin@econojin.com"
            />
          </div>
          <div>
            <label className="text-sm font-medium mb-1 block">رمز عبور</label>
            <input
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2.5 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-eco-500"
              placeholder="••••••••"
            />
          </div>

          {error && (
            <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={submitting || loading}
            className="w-full flex items-center justify-center gap-2 py-2.5 bg-eco-600 text-white rounded-lg hover:bg-eco-700 text-sm font-medium disabled:opacity-50"
          >
            {submitting ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <LogIn className="w-4 h-4" />
            )}
            ورود
          </button>
        </form>

        <p className="text-xs text-muted-foreground text-center mt-6">
          احراز هویت با کوکی HttpOnly (اولویت) و Bearer در حالت ترکیبی
        </p>
      </div>
    </div>
  )
}
