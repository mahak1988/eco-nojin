/**
 * ============================================================================
 *  Dashboard — main landing page after login (i18n-aware)
 * ============================================================================
 */

import { Link } from "react-router-dom";

import { useAuth } from "@/hooks/useAuth";
import { useLanguage } from "@/hooks/useLanguage";
import { formatNumber } from "@/lib/i18n-utils";

// ---------------------------------------------------------------------------
// Quick-link cards
// ---------------------------------------------------------------------------

interface QuickLink {
  to: string;
  titleKey: string;
  descriptionKey: string;
  icon: string;
  gradient: string;
}

const QUICK_LINKS: readonly QuickLink[] = [
  {
    to: "/carbon",
    titleKey: "nav.carbon",
    descriptionKey: "carbon.subtitle",
    icon: "🏭",
    gradient: "from-red-500 to-orange-500",
  },
  {
    to: "/hydrology/watersheds",
    titleKey: "nav.watersheds",
    descriptionKey: "hydrology.subtitle",
    icon: "💧",
    gradient: "from-blue-500 to-cyan-500",
  },
  {
    to: "/soil",
    titleKey: "nav.soil",
    descriptionKey: "soil.subtitle",
    icon: "🌱",
    gradient: "from-emerald-500 to-teal-500",
  },
  {
    to: "/documents",
    titleKey: "nav.documents",
    descriptionKey: "documents.subtitle",
    icon: "📄",
    gradient: "from-purple-500 to-indigo-500",
  },
] as const;

function QuickLinkCard({ link }: { link: QuickLink }): JSX.Element {
  const { t, dir } = useLanguage();
  return (
    <Link
      to={link.to}
      dir={dir}
      className="group rounded-xl border border-gray-200 bg-white p-5 transition hover:border-emerald-200 hover:shadow-md"
    >
      <div className={`flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${link.gradient} text-2xl`}>
        {link.icon}
      </div>
      <h3 className="mt-4 text-base font-semibold text-gray-900">{t(link.titleKey)}</h3>
      <p className="mt-1 text-sm text-gray-600">{t(link.descriptionKey)}</p>
      <p className="mt-3 text-xs font-medium text-emerald-600 transition group-hover:translate-x-1">
        {t("common.back")} ←
      </p>
    </Link>
  );
}

// ---------------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------------

export function Dashboard(): JSX.Element {
  const { user } = useAuth();
  const { t, dir, language } = useLanguage();

  if (!user) return <></>;

  const hour = new Date().getHours();
  const greetingKey =
    hour < 12 ? "dashboard.greetingMorning" : hour < 18 ? "dashboard.greetingNoon" : "dashboard.greetingEvening";

  // Mock stats — replace with real data via useApi
  const stats = [
    { labelKey: "dashboard.sustainabilityScore", value: formatNumber(78, language), suffix: "/100", trendKey: "dashboard.pointsUp", trendValue: "4" },
    { labelKey: "dashboard.activeReports", value: formatNumber(12, language), suffix: "", trendKey: "dashboard.newReports", trendValue: "3" },
    { labelKey: "dashboard.monitoredRegions", value: formatNumber(47, language), suffix: "", trendKey: "dashboard.newRegions", trendValue: "2" },
    { labelKey: "dashboard.ecoCoin", value: formatNumber(1250, language), suffix: "ECO", trendKey: "dashboard.pointsUp", trendValue: "250" },
  ];

  return (
    <div dir={dir} className="mx-auto max-w-7xl px-4 py-8">
      {/* Greeting */}
      <header className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          {t(greetingKey)}، {user.displayName} 👋
        </h1>
        <p className="mt-1 text-sm text-gray-600">{t("dashboard.welcomeMessage")}</p>
      </header>

      {/* Stats summary */}
      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.labelKey} className="rounded-xl border border-gray-200 bg-white p-5">
            <p className="text-sm text-gray-600">{t(stat.labelKey)}</p>
            <p className="mt-2 text-2xl font-bold text-gray-900">
              {stat.value}
              {stat.suffix && <span className="ms-1 text-sm font-normal text-gray-500">{stat.suffix}</span>}
            </p>
            <p className="mt-1 text-xs text-emerald-600">
              {t(stat.trendKey, { value: stat.trendValue })}
            </p>
          </div>
        ))}
      </div>

      {/* Quick links */}
      <section>
        <h2 className="mb-4 text-lg font-semibold text-gray-900">{t("dashboard.quickAccess")}</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {QUICK_LINKS.map((link) => (
            <QuickLinkCard key={link.to} link={link} />
          ))}
        </div>
      </section>

      {/* Welcome banner */}
      <section className="mt-8 rounded-2xl bg-gradient-to-br from-emerald-600 to-teal-700 p-8 text-white">
        <h2 className="text-xl font-bold">{t("dashboard.welcomeBannerTitle")}</h2>
        <p className="mt-2 max-w-2xl text-sm leading-7 text-emerald-50">
          {t("dashboard.welcomeBannerText")}
        </p>
        <Link
          to="/documents"
          className="mt-5 inline-block rounded-lg bg-white px-5 py-2.5 text-sm font-semibold text-emerald-700 transition hover:bg-emerald-50"
        >
          {t("dashboard.viewReports")}
        </Link>
      </section>
    </div>
  );
}
