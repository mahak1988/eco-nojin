/**
 * ============================================================================
 *  EcoCoinDashboard — EcoCoin overview (i18n-aware)
 * ============================================================================
 */

import { Link } from "react-router-dom";

import { useLanguage } from "@/hooks/useLanguage";
import { formatNumber } from "@/lib/i18n-utils";

const QUICK_LINKS = [
  { to: "/ecocoin/wallet", labelKey: "ecoCoin.wallet", icon: "👛" },
  { to: "/ecocoin/mining", labelKey: "ecoCoin.mining", icon: "⛏️" },
  { to: "/ecocoin/challenges", labelKey: "ecoCoin.challenges", icon: "🏆" },
  { to: "/ecocoin/rewards", labelKey: "ecoCoin.rewards", icon: "🎁" },
] as const;

export function EcoCoinDashboard(): JSX.Element {
  const { t, dir, language } = useLanguage();

  const stats = [
    { labelKey: "ecoCoin.balance", value: formatNumber(1250, language), suffix: "ECO" },
    { labelKey: "ecoCoin.minedThisMonth", value: formatNumber(320, language), suffix: "ECO" },
    { labelKey: "ecoCoin.challengesCompleted", value: formatNumber(8, language), suffix: "" },
    { labelKey: "ecoCoin.rank", value: formatNumber(142, language), suffix: "" },
  ];

  return (
    <div dir={dir} className="mx-auto max-w-7xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("ecoCoin.title")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("ecoCoin.subtitle")}</p>
      </header>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((s) => (
          <div key={s.labelKey} className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-gray-600">{t(s.labelKey)}</p>
            <p className="mt-2 text-2xl font-bold text-gray-900">
              {s.value}
              {s.suffix && <span className="ms-1 text-sm font-normal text-gray-500">{s.suffix}</span>}
            </p>
          </div>
        ))}
      </div>

      <h2 className="mb-4 mt-8 text-lg font-semibold text-gray-900">{t("dashboard.quickAccess")}</h2>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {QUICK_LINKS.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className="group rounded-xl border border-gray-200 bg-white p-5 transition hover:border-emerald-200 hover:shadow-md"
          >
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-2xl">{link.icon}</div>
            <h3 className="mt-4 text-base font-semibold text-gray-900">{t(link.labelKey)}</h3>
          </Link>
        ))}
      </div>
    </div>
  );
}
