// apps/web/src/pages/DashboardPage.tsx — live science/runs + stats when API up
import { useMemo, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  LayoutDashboard, Users, Leaf, ArrowUpRight, ArrowDownRight,
  Activity, MapPin, Satellite, FlaskConical, BookOpen, ShieldCheck, Mountain,
} from "lucide-react";
import { getDashboardStats, getDashboardOverview } from "../lib/apiServices";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { AnimatedCounter } from "../components/eco/AnimatedCounter";
import { HealthWidget } from "../features/dashboard/HealthWidget";
import { DataSourceBadge } from "../components/ui/DataSourceBadge";
import { DataTable } from "../components/science/ScienceVisuals";
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
  science_runs: "اجراهای علمی اخیر",
  soil: "خاک / RothC",
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
  link_science: "فاز علمی",
  link_farms: "مزارع",
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
  science_runs: "Recent science runs",
  soil: "Soil / RothC",
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
  link_science: "Science",
  link_farms: "Farms",
};

const AR: typeof FA = { ...EN, title: "لوحة التحكم", subtitle: "نظرة عامة على أداء المنصة" };
const DASH_STR: Record<DashLang, typeof FA> = { fa: FA, en: EN, ar: AR };

const DEFAULT_KPIS = [
  { key: "users", icon: Users, value: 0, change: 0, color: "text-green-700", bg: "bg-green-50" },
  { key: "projects", icon: Activity, value: 0, change: 0, color: "text-blue-700", bg: "bg-blue-50" },
  { key: "carbon", icon: Leaf, value: 0, change: 0, color: "text-emerald-700", bg: "bg-emerald-50" },
  { key: "regions", icon: MapPin, value: 0, change: 0, color: "text-amber-700", bg: "bg-amber-50" },
];

const ACTIVITY_ICONS = [ShieldCheck, FlaskConical, Users, Satellite, ShieldCheck];

const QUICK_LINKS = [
  { key: "link_science", to: "/science", icon: FlaskConical },
  { key: "link_farms", to: "/farms", icon: Leaf },
  { key: "link_satellite", to: "/satellite", icon: Satellite },
  { key: "link_simulators", to: "/simulators", icon: FlaskConical },
  { key: "link_mrv", to: "/mrv", icon: ShieldCheck },
  { key: "link_education", to: "/education", icon: BookOpen },
  { key: "link_accounting", to: "/accounting", icon: Activity },
  { key: "link_admin", to: "/admin", icon: LayoutDashboard },
];

function Sparkline({ values, color }: { values: number[]; color: string }) {
  const W = 120, H = 32;
  if (!values.length) return null;
  const max = Math.max(...values), min = Math.min(...values);
  const range = max - min || 1;
  const pts = values.map((v, i) =>
    `${(i / Math.max(1, values.length - 1)) * W},${H - ((v - min) / range) * H}`
  ).join(" ");
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ height: 32 }} preserveAspectRatio="none">
      <polyline points={pts} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export default function DashboardPage() {
  const [apiSource, setApiSource] = useState<DataSource>("mock");
  const [overview, setOverview] = useState<Record<string, unknown> | null>(null);
  const [kpis, setKpis] = useState(DEFAULT_KPIS);

  useEffect(() => {
    getDashboardStats().then((r) => {
      setApiSource(r.source);
      if (r.source === "api" && r.data) {
        const d = r.data as Record<string, number>;
        setKpis([
          { key: "users", icon: Users, value: Number(d.totalUsers ?? d.users ?? 0), change: Number(d.usersChange ?? 0), color: "text-green-700", bg: "bg-green-50" },
          { key: "projects", icon: Activity, value: Number(d.totalProjects ?? d.projects ?? 0), change: Number(d.projectsChange ?? 0), color: "text-blue-700", bg: "bg-blue-50" },
          { key: "carbon", icon: Leaf, value: Number(d.carbonOffset ?? d.carbon ?? 0), change: Number(d.carbonChange ?? 0), color: "text-emerald-700", bg: "bg-emerald-50" },
          { key: "regions", icon: MapPin, value: Number(d.activeRegions ?? d.regions ?? 0), change: Number(d.regionsChange ?? 0), color: "text-amber-700", bg: "bg-amber-50" },
        ]);
      }
    });
    getDashboardOverview().then((r) => {
      if (r.source === "api") setOverview(r.data as Record<string, unknown>);
    });
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

  const runs = ((overview?.runs as Record<string, unknown>[]) || []).slice(0, 6);
  const soil = (overview?.soil_snapshot as { rothc?: { soc_final?: number; delta?: number } }) || {};
  const scienceOk = Boolean((overview?.science as { ok?: boolean })?.ok);

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
          <div className="flex items-center gap-2">
            {overview && (
              <span className={`rounded-full px-2.5 py-1 text-[11px] font-bold ${
                scienceOk ? "bg-emerald-50 text-emerald-800" : "bg-amber-50 text-amber-800"
              }`}>
                science {scienceOk ? "ok" : "…"}
              </span>
            )}
            <DataSourceBadge source={apiSource} />
          </div>
        </div>
      </SectionReveal>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-4">
        <div className="lg:col-span-1">
          <HealthWidget />
        </div>
        <div className="grid grid-cols-2 gap-4 lg:col-span-3 lg:grid-cols-3">
          {kpis.slice(0, 3).map((kpi, i) => {
            const label = s[`kpi_${kpi.key}` as keyof typeof s] as string;
            const up = kpi.change >= 0;
            const spark = [0, kpi.value * 0.4, kpi.value * 0.6, kpi.value * 0.75, kpi.value * 0.9, kpi.value];
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
                      values={spark}
                      color={kpi.color.includes("green") || kpi.color.includes("emerald") ? "#15803d" : "#1d4ed8"}
                    />
                  </div>
                </div>
              </SectionReveal>
            );
          })}
        </div>
      </div>

      {(runs.length > 0 || soil.rothc) && (
        <div className="grid gap-4 lg:grid-cols-3">
          {soil.rothc && (
            <div className="rounded-2xl border border-amber-200 bg-amber-50/40 p-4">
              <h2 className="mb-2 flex items-center gap-2 font-display text-lg text-stone-800">
                <Mountain className="h-5 w-5 text-amber-700" /> {s.soil}
              </h2>
              <p className="text-sm text-stone-700">
                SOC نهایی: <span className="font-mono font-bold">{soil.rothc.soc_final ?? "—"}</span> t C/ha
              </p>
              <p className="text-sm text-stone-600">
                Δ: <span className="font-mono">{soil.rothc.delta ?? "—"}</span>
              </p>
              <Link to="/science" className="mt-2 inline-block text-xs font-bold text-emerald-700">
                Science Lab →
              </Link>
            </div>
          )}
          <div className="rounded-2xl border border-stone-200 bg-white p-4 lg:col-span-2">
            <h2 className="mb-3 font-display text-lg text-stone-800">{s.science_runs}</h2>
            <DataTable
              columns={["ID", "Model", "Created"]}
              rows={runs.map((r) => [
                String(r.id ?? ""),
                String(r.model ?? ""),
                String(r.created_at ?? "").slice(0, 19),
              ])}
              maxHeight={220}
              numericCols={[0]}
            />
          </div>
        </div>
      )}

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
