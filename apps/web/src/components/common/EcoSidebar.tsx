import * as React from "react"
import { cn } from "@/lib/utils"
import { Leaf, LayoutDashboard, Map, TrendingUp, MapPin, Users, Calendar, BarChart3, Beaker, Droplets, Sparkles, FileText, Settings, ChevronRight, Menu } from "lucide-react"

// Navigation groups from agri-moon - adapted for EcoNojin
const NAV_GROUPS = [
  {
    label: "داشبورد",
    items: [
      { to: "/dashboard", label: "نمای کلی", icon: LayoutDashboard },
      { to: "/gis-explorer", label: "GIS Explorer", icon: Map, badge: "فعال", badgeColor: "bg-green-500" },
      { to: "/production-analytics", label: "تحلیل‌های تولید", icon: TrendingUp },
    ],
  },
  {
    label: "عملیات",
    items: [
      { to: "/land-registry", label: "ثبت زمین", icon: MapPin },
      { to: "/farmers", label: "کشاورزان", icon: Users },
      { to: "/planting-seasons", label: "فصل‌های کاشت", icon: Calendar },
      { to: "/harvest-monitoring", label: "نظارت محصول", icon: BarChart3 },
    ],
  },
  {
    label: "منابع",
    items: [
      { to: "/fertilizer", label: "کود و تغذیه", icon: Beaker },
      { to: "/water-irrigation", label: "آب و آبیاری", icon: Droplets },
    ],
  },
  {
    label: "هوش مصنوعی",
    items: [
      { to: "/ai-insights", label: "دریافت‌های هوشمند", icon: Sparkles, badge: "AI", badgeColor: "bg-violet-500" },
      { to: "/reports", label: "گزارش‌ها", icon: FileText },
      { to: "/administration", label: "مدیریت", icon: Settings },
    ],
  },
]

export default function EcoSidebar() {
  const [collapsed, setCollapsed] = React.useState(false)

  return (
    <aside
      className={cn(
        "flex flex-col h-full bg-white dark:bg-gray-950 border-r border-gray-100 dark:border-gray-800 transition-all duration-300 shrink-0",
        collapsed ? "w-[60px]" : "w-[220px]",
      )}
    >
      {/* Logo + collapse toggle */}
      <div className="flex items-center border-b border-gray-100 dark:border-gray-800 shrink-0 px-4 py-4 justify-between">
        {collapsed ? (
          <div className="w-9 h-9 bg-green-700 rounded-xl flex items-center justify-center mx-auto">
            <Leaf className="w-4 h-4 text-white" />
          </div>
        ) : (
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-green-700 rounded-xl flex items-center justify-center shrink-0">
              <Leaf className="w-4 h-4 text-white" />
            </div>
            <div>
              <div className="text-sm font-bold text-gray-900 dark:text-white leading-none">EcoNojin</div>
              <div className="text-[10px] text-gray-400 mt-0.5 leading-none">کشاورزی هوشمند</div>
            </div>
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-400 transition-colors"
        >
          <Menu className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Season badge */}
      {!collapsed && (
        <div className="px-3 py-3 shrink-0">
          <div className="bg-green-50 dark:bg-green-950/40 rounded-xl px-3 py-2">
            <div className="text-[9px] text-green-600 dark:text-green-400 font-bold uppercase tracking-wider">فصل جاری</div>
            <div className="text-xs font-semibold text-green-800 dark:text-green-300 mt-0.5">۱۴۰۴ – فصل الف</div>
            <div className="text-[10px] text-green-600/70 dark:text-green-500">آذر ۱۴۰۴ – شهریور ۱۴۰۴</div>
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-2 pb-2">
        {collapsed ? (
          <div className="mt-2 space-y-1">
            {NAV_GROUPS.flatMap(g => g.items).map(({ to, icon: Icon }) => (
              <a
                key={to}
                href={to}
                className="flex items-center justify-center w-10 h-10 rounded-xl mx-auto transition-all text-gray-400 dark:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-700 dark:hover:text-gray-300"
              >
                <Icon className="w-4 h-4 shrink-0" />
              </a>
            ))}
          </div>
        ) : (
          <div className="space-y-4 mt-1">
            {NAV_GROUPS.map(group => (
              <div key={group.label}>
                <p className="text-[10px] font-bold text-gray-400 dark:text-gray-600 uppercase tracking-widest px-3 mb-1">
                  {group.label}
                </p>
                <div className="space-y-0.5">
                  {group.items.map(({ to, label, icon: Icon, badge, badgeColor }) => (
                    <a
                      key={to}
                      href={to}
                      className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-sm transition-all group text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800/60 hover:text-gray-800 dark:hover:text-gray-200"
                    >
                      <Icon className="w-4 h-4 shrink-0 text-gray-400 group-hover:text-gray-600" />
                      <span className="flex-1 truncate text-[13px]">{label}</span>
                      {badge && (
                        <span className={cn("text-[9px] font-bold text-white px-1.5 py-0.5 rounded-full leading-none", badgeColor)}>
                          {badge}
                        </span>
                      )}
                    </a>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </nav>
    </aside>
  )
}
