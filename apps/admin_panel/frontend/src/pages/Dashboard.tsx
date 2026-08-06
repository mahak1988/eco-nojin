import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Users, Settings, FileText, Activity, Shield, BarChart3,
  Cloud, AlertTriangle, Sprout, TrendingUp,
  Map, RefreshCw, CheckCircle, XCircle, Loader2, FlaskConical, Satellite,
} from 'lucide-react'
import { fetchDashboard, fetchSystemHealth, DashboardData, SystemHealth } from '../api/adminApi'

interface StatCardProps {
  title: string
  value: string | number
  icon: React.ReactNode
  color: string
  loading?: boolean
  error?: boolean
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color, loading, error }) => (
  <div className="p-5 bg-card rounded-xl border shadow-sm flex items-center gap-4">
    <div className={`p-3 rounded-lg ${color}`}>{icon}</div>
    <div className="flex-1 min-w-0">
      <p className="text-sm text-muted-foreground truncate">{title}</p>
      {loading ? (
        <Loader2 className="w-4 h-4 animate-spin mt-1 text-muted-foreground" />
      ) : error ? (
        <p className="text-sm text-destructive font-medium">—</p>
      ) : (
        <p className="text-2xl font-bold">{value}</p>
      )}
    </div>
  </div>
)

const Dashboard: React.FC = () => {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null)
  const [health, setHealth] = useState<SystemHealth | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [lastRefresh, setLastRefresh] = useState(new Date())

  const load = async () => {
    setLoading(true)
    setError(false)
    try {
      const [dash, sysHealth] = await Promise.all([
        fetchDashboard(),
        fetchSystemHealth().catch(() => null),
      ])
      setDashboard(dash)
      setHealth(sysHealth)
    } catch {
      setError(true)
    } finally {
      setLoading(false)
      setLastRefresh(new Date())
    }
  }

  useEffect(() => {
    load()
  }, [])

  // Only routes that exist in App.tsx
  const navCards = [
    { to: '/users', label: 'مدیریت کاربران', desc: 'مشاهده و مدیریت کاربران سیستم', icon: <Users className="w-5 h-5" />, color: 'bg-blue-100 text-blue-600' },
    { to: '/farms', label: 'مزارع', desc: 'مدیریت اطلاعات مزارع', icon: <Map className="w-5 h-5" />, color: 'bg-emerald-100 text-emerald-600' },
    { to: '/weather', label: 'آب‌وهوا', desc: 'پیش‌بینی و هشدارهای آب‌وهوایی', icon: <Cloud className="w-5 h-5" />, color: 'bg-sky-100 text-sky-600' },
    { to: '/risks', label: 'ارزیابی ریسک', desc: 'پیش‌بینی و مدیریت ریسک', icon: <AlertTriangle className="w-5 h-5" />, color: 'bg-red-100 text-red-600' },
    { to: '/economics', label: 'اقتصاد سبز', desc: 'تحلیل هزینه-فایده و EcoCoin', icon: <TrendingUp className="w-5 h-5" />, color: 'bg-yellow-100 text-yellow-600' },
    { to: '/satellite', label: 'داده ماهواره‌ای', desc: 'NDVI و تصاویر ماهواره‌ای', icon: <Satellite className="w-5 h-5" />, color: 'bg-lime-100 text-lime-600' },
    { to: '/simulation', label: 'شبیه‌سازی', desc: 'مدل‌های علمی و سناریوها', icon: <FlaskConical className="w-5 h-5" />, color: 'bg-indigo-100 text-indigo-600' },
    { to: '/reports', label: 'گزارش‌ها', desc: 'گزارش‌های سیستم و عملکرد', icon: <BarChart3 className="w-5 h-5" />, color: 'bg-violet-100 text-violet-600' },
    { to: '/audit-logs', label: 'لاگ حسابرسی', desc: 'مشاهده فعالیت‌های سیستم', icon: <Activity className="w-5 h-5" />, color: 'bg-purple-100 text-purple-600' },
    { to: '/monitoring', label: 'نظارت سیستم', desc: 'سلامت و پایش زنده', icon: <Shield className="w-5 h-5" />, color: 'bg-green-100 text-green-600' },
    { to: '/security', label: 'امنیت', desc: 'SpiderGuard و حفاظت', icon: <Shield className="w-5 h-5" />, color: 'bg-orange-100 text-orange-600' },
    { to: '/settings', label: 'تنظیمات', desc: 'پیکربندی ظاهر و سیستم', icon: <Settings className="w-5 h-5" />, color: 'bg-gray-100 text-gray-600' },
  ]

  const statCards = [
    { title: 'کل کاربران', value: dashboard?.user_count ?? '—', icon: <Users className="w-5 h-5" />, color: 'bg-blue-100 text-blue-600' },
    { title: 'کاربران فعال', value: dashboard?.active_user_count ?? '—', icon: <Users className="w-5 h-5" />, color: 'bg-emerald-100 text-emerald-600' },
    { title: 'سوپریوزر', value: dashboard?.superuser_count ?? '—', icon: <Shield className="w-5 h-5" />, color: 'bg-purple-100 text-purple-600' },
    { title: 'تنظیمات', value: dashboard?.total_settings ?? '—', icon: <Settings className="w-5 h-5" />, color: 'bg-gray-100 text-gray-600' },
    { title: 'لاگ حسابرسی', value: dashboard?.total_audit_logs ?? '—', icon: <Activity className="w-5 h-5" />, color: 'bg-amber-100 text-amber-600' },
    { title: 'گزارش‌ها', value: dashboard?.total_reports ?? '—', icon: <FileText className="w-5 h-5" />, color: 'bg-violet-100 text-violet-600' },
  ]

  const dbOk = health?.database === 'ok' || health?.database === 'healthy'
  const redisOk =
    health?.redis === 'ok' || health?.redis === 'healthy' || health?.redis === 'unavailable'

  return (
    <div className="space-y-6 p-1" dir="rtl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">داشبورد اکونوژین</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            آخرین به‌روزرسانی: {lastRefresh.toLocaleTimeString('fa-IR')}
          </p>
        </div>
        <button
          onClick={load}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg border bg-background hover:bg-muted transition-colors text-sm disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          به‌روزرسانی
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          خطا در دریافت داده داشبورد. لطفاً دوباره تلاش کنید یا وضعیت احراز هویت را بررسی کنید.
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {statCards.map((s) => (
          <StatCard
            key={s.title}
            title={s.title}
            value={s.value as string | number}
            icon={s.icon}
            color={s.color}
            loading={loading}
            error={error}
          />
        ))}
      </div>

      <div>
        <h2 className="text-sm font-semibold text-muted-foreground mb-3">دسترسی سریع</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {navCards.map((c) => (
            <Link
              key={c.to}
              to={c.to}
              className="p-5 bg-card rounded-xl border shadow-sm hover:shadow-md transition-all hover:-translate-y-0.5 flex items-center gap-4 group"
            >
              <div className={`p-2.5 rounded-lg ${c.color} transition-transform group-hover:scale-110`}>
                {c.icon}
              </div>
              <div className="min-w-0">
                <h3 className="font-semibold text-sm">{c.label}</h3>
                <p className="text-xs text-muted-foreground mt-0.5 truncate">{c.desc}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>

      <div className="rounded-xl border bg-card p-4">
        <h2 className="text-sm font-semibold mb-3 flex items-center gap-2">
          <Shield className="w-4 h-4 text-green-500" /> وضعیت سرویس‌ها
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { name: 'API', ok: !error },
            { name: 'پایگاه داده', ok: health ? dbOk : !error },
            { name: 'Redis', ok: health ? redisOk : true },
            { name: 'مسیرهای API', ok: (health?.total_api_routes ?? 0) > 0 || !error },
          ].map((s) => (
            <div key={s.name} className="flex items-center gap-2 text-xs">
              {s.ok ? (
                <CheckCircle className="w-3.5 h-3.5 text-green-500 shrink-0" />
              ) : (
                <XCircle className="w-3.5 h-3.5 text-red-500 shrink-0" />
              )}
              <span className={s.ok ? 'text-foreground' : 'text-destructive'}>{s.name}</span>
            </div>
          ))}
        </div>
        {health && (
          <p className="text-xs text-muted-foreground mt-3">
            محیط: {health.environment} · کاربران ۲۴ساعت: {health.active_users_last_24h ?? '—'}
            {health.database_latency_ms != null && ` · تأخیر DB: ${health.database_latency_ms}ms`}
          </p>
        )}
      </div>
    </div>
  )
}

export default Dashboard
