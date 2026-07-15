/**
 * ============================================================================
 *  AboutUs — about page with team + mission + timeline (i18n-aware)
 * ============================================================================
 */

import { Link } from "react-router-dom";

import { useLanguage } from "@/hooks/useLanguage";
import { formatNumber } from "@/lib/i18n-utils";

// ---------------------------------------------------------------------------
// Static content (translation keys for labels; data stays here)
// ---------------------------------------------------------------------------

interface TeamMember {
  nameKey: string;
  roleKey: string;
  bioKey: string;
  avatarInitials: string;
}

const TEAM: readonly TeamMember[] = [
  { nameKey: "team.maryamName", roleKey: "team.maryamRole", bioKey: "team.maryamBio", avatarInitials: "MM" },
  { nameKey: "team.amirName", roleKey: "team.amirRole", bioKey: "team.amirBio", avatarInitials: "AR" },
  { nameKey: "team.saharName", roleKey: "team.saharRole", bioKey: "team.saharBio", avatarInitials: "SK" },
] as const;

interface Milestone {
  year: string;
  titleKey: string;
  descriptionKey: string;
}

const TIMELINE: readonly Milestone[] = [
  { year: "2022", titleKey: "about.timelineEvents.founded.title", descriptionKey: "about.timelineEvents.founded.description" },
  { year: "2023", titleKey: "about.timelineEvents.carbonDashboard.title", descriptionKey: "about.timelineEvents.carbonDashboard.description" },
  { year: "2024", titleKey: "about.timelineEvents.watershedExpansion.title", descriptionKey: "about.timelineEvents.watershedExpansion.description" },
  { year: "2025", titleKey: "about.timelineEvents.ecoCoin.title", descriptionKey: "about.timelineEvents.ecoCoin.description" },
] as const;

// ---------------------------------------------------------------------------
// Subcomponents
// ---------------------------------------------------------------------------

function Mission(): JSX.Element {
  const { t, dir } = useLanguage();
  return (
    <section dir={dir} className="rounded-2xl bg-gradient-to-br from-emerald-600 to-teal-600 p-8 text-white sm:p-12">
      <h2 className="text-2xl font-bold sm:text-3xl">{t("about.mission")}</h2>
      <p className="mt-4 max-w-3xl text-sm leading-7 text-emerald-50 sm:text-base">
        {t("about.missionText")}
      </p>
    </section>
  );
}

function StatsRow(): JSX.Element {
  const { t, dir, language } = useLanguage();
  const stats = [
    { value: `+${formatNumber(50, language)}`, labelKey: "about.monitoredRegions" },
    { value: `+${formatNumber(12000, language)}`, labelKey: "about.activeUsers" },
    { value: `+${formatNumber(800, language)}`, labelKey: "about.envReports" },
    { value: "24/7", labelKey: "about.liveMonitoring" },
  ];
  return (
    <div dir={dir} className="grid grid-cols-2 gap-4 sm:grid-cols-4">
      {stats.map((s) => (
        <div key={s.labelKey} className="rounded-xl border border-gray-200 bg-white p-5 text-center">
          <p className="text-2xl font-bold text-emerald-600">{s.value}</p>
          <p className="mt-1 text-xs text-gray-600">{t(s.labelKey)}</p>
        </div>
      ))}
    </div>
  );
}

function TeamGrid(): JSX.Element {
  const { t, dir } = useLanguage();
  return (
    <section dir={dir}>
      <h2 className="text-xl font-bold text-gray-900">{t("about.leadership")}</h2>
      <p className="mt-1 text-sm text-gray-600">{t("about.leadershipSubtitle")}</p>
      <div className="mt-5 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {TEAM.map((member) => (
          <article key={member.nameKey} className="rounded-xl border border-gray-200 bg-white p-5">
            <div className="flex items-center gap-4">
              <span className="flex h-14 w-14 items-center justify-center rounded-full bg-emerald-100 text-base font-semibold text-emerald-700">
                {member.avatarInitials}
              </span>
              <div>
                <h3 className="text-sm font-semibold text-gray-900">{t(member.nameKey)}</h3>
                <p className="text-xs text-emerald-600">{t(member.roleKey)}</p>
              </div>
            </div>
            <p className="mt-4 text-sm leading-6 text-gray-600">{t(member.bioKey)}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function Timeline(): JSX.Element {
  const { t, dir, language } = useLanguage();
  return (
    <section dir={dir}>
      <h2 className="text-xl font-bold text-gray-900">{t("about.timeline")}</h2>
      <p className="mt-1 text-sm text-gray-600">{t("about.timelineSubtitle")}</p>
      <ol className="mt-6 space-y-6 border-s-2 border-emerald-100 ps-6">
        {TIMELINE.map((item) => (
          <li key={item.year} className="relative">
            <span className="absolute -start-[1.65rem] top-1 flex h-4 w-4 items-center justify-center rounded-full bg-emerald-500 ring-4 ring-emerald-50" />
            <p className="text-xs font-semibold text-emerald-600">
              {language === "fa" ? formatNumber(Number(item.year)) : item.year}
            </p>
            <h3 className="mt-1 text-sm font-semibold text-gray-900">{t(item.titleKey)}</h3>
            <p className="mt-1 text-sm leading-6 text-gray-600">{t(item.descriptionKey)}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export function AboutUs(): JSX.Element {
  const { t, dir } = useLanguage();
  return (
    <div dir={dir} className="mx-auto max-w-5xl px-4 py-8">
      <header className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-gray-900">{t("about.title")}</h1>
        <p className="mt-2 text-sm text-gray-600">{t("common.appTagline")}</p>
      </header>

      <div className="space-y-8">
        <Mission />
        <StatsRow />
        <TeamGrid />
        <Timeline />

        <div dir={dir} className="rounded-2xl border border-emerald-200 bg-emerald-50 p-8 text-center">
          <h2 className="text-xl font-bold text-gray-900">{t("about.joinCommunity")}</h2>
          <p className="mt-2 text-sm text-gray-600">{t("about.joinCommunityText")}</p>
          <Link
            to="/register"
            className="mt-4 inline-block rounded-lg bg-emerald-600 px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-700"
          >
            {t("user.register")}
          </Link>
        </div>
      </div>
    </div>
  );
}
