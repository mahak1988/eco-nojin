/**
 * ============================================================================
 *  Dashboard — main landing page after login (i18n-aware, premium UI)
 * ============================================================================
 */

import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Activity,
  ArrowUpRight,
  Coins,
  FileText,
  Leaf,
  MapPin,
  TrendingUp,
  Waves,
} from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { ChartCard } from "@/components/shared/ChartCard";
import { PageHeader } from "@/components/shared/PageHeader";
import { StatCard } from "@/components/shared/StatCard";
import { StaggerContainer, StaggerItem } from "@/components/motion/StaggerChildren";
import { useAuth } from "@/hooks/useAuth";
import { useLanguage } from "@/hooks/useLanguage";
import { formatNumber } from "@/lib/i18n-utils";

interface QuickLink {
  to: string;
  titleKey: string;
  descriptionKey: string;
  icon: typeof Leaf;
  gradient: string;
}

const QUICK_LINKS: readonly QuickLink[] = [
  {
    to: "/carbon",
    titleKey: "nav.carbon",
    descriptionKey: "carbon.subtitle",
    icon: Leaf,
    gradient: "from-orange-500 to-rose-500",
  },
  {
    to: "/hydrology/watersheds",
    titleKey: "nav.watersheds",
    descriptionKey: "hydrology.subtitle",
    icon: Waves,
    gradient: "from-blue-500 to-cyan-500",
  },
  {
    to: "/soil",
    titleKey: "nav.soil",
    descriptionKey: "soil.subtitle",
    icon: Activity,
    gradient: "from-emerald-500 to-teal-500",
  },
  {
    to: "/documents",
    titleKey: "nav.documents",
    descriptionKey: "documents.subtitle",
    icon: FileText,
    gradient: "from-violet-500 to-indigo-500",
  },
] as const;

const ACTIVITY_DATA = [
  { day: "Sat", value: 42 },
  { day: "Sun", value: 58 },
  { day: "Mon", value: 51 },
  { day: "Tue", value: 67 },
  { day: "Wed", value: 74 },
  { day: "Thu", value: 63 },
  { day: "Fri", value: 81 },
];

const RECENT_ACTIVITY = [
  { id: 1, titleKey: "nav.carbon", timeKey: "dashboard.newReports", icon: Leaf, color: "text-orange-500", bg: "bg-orange-500/10" },
  { id: 2, titleKey: "nav.watersheds", timeKey: "dashboard.newRegions", icon: Waves, color: "text-blue-500", bg: "bg-blue-500/10" },
  { id: 3, titleKey: "nav.documents", timeKey: "dashboard.newReports", icon: FileText, color: "text-violet-500", bg: "bg-violet-500/10" },
] as const;

function QuickLinkCard({ link, index }: { link: QuickLink; index: number }): JSX.Element {
  const { t, dir } = useLanguage();
  const Icon = link.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 + index * 0.08, duration: 0.45 }}
      whileHover={{ y: -4 }}
    >
      <Link
        to={link.to}
        dir={dir}
        className="group flex h-full flex-col rounded-2xl border border-gray-200 bg-white p-5 shadow-sm transition hover:border-emerald-200 hover:shadow-lg dark:border-gray-800 dark:bg-gray-900 dark:hover:border-emerald-800"
      >
        <div className={`flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${link.gradient} text-white shadow-md`}>
          <Icon className="h-6 w-6" />
        </div>
        <h3 className="mt-4 text-base font-semibold text-gray-900 dark:text-white">{t(link.titleKey)}</h3>
        <p className="mt-1 flex-1 text-sm text-gray-600 dark:text-gray-400">{t(link.descriptionKey)}</p>
        <span className="mt-4 inline-flex items-center gap-1 text-xs font-semibold text-emerald-600 transition group-hover:gap-2 dark:text-emerald-400">
          {t("common.back")}
          <ArrowUpRight className="h-3.5 w-3.5" />
        </span>
      </Link>
    </motion.div>
  );
}

export function Dashboard(): JSX.Element {
  const { user } = useAuth();
  const { t, dir, language } = useLanguage();

  if (!user) return <></>;

  const hour = new Date().getHours();
  const greetingKey =
    hour < 12 ? "dashboard.greetingMorning" : hour < 18 ? "dashboard.greetingNoon" : "dashboard.greetingEvening";

  const stats = [
    {
      label: t("dashboard.sustainabilityScore"),
      value: `${formatNumber(78, language)}/100`,
      icon: TrendingUp,
      color: "text-emerald-600",
      bgColor: "bg-emerald-500/10",
      trend: 4,
    },
    {
      label: t("dashboard.activeReports"),
      value: formatNumber(12, language),
      icon: FileText,
      color: "text-blue-600",
      bgColor: "bg-blue-500/10",
      trend: 12,
    },
    {
      label: t("dashboard.monitoredRegions"),
      value: formatNumber(47, language),
      icon: MapPin,
      color: "text-violet-600",
      bgColor: "bg-violet-500/10",
      trend: 5,
    },
    {
      label: t("dashboard.ecoCoin"),
      value: formatNumber(1250, language),
      icon: Coins,
      color: "text-amber-600",
      bgColor: "bg-amber-500/10",
      trend: 18,
    },
  ];

  return (
    <div dir={dir} className="mx-auto max-w-7xl px-4 py-8">
      <PageHeader
        title={`${t(greetingKey)}، ${user.displayName} 👋`}
        description={t("dashboard.welcomeMessage")}
        icon={Activity}
        color="text-emerald-600"
      />

      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => (
          <StatCard key={stat.label} {...stat} delay={index * 0.08} />
        ))}
      </div>

      <div className="mb-8 grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <ChartCard
            title={t("dashboard.activityChart")}
            icon={Activity}
            iconColor="text-emerald-600"
            delay={0.15}
          >
            <p className="mb-4 text-sm text-gray-500 dark:text-gray-400">{t("dashboard.activityChartDesc")}</p>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={ACTIVITY_DATA} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                  <defs>
                    <linearGradient id="activityFill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#10b981" stopOpacity={0.35} />
                      <stop offset="100%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-800" />
                  <XAxis dataKey="day" tick={{ fontSize: 12 }} stroke="#94a3b8" />
                  <YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" />
                  <Tooltip
                    contentStyle={{
                      borderRadius: "12px",
                      border: "1px solid rgb(229 231 235)",
                      background: "rgba(255,255,255,0.95)",
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="#059669"
                    strokeWidth={2.5}
                    fill="url(#activityFill)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>
        </div>

        <ChartCard title={t("dashboard.recentActivity")} icon={FileText} iconColor="text-blue-600" delay={0.25}>
          <StaggerContainer className="space-y-3">
            {RECENT_ACTIVITY.map((item) => {
              const Icon = item.icon;
              return (
                <StaggerItem key={item.id}>
                  <div className="flex items-center gap-3 rounded-xl border border-gray-100 bg-gray-50/80 p-3 dark:border-gray-800 dark:bg-gray-900/60">
                    <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${item.bg}`}>
                      <Icon className={`h-5 w-5 ${item.color}`} />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-gray-900 dark:text-white">{t(item.titleKey)}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">{t(item.timeKey, { value: "2" })}</p>
                    </div>
                  </div>
                </StaggerItem>
              );
            })}
          </StaggerContainer>
          <Link
            to="/documents"
            className="mt-4 inline-flex items-center gap-1 text-sm font-semibold text-emerald-600 hover:text-emerald-700 dark:text-emerald-400"
          >
            {t("dashboard.viewAll")}
            <ArrowUpRight className="h-4 w-4" />
          </Link>
        </ChartCard>
      </div>

      <section className="mb-8">
        <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-white">{t("dashboard.quickAccess")}</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {QUICK_LINKS.map((link, index) => (
            <QuickLinkCard key={link.to} link={link} index={index} />
          ))}
        </div>
      </section>

      <motion.section
        initial={{ opacity: 0, y: 24 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
        className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-emerald-600 via-emerald-700 to-teal-800 p-8 text-white shadow-glow-lg"
      >
        <div className="pointer-events-none absolute -end-16 -top-16 h-48 w-48 rounded-full bg-white/10 blur-2xl" />
        <div className="pointer-events-none absolute -bottom-20 -start-10 h-56 w-56 rounded-full bg-teal-400/20 blur-3xl" />
        <div className="relative">
          <h2 className="text-xl font-bold sm:text-2xl">{t("dashboard.welcomeBannerTitle")}</h2>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-emerald-50 sm:text-base">
            {t("dashboard.welcomeBannerText")}
          </p>
          <Link
            to="/documents"
            className="mt-6 inline-flex items-center gap-2 rounded-xl bg-white px-5 py-2.5 text-sm font-semibold text-emerald-700 transition hover:bg-emerald-50 hover:shadow-lg"
          >
            {t("dashboard.viewReports")}
            <ArrowUpRight className="h-4 w-4" />
          </Link>
        </div>
      </motion.section>
    </div>
  );
}
