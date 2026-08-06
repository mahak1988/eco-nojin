import { useEffect, useState } from 'react'
import { Activity, Cpu, Database, Server, RefreshCw, Loader2, AlertCircle, CheckCircle, XCircle } from 'lucide-react'
import { fetchSystemHealth, SystemHealth } from '../api/adminApi'

export default function MonitoringPage() {
  const [health, setHealth] = useState<SystemHealth | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastRefresh, setLastRefresh] = useState(new Date())

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchSystemHealth()
      setHealth(data)
      setLastRefresh(new Date())
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'خطا در دریافت وضعیت سیستم')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    const interval = setInterval(load, 30000) // auto-refresh every 30s
    return () => clearInterval(interval)
  }, [])

  const dbOk = health?.database === 'ok' || health?.database === 'healthy'
  const redisOk =
    health?.redis === 'ok' ||
    health?.redis === 'healthy' ||
    health?.redis === 'unavailable'

  const stats = health
    ? [
        {
          label: 'پایگاه داده',
          value: health.database,
          ok: dbOk,
          icon: <Database className="w-5 h-5" />,
          detail:
            health.database_latency_ms != null
              ? `${health.database_latency_ms} ms`
              : undefined,
        },
        {
          label: 'Redis',
          value: health.redis,
          ok: redisOk,
          icon: <Server className="w-5 h-5" />,
          detail:
            health.redis_latency_ms != null
              ? `${health.redis_latency_ms} ms`
              : undefined,
        },
        {
          label: 'کل کاربران',
          value: String(health.total_users ?? '—'),
          ok: true,
          icon: <Activity className="w-5 h-5" />,
          detail: `فعال ۲۴س: ${health.active_users_last_24h ?? '—'}`,
        },
        {
          label: 'مسیرهای API',
          value: String(health.total_api_routes ?? '—'),
          ok: (health.total_api_routes ?? 0) > 0,
          icon: <Cpu className="w-5 h-5" />,
          detail: health.environment,
        },
      ]
    : []

  return (
    <div className="space-y-6" dir="rtl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">نظارت سیستم</h1>
          <p className="text-muted-foreground">
            وضعیت زنده سلامت سیستم · آخرین به‌روزرسانی:{' '}
            {lastRefresh.toLocaleTimeString('fa-IR')}
          </p>
        </div>
        <button
          onClick={load}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg border bg-background hover:bg-muted text-sm disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          به‌روزرسانی
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          {error}
        </div>
      )}

      {loading && !health && (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="w-8 h-8 animate-spin text-eco-600" />
        </div>
      )}

      {health && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {stats.map((stat) => (
              <div key={stat.label} className="rounded-xl border bg-card p-5 shadow-sm">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-muted-foreground">{stat.label}</p>
                  {stat.ok ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <XCircle className="w-4 h-4 text-red-500" />
                  )}
                </div>
                <p className={`text-2xl font-bold ${stat.ok ? 'text-foreground' : 'text-destructive'}`}>
                  {stat.value}
                </p>
                {stat.detail && (
                  <p className="text-xs text-muted-foreground mt-1">{stat.detail}</p>
                )}
              </div>
            ))}
          </div>

          <div className="rounded-xl border bg-card shadow-sm p-5">
            <h2 className="font-semibold mb-3">جزئیات فنی</h2>
            <dl className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
              <div>
                <dt className="text-muted-foreground">محیط اجرا</dt>
                <dd className="font-medium">{health.environment}</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">نسخه پایتون</dt>
                <dd className="font-medium">{health.python_version}</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">آپتایم (ثانیه)</dt>
                <dd className="font-medium">{health.uptime_seconds ?? '—'}</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">تأخیر پایگاه داده</dt>
                <dd className="font-medium">
                  {health.database_latency_ms != null
                    ? `${health.database_latency_ms} ms`
                    : '—'}
                </dd>
              </div>
            </dl>
          </div>
        </>
      )}
    </div>
  )
}
