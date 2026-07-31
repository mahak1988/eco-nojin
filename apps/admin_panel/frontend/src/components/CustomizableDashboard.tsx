import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Users, Settings, FileText, Activity, Shield, UserCheck, Grid3x3, Plus, GripVertical, Brain, Lightbulb, AlertTriangle } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell,
} from 'recharts';
import { fetchDashboard, fetchSystemHealth, DashboardData, SystemHealth } from '../api/adminApi';
import { useTheme } from '../contexts/ThemeContext';

interface DashboardWidget {
  id: string;
  type: 'stats' | 'chart' | 'recent-activity' | 'system-health' | 'quick-actions' | 'smart-recommendations' | 'intelligent-alerts';
  position: { x: number; y: number };
  size: { w: number; h: number };
  title: string;
  enabled: boolean;
}

const CustomizableDashboard: React.FC = () => {
  const { t } = useTranslation();
  const { themeColors } = useTheme();
  const [dashData, setDashData] = useState<DashboardData | null>(null);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const [widgets, setWidgets] = useState<DashboardWidget[]>(() => {
    const savedWidgets = localStorage.getItem('dashboard-widgets');
    if (savedWidgets) {
      return JSON.parse(savedWidgets);
    }
    
    // Default widgets
    return [
      {
        id: 'stats',
        type: 'stats',
        position: { x: 0, y: 0 },
        size: { w: 12, h: 2 },
        title: 'آمار کلیدی',
        enabled: true
      },
      {
        id: 'chart',
        type: 'chart',
        position: { x: 0, y: 1 },
        size: { w: 8, h: 4 },
        title: 'نمودار سیستم',
        enabled: true
      },
      {
        id: 'health',
        type: 'system-health',
        position: { x: 8, y: 1 },
        size: { w: 4, h: 4 },
        title: 'سلامت سیستم',
        enabled: true
      },
      {
        id: 'activity',
        type: 'recent-activity',
        position: { x: 0, y: 2 },
        size: { w: 12, h: 3 },
        title: 'فعالیت‌های اخیر',
        enabled: true
      },
      {
        id: 'recommendations',
        type: 'smart-recommendations',
        position: { x: 0, y: 3 },
        size: { w: 6, h: 4 },
        title: 'توصیه‌های هوشمند',
        enabled: true
      },
      {
        id: 'alerts',
        type: 'intelligent-alerts',
        position: { x: 6, y: 3 },
        size: { w: 6, h: 4 },
        title: 'هشدارهای هوشمند',
        enabled: true
      }
    ];
  });

  useEffect(() => {
    Promise.all([
      fetchDashboard(),
      fetchSystemHealth(),
    ])
      .then(([d, h]) => {
        setDashData(d);
        setHealth(h);
      })
      .catch((err) => setError(err?.message || 'Failed to load dashboard'))
      .finally(() => setLoading(false));
  }, []);

  // Save widgets to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('dashboard-widgets', JSON.stringify(widgets));
  }, [widgets]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-2">
          <div className="mx-auto text-red-500">
            <Activity className="w-12 h-12 mx-auto" />
          </div>
          <p className="text-red-600 font-medium">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 text-sm"
          >
            تلاش مجدد
          </button>
        </div>
      </div>
    );
  }

  if (!dashData) return null;

  const stats = [
    { label: 'کل کاربران', value: dashData.user_count.toLocaleString(), icon: Users, color: 'text-eco-600' },
    { label: 'کاربران فعال', value: dashData.active_user_count.toLocaleString(), icon: UserCheck, color: 'text-green-600' },
    { label: 'کاربران ادمین', value: dashData.superuser_count.toLocaleString(), icon: Shield, color: 'text-purple-600' },
    { label: 'تنظیمات', value: dashData.total_settings.toLocaleString(), icon: Settings, color: 'text-amber-600' },
    { label: 'لاگ‌های حسابرسی', value: dashData.total_audit_logs.toLocaleString(), icon: Activity, color: 'text-blue-600' },
    { label: 'گزارش‌ها', value: dashData.total_reports.toLocaleString(), icon: FileText, color: 'text-water-600' },
  ];

  const chartData = dashData ? [
    { name: 'کاربران', count: dashData.user_count },
    { name: 'فعال', count: dashData.active_user_count },
    { name: 'ادمین', count: dashData.superuser_count },
    { name: 'تنظیمات', count: dashData.total_settings },
    { name: 'لاگ‌ها', count: dashData.total_audit_logs },
    { name: 'گزارش‌ها', count: dashData.total_reports },
  ] : [];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82ca9d'];

  const renderWidget = (widget: DashboardWidget) => {
    switch (widget.type) {
      case 'stats':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {stats.map((stat) => (
              <div 
                key={stat.label} 
                className="rounded-xl border bg-card p-5 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-muted-foreground">{stat.label}</p>
                  <stat.icon className={`w-5 h-5 ${stat.color}`} />
                </div>
                <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
              </div>
            ))}
          </div>
        );
      
      case 'chart':
        return (
          <div className="rounded-xl border bg-card p-6 shadow-sm">
            <h2 className="font-semibold mb-4">نمودار سیستم</h2>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="name" className="text-xs" />
                <YAxis className="text-xs" />
                <Tooltip
                  contentStyle={{
                    borderRadius: '8px',
                    border: '1px solid hsl(var(--border))',
                    background: 'hsl(var(--card))',
                  }}
                />
                <Bar dataKey="count" fill={themeColors.primary} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        );
      
      case 'system-health':
        return (
          <div className="rounded-xl border bg-card p-6 shadow-sm">
            <h2 className="font-semibold mb-4">سلامت سیستم</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                <span className="text-sm">پایگاه داده</span>
                <span className={`flex items-center gap-2 text-sm font-medium ${health?.database === 'healthy' ? 'text-green-600' : 'text-red-600'}`}>
                  <span className={`w-2 h-2 rounded-full ${health?.database === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`} />
                  {health?.database}
                  {health?.database_latency_ms !== null && <span className="text-muted-foreground text-xs">({health?.database_latency_ms}ms)</span>}
                </span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                <span className="text-sm">ردیس</span>
                <span className="flex items-center gap-2 text-sm text-muted-foreground">
                  <span className="w-2 h-2 rounded-full bg-gray-400" />
                  {health?.redis}
                </span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                <span className="text-sm">پایتون</span>
                <span className="text-sm font-mono">{health?.python_version}</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                <span className="text-sm">مسیرهای API</span>
                <span className="text-sm font-medium">{health?.total_api_routes}</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                <span className="text-sm">فعال (۲۴ ساعت)</span>
                <span className="text-sm font-medium">{health?.active_users_last_24h} کاربر</span>
              </div>
            </div>
          </div>
        );
      
      case 'recent-activity':
        return (
          <div className="rounded-xl border bg-card p-6 shadow-sm">
            <h2 className="font-semibold mb-4">فعالیت‌های اخیر</h2>
            <div className="space-y-3">
              {dashData.total_audit_logs > 0 ? (
                <>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                    <div className="w-2 h-2 rounded-full bg-eco-500" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">{dashData.total_audit_logs.toLocaleString()} رویداد حسابرسی ثبت شده</p>
                      <p className="text-xs text-muted-foreground">سیستم به طور فعال لاگ‌گذاری می‌کند</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                    <div className="w-2 h-2 rounded-full bg-blue-500" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">{dashData.total_reports} گزارش تولید شده</p>
                      <p className="text-xs text-muted-foreground">در بخش گزارش‌ها در دسترس است</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                    <div className="w-2 h-2 rounded-full bg-amber-500" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">{dashData.total_settings} تنظیمات سیستمی پیکربندی شده</p>
                      <p className="text-xs text-muted-foreground">در بخش تنظیمات مدیریت می‌شوند</p>
                    </div>
                  </div>
                </>
              ) : (
                <p className="text-muted-foreground text-sm">فعالیت اخیری وجود ندارد</p>
              )}
            </div>
          </div>
        );
      
      case 'smart-recommendations':
        return (
          <div className="rounded-xl border bg-card p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <Lightbulb className="w-5 h-5 text-primary" />
              <h2 className="font-semibold">توصیه‌های هوشمند</h2>
            </div>
            <div className="space-y-3">
              <div className="flex items-start gap-3 p-3 rounded-lg bg-blue-50 border border-blue-200">
                <div className="flex-shrink-0 pt-1">
                  <span className="inline-flex items-center rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800">
                    بالا
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium truncate">نیاز به مقیاس‌بندی عملکرد</h3>
                  <p className="text-sm text-muted-foreground truncate">سیستم شما بیش از 1000 کاربر فعال دارد، پیشنهاد می‌شود تنظیمات عملکرد را بررسی کنید</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 rounded-lg bg-yellow-50 border border-yellow-200">
                <div className="flex-shrink-0 pt-1">
                  <span className="inline-flex items-center rounded-full bg-yellow-100 px-2.5 py-0.5 text-xs font-medium text-yellow-800">
                    متوسط
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium truncate">مدیریت بازنشانی لاگ</h3>
                  <p className="text-sm text-muted-foreground truncate">حجم بالای لاگ‌ها ممکن است فضای ذخیره‌سازی را مصرف کند</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 rounded-lg bg-green-50 border border-green-200">
                <div className="flex-shrink-0 pt-1">
                  <span className="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800">
                    کم
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium truncate">بینش هوشمند تحلیلگر سیستم</h3>
                  <p className="text-sm text-muted-foreground truncate">تحلیل هوش مصنوعی از رفتار سیستم نشان می‌دهد...</p>
                </div>
              </div>
            </div>
          </div>
        );
      
      case 'intelligent-alerts':
        return (
          <div className="rounded-xl border bg-card p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="w-5 h-5 text-orange-500" />
              <h2 className="font-semibold">هشدارهای هوشمند</h2>
            </div>
            <div className="space-y-3">
              <div className="flex items-start gap-3 p-3 rounded-lg bg-red-50 border border-red-200">
                <div className="flex-shrink-0 pt-1">
                  <span className="inline-flex items-center rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-800">
                    خطایی
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium truncate">مشکل سلامت پایگاه داده</h3>
                  <p className="text-sm text-muted-foreground truncate">وضعیت پایگاه داده: ناسالم</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 rounded-lg bg-yellow-50 border border-yellow-200">
                <div className="flex-shrink-0 pt-1">
                  <span className="inline-flex items-center rounded-full bg-yellow-100 px-2.5 py-0.5 text-xs font-medium text-yellow-800">
                    هشدار
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium truncate">تاخیر بالا در پایگاه داده</h3>
                  <p className="text-sm text-muted-foreground truncate">تاخیر فعلی: 250ms</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 rounded-lg bg-blue-50 border border-blue-200">
                <div className="flex-shrink-0 pt-1">
                  <span className="inline-flex items-center rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800">
                    اطلاعات
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium truncate">تعداد بالای کاربران</h3>
                  <p className="text-sm text-muted-foreground truncate">کل کاربران: 10,500</p>
                </div>
              </div>
            </div>
          </div>
        );
      
      default:
        return <div>ویجت ناشناخته</div>;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">داشبورد مدیریت</h1>
          <p className="text-muted-foreground">
            بررسی کلی سیستم &bull; محیط: <span className="font-mono text-xs bg-muted px-2 py-0.5 rounded">{health?.environment || 'ناشناخته'}</span>
          </p>
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={() => setEditing(!editing)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
              editing 
                ? 'bg-green-100 text-green-800 border border-green-300' 
                : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
            }`}
          >
            <Grid3x3 className="w-4 h-4" />
            {editing ? 'پایان ویرایش' : 'ویرایش داشبورد'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-4">
        {widgets
          .filter(w => w.enabled)
          .sort((a, b) => a.position.y - b.position.y || a.position.x - b.position.x)
          .map(widget => (
            <div 
              key={widget.id}
              className={`col-span-${widget.size.w} row-span-${widget.size.h} ${
                editing ? 'border-2 border-dashed border-primary/50 rounded-lg p-4' : ''
              }`}
            >
              {editing && (
                <div className="mb-2 flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <GripVertical className="w-4 h-4 text-muted-foreground cursor-move" />
                    <span className="text-sm font-medium">{widget.title}</span>
                  </div>
                  <div className="flex gap-1">
                    <button 
                      onClick={() => {
                        setWidgets(w => 
                          w.map(wg => wg.id === widget.id ? { ...wg, enabled: !wg.enabled } : wg)
                        );
                      }}
                      className="text-xs px-2 py-1 rounded bg-muted hover:bg-muted/80"
                    >
                      {widget.enabled ? 'غیرفعال' : 'فعال'}
                    </button>
                  </div>
                </div>
              )}
              
              <div className={editing ? 'opacity-70' : ''}>
                {renderWidget(widget)}
              </div>
            </div>
          ))}
      </div>

      {editing && (
        <div className="mt-6 p-4 border rounded-lg bg-muted/30">
          <h3 className="font-medium mb-2">افزودن ویجت جدید</h3>
          <div className="flex flex-wrap gap-2">
            <button 
              onClick={() => {
                const newWidget: DashboardWidget = {
                  id: `widget-${Date.now()}`,
                  type: 'smart-recommendations',
                  position: { x: 0, y: Math.max(...widgets.map(w => w.position.y)) + 1 },
                  size: { w: 6, h: 3 },
                  title: 'توصیه‌های هوشمند',
                  enabled: true
                };
                setWidgets([...widgets, newWidget]);
              }}
              className="flex items-center gap-2 px-3 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 text-sm"
            >
              <Lightbulb className="w-4 h-4" />
              توصیه‌های هوشمند
            </button>
            <button 
              onClick={() => {
                const newWidget: DashboardWidget = {
                  id: `widget-${Date.now()}`,
                  type: 'intelligent-alerts',
                  position: { x: 6, y: Math.max(...widgets.map(w => w.position.y)) + 1 },
                  size: { w: 6, h: 3 },
                  title: 'هشدارهای هوشمند',
                  enabled: true
                };
                setWidgets([...widgets, newWidget]);
              }}
              className="flex items-center gap-2 px-3 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 text-sm"
            >
              <AlertTriangle className="w-4 h-4" />
              هشدارهای هوشمند
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CustomizableDashboard;