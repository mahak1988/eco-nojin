// apps/web/src/pages/DashboardPage.tsx
import { useMemo, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  LayoutDashboard, Users, Leaf, ArrowUpRight, ArrowDownRight,
  Activity, MapPin, Satellite, FlaskConical, BookOpen, ShieldCheck,
} from "lucide-react";
import { getDashboardStats } from "../lib/apiServices";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { AnimatedCounter } from "../components/eco/AnimatedCounter";
import { HealthWidget } from "../features/dashboard/HealthWidget";
import { DataSourceBadge } from "../components/ui/DataSourceBadge";
import type { DataSource } from "../types/common";

type DashLang = "fa" | "en" | "ar";

const FA = {
  title: "داشبورد",
  subtitle: "نمای کلی عملکرد پلتفرم اکونوژین",
  kpi_users: "کاربران فعال",
  kpi_projects: "پروژه‌ها",
  kpi_carbon: "کربن جبران‌شده",
  kpi_regions: "منطقه‌های فعال",
  carbon_unit: "تن CO₂e",
  recent: "فعالیت‌های اخیر",
  quick_links: "دسترسی سریع",
  act1: "گزارش MRV سه‌ماهه منتشر شد",
  act2: "پایلوت کشاورزی اصفهان به ۴۵٪ پیشرفت رسید",
  act3: "۱۲۰ کاربر جدید در شبکه ثبت‌نام کردند",
  act4: "تصویر ماهواره‌ای جدید دریافت شد",
  act5: "سیاست حفاظت داده به‌روزرسانی شد",
  time1: "۲ ساعت پیش", time2: "۵ ساعت پیش", time3: "دیروز", time4: "۲ روز پیش", time5: "۳ روز پیش",
  link_satellite: "تصاویر ماهواره‌ای",
  link_simulators: "شبیه‌سازها",
  link_mrv: "MRV",
  link_reports: "گزارش‌ها",
  link_education: "آموزش",
  link_risks: "ریسک‌ها",
  link_admin: "پنل ادمین",
  link_accounting: "حسابداری",
};

const EN: typeof FA = {
  title: "Dashboard",
  subtitle: "EcoNojin platform performance overview",
  kpi_users: "Active Users",
  kpi_projects: "Projects",
  kpi_carbon: "Carbon Offset",
  kpi_regions: "Active Regions",
  carbon_unit: "tCO₂e",
  recent: "Recent Activity",
  quick_links: "Quick Access",
  act1: "Q3 MRV report published",
  act2: "Isfahan farming pilot reached 45% progress",
  act3: "120 new users joined the network",
  act4: "New satellite imagery received",
  act5: "Data protection policy updated",
  time1: "2 hours ago", time2: "5 hours ago", time3: "Yesterday", time4: "2 days ago", time5: "3 days ago",
  link_satellite: "Satellite Imagery",
  link_simulators: "Simulators",
  link_mrv: "MRV",
  link_reports: "Reports",
  link_education: "Education",
  link_risks: "Risks",
  link_admin: "Admin panel",
  link_accounting: "Accounting",
};

const AR: typeof FA = { ...EN, title: "لوحة التحكم", subtitle: "نظرة عامة على أداء المنصة" };

const DASH_STR: Record<DashLang, typeof FA> = { fa: FA, en: EN, ar: AR };

const KPIS = [
  { key: "users", icon: Users, value: 4256, change: 12.5, color: "text-green-700", bg: "bg-green-50" },
  { key: "projects", icon: Activity, value: 38, change: 8.2, color: "text-blue-700", bg: "bg-blue-50" },
  { key: "carbon", icon: Leaf, value: 4820, change: 15.3, color: "text-emerald-700", bg: "bg-emerald-50" },
  { key: "regions", icon: MapPin, value: 6, change: 2, color: "text-amber-700", bg: "bg-amber-50" },
];

const ACTIVITY_ICONS = [ShieldCheck, FlaskConical, Users, Satellite, ShieldCheck];

const QUICK_LINKS = [
  { key: "link_satellite", to: "/satellite", icon: Satellite },
  { key: "link_simulators", to: "/simulators", icon: FlaskConical },
  { key: "link_mrv", to: "/mrv", icon: ShieldCheck },
  { key: "link_education", to: "/education", icon: BookOpen },
  { key: "link_accounting", to: "/accounting", icon: Activity },
  { key: "link_admin", to: "/admin", icon: LayoutDashboard },
];

function Sparkline({ values, color }: { values: number[]; color: string }) {
  const W = 120, H = 32;
  const max = Math.max(...values), min = Math.min(...values);
  const range = max - min || 1;
  const pts = values.map((v, i) =>
    `${(i / (values.length - 1)) * W},${H - ((v - min) / range) * H}`
  ).join(" ");
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ height: 32 }} preserveAspectRatio="none">
      <polyline points={pts} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

const SPARK_DATA: Record<string, number[]> = {
  users: [3200, 3400, 3600, 3800, 4000, 4256],
  projects: [28, 30, 32, 34, 36, 38],
  carbon: [3200, 3600, 3900, 4200, 4500, 4820],
  regions: [3, 4, 4, 5, 5, 6],
};

export default function DashboardPage() {
  const [apiSource, setApiSource] = useState<DataSource>("mock");
  useEffect(() => {
    getDashboardStats().then((r) => setApiSource(r.source));
  }, []);
  const { lang } = useLang();
  const s = DASH_STR[(lang as DashLang) in DASH_STR ? (lang as DashLang) : "en"];
  const locale = lang === "fa" ? "fa-IR" : lang === "ar" ? "ar-EG" : "en-US";

  const activities = useMemo(
    () => [
      { text: s.act1, time: s.time1 },
      { text: s.act2, time: s.time2 },
      { text: s.act3, time: s.time3 },
      { text: s.act4, time: s.time4 },
      { text: s.act5, time: s.time5 },
    ],
    [s],
  );

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
      <SectionReveal>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-xl bg-green-50 ring-1 ring-green-600/15">
              <LayoutDashboard className="h-5 w-5 text-green-700" />
            </div>
            <div>
              <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
              <p className="mt-0.5 text-stone-600">{s.subtitle}</p>
            </div>
          </div>
          <DataSourceBadge source={apiSource} />
        </div>
      </SectionReveal>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-4">
        <div className="lg:col-span-1">
          <HealthWidget />
        </div>
        <div className="grid grid-cols-2 gap-4 lg:col-span-3 lg:grid-cols-3">
          {KPIS.slice(0, 3).map((kpi, i) => {
            const label = s[`kpi_${kpi.key}` as keyof typeof s] as string;
            const up = kpi.change >= 0;
            return (
              <SectionReveal key={kpi.key} delay={i * 70}>
                <div className={`rounded-2xl border border-stone-200/80 p-4 shadow-sm ${kpi.bg}`}>
                  <div className="flex items-center justify-between">
                    <kpi.icon className={`h-5 w-5 ${kpi.color}`} />
                    <span className={`inline-flex items-center gap-0.5 text-xs font-bold ${up ? "text-green-700" : "text-red-700"}`}>
                      {up ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
                      {Math.abs(kpi.change).toLocaleString(locale)}%
                    </span>
                  </div>
                  <p className={`mt-2 font-display text-2xl font-black tabular-nums ${kpi.color}`}>
                    <AnimatedCounter end={kpi.value} />
                    {kpi.key === "carbon" && (
                      <span className="ms-1 text-xs font-bold text-stone-500">{s.carbon_unit}</span>
                    )}
                  </p>
                  <p className="mt-0.5 text-xs font-medium text-stone-600">{label}</p>
                  <div className="mt-2">
                    <Sparkline
                      values={SPARK_DATA[kpi.key]}
                      color={kpi.color.includes("green") || kpi.color.includes("emerald") ? "#15803d" : "#1d4ed8"}
                    />
                  </div>
                </div>
              </SectionReveal>
            );
          })}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <SectionReveal delay={100} className="lg:col-span-2">
          <div className="rounded-2xl border border-stone-200/80 bg-white p-5 shadow-sm">
            <h2 className="mb-4 font-display text-lg text-stone-800">{s.recent}</h2>
            <div className="space-y-3">
              {activities.map((a, i) => {
                const Icon = ACTIVITY_ICONS[i];
                return (
                  <div key={i} className="flex items-start gap-3 rounded-xl bg-stone-50 p-3">
                    <span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-green-100 text-green-700">
                      <Icon className="h-4 w-4" />
                    </span>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-stone-800">{a.text}</p>
                      <p className="mt-0.5 text-xs text-stone-500">{a.time}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </SectionReveal>

        <SectionReveal delay={120}>
          <div className="rounded-2xl border border-stone-200/80 bg-white p-5 shadow-sm">
            <h2 className="mb-4 font-display text-lg text-stone-800">{s.quick_links}</h2>
            <div className="grid grid-cols-2 gap-2">
              {QUICK_LINKS.map((l) => (
                <Link
                  key={l.key}
                  to={l.to}
                  className="flex flex-col items-center gap-2 rounded-xl border border-stone-200 p-3 text-center transition-all hover:-translate-y-0.5 hover:border-green-300 hover:bg-green-50/50 hover:shadow-sm"
                >
                  <l.icon className="h-5 w-5 text-green-700" />
                  <span className="text-xs font-bold text-stone-700">{s[l.key as keyof typeof s] as string}</span>
                </Link>
              ))}
            </div>
          </div>
        </SectionReveal>
      </div>
    </div>
  );
}
