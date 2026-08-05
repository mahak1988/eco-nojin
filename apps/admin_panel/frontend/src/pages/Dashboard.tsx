import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Users, Settings, FileText, Activity, Shield, BarChart3,
  Brain, Droplets, Cloud, AlertTriangle, Sprout, TrendingUp,
  Map, Zap, RefreshCw, CheckCircle, XCircle, Loader2
} from 'lucide-react';

// ── Types ────────────────────────────────────────────────────────────────────

interface DashboardStats {
  total_farms?: number;
  total_crops?: number;
  active_users?: number;
  water_usage_m3?: number;
  risk_alerts?: number;
  [key: string]: unknown;
}

interface DashboardOverview {
  farms_summary?: { total: number; active: number };
  weather_status?: string;
  recent_alerts?: Array<{ message: string; severity: string }>;
  [key: string]: unknown;
}

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
  loading?: boolean;
  error?: boolean;
}

// ── StatCard ─────────────────────────────────────────────────────────────────

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
);

// ── AlertBadge ────────────────────────────────────────────────────────────────

const severityClass: Record<string, string> = {
  high: 'bg-red-100 text-red-700 border-red-200',
  medium: 'bg-amber-100 text-amber-700 border-amber-200',
  low: 'bg-green-100 text-green-700 border-green-200',
};

// ── Main Dashboard ────────────────────────────────────────────────────────────

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const [overviewLoading, setOverviewLoading] = useState(true);
  const [statsError, setStatsError] = useState(false);
  const [overviewError, setOverviewError] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  const BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

  const fetchStats = async () => {
    setStatsLoading(true);
    setStatsError(false);
    try {
      const r = await fetch(`${BASE}/dashboard/stats`, { credentials: 'include' });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      setStats(await r.json());
    } catch {
      setStatsError(true);
    } finally {
      setStatsLoading(false);
    }
  };

  const fetchOverview = async () => {
    setOverviewLoading(true);
    setOverviewError(false);
    try {
      const r = await fetch(`${BASE}/dashboard/overview`, { credentials: 'include' });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      setOverview(await r.json());
    } catch {
      setOverviewError(true);
    } finally {
      setOverviewLoading(false);
    }
  };

  const refresh = () => {
    fetchStats();
    fetchOverview();
    setLastRefresh(new Date());
  };

  useEffect(() => {
    fetchStats();
    fetchOverview();
  }, []);

  const navCards = [
    { to: '/users', label: 'مدیریت کاربران', desc: 'مشاهده و مدیریت کاربران سیستم', icon: <Users className="w-5 h-5" />, color: 'bg-blue-100 text-blue-600' },
    { to: '/farms', label: 'مزارع', desc: 'مدیریت اطلاعات مزارع', icon: <Map className="w-5 h-5" />, color: 'bg-emerald-100 text-emerald-600' },
    { to: '/crops', label: 'محصولات', desc: 'مدیریت انواع محصولات کشاورزی', icon: <Sprout className="w-5 h-5" />, color: 'bg-lime-100 text-lime-600' },
    { to: '/water', label: 'مدیریت آب', desc: 'پایش منابع و مصرف آب', icon: <Droplets className="w-5 h-5" />, color: 'bg-cyan-100 text-cyan-600' },
    { to: '/weather', label: 'آب‌وهوا', desc: 'پیش‌بینی و هشدارهای آب‌وهوایی', icon: <Cloud className="w-5 h-5" />, color: 'bg-sky-100 text-sky-600' },
    { to: '/risks', label: 'ارزیابی ریسک', desc: 'پیش‌بینی و مدیریت ریسک', icon: <AlertTriangle className="w-5 h-5" />, color: 'bg-red-100 text-red-600' },
    { to: '/economics', label: 'اقتصاد سبز', desc: 'تحلیل هزینه-فایده و EcoCoin', icon: <TrendingUp className="w-5 h-5" />, color: 'bg-yellow-100 text-yellow-600' },
    { to: '/intelligent-analytics', label: 'تحلیل هوشمند', desc: 'تحلیل‌های پیشرفته با هوش مصنوعی', icon: <Brain className="w-5 h-5" />, color: 'bg-indigo-100 text-indigo-600' },
    { to: '/reports', label: 'گزارش‌ها', desc: 'گزارش‌های سیستم و عملکرد', icon: <BarChart3 className="w-5 h-5" />, color: 'bg-violet-100 text-violet-600' },
    { to: '/audit-logs', label: 'لاگ حسابرسی', desc: 'مشاهده فعالیت‌های سیستم', icon: <Activity className="w-5 h-5" />, color: 'bg-purple-100 text-purple-600' },
    { to: '/content-management', label: 'مدیریت محتوا', desc: 'مدیریت صفحات، مقالات و محصولات', icon: <FileText className="w-5 h-5" />, color: 'bg-amber-100 text-amber-600' },
    { to: '/settings', label: 'تنظیمات', desc: 'پیکربندی سیستم', icon: <Settings className="w-5 h-5" />, color: 'bg-gray-100 text-gray-600' },
  ];

  const statCards = [
    {
      title: 'مزارع ثبت‌شده',
      value: stats?.total_farms ?? stats?.farms ?? '—',
      icon: <Map className="w-5 h-5" />,
      color: 'bg-emerald-100 text-emerald-600',
    },
    {
      title: 'محصولات',
      value: stats?.total_crops ?? stats?.crops ?? '—',
      icon: <Sprout className="w-5 h-5" />,
      color: 'bg-lime-100 text-lime-600',
    },
    {
      title: 'کاربران فعال',
      value: stats?.active_users ?? stats?.users ?? '—',
      icon: <Users className="w-5 h-5" />,
      color: 'bg-blue-100 text-blue-600',
    },
    {
      title: 'هشدارهای ریسک',
      value: stats?.risk_alerts ?? stats?.alerts ?? '—',
      icon: <AlertTriangle className="w-5 h-5" />,
      color: 'bg-red-100 text-red-600',
    },
    {
      title: 'مصرف آب (m³)',
      value: stats?.water_usage_m3 != null
        ? Number(stats.water_usage_m3).toLocaleString('fa-IR')
        : '—',
      icon: <Droplets className="w-5 h-5" />,
      color: 'bg-cyan-100 text-cyan-600',
    },
    {
      title: 'وضعیت سیستم',
      value: statsError ? 'خطا' : statsLoading ? '...' : 'فعال',
      icon: statsError ? <XCircle className="w-5 h-5" /> : <CheckCircle className="w-5 h-5" />,
      color: statsError ? 'bg-red-100 text-red-600' : 'bg-green-100 text-green-600',
    },
  ];

  const alerts = overview?.recent_alerts ?? [];

  return (
    <div className="space-y-6 p-1" dir="rtl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">داشبورد اکونوژین</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            آخرین به‌روزرسانی: {lastRefresh.toLocaleTimeString('fa-IR')}
          </p>
        </div>
        <button
          onClick={refresh}
          disabled={statsLoading || overviewLoading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg border bg-background hover:bg-muted transition-colors text-sm disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${(statsLoading || overviewLoading) ? 'animate-spin' : ''}`} />
          به‌روزرسانی
        </button>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {statCards.map((s) => (
          <StatCard
            key={s.title}
            title={s.title}
            value={s.value as string | number}
            icon={s.icon}
            color={s.color}
            loading={statsLoading}
            error={statsError}
          />
        ))}
      </div>

      {/* Alerts */}
      {!overviewLoading && !overviewError && alerts.length > 0 && (
        <div className="rounded-xl border bg-card p-4 space-y-2">
          <h2 className="text-sm font-semibold flex items-center gap-2">
            <Zap className="w-4 h-4 text-amber-500" /> هشدارهای اخیر
          </h2>
          <div className="space-y-1">
            {alerts.slice(0, 5).map((a, i) => (
              <div
                key={i}
                className={`text-xs px-3 py-1.5 rounded-lg border ${severityClass[a.severity] ?? severityClass.low}`}
              >
                {a.message}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Navigation Cards */}
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

      {/* System Health */}
      <div className="rounded-xl border bg-card p-4">
        <h2 className="text-sm font-semibold mb-3 flex items-center gap-2">
          <Shield className="w-4 h-4 text-green-500" /> وضعیت سرویس‌ها
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { name: 'API', ok: !statsError },
            { name: 'پایگاه داده', ok: !overviewError },
            { name: 'آب‌وهوا (Open-Meteo)', ok: true },
            { name: 'امنیت', ok: true },
          ].map((s) => (
            <div key={s.name} className="flex items-center gap-2 text-xs">
              {s.ok
                ? <CheckCircle className="w-3.5 h-3.5 text-green-500 shrink-0" />
                : <XCircle className="w-3.5 h-3.5 text-red-500 shrink-0" />}
              <span className={s.ok ? 'text-foreground' : 'text-destructive'}>{s.name}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
