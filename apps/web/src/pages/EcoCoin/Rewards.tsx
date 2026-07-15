/**
 * ============================================================================
 *  EcoCoin Rewards — reward store (i18n-aware)
 * ============================================================================
 */

import { useLanguage } from "@/hooks/useLanguage";
import { formatNumber } from "@/lib/i18n-utils";

interface Reward { id: string; nameKey: string; descKey: string; cost: number; icon: string; }
const REWARDS: readonly Reward[] = [
  { id: "1", nameKey: "ecoCoin.rw1Name", descKey: "ecoCoin.rw1Desc", cost: 500, icon: "📱" },
  { id: "2", nameKey: "ecoCoin.rw2Name", descKey: "ecoCoin.rw2Desc", cost: 1000, icon: "🌱" },
  { id: "3", nameKey: "ecoCoin.rw3Name", descKey: "ecoCoin.rw3Desc", cost: 300, icon: "📚" },
  { id: "4", nameKey: "ecoCoin.rw4Name", descKey: "ecoCoin.rw4Desc", cost: 2000, icon: "🎫" },
  { id: "5", nameKey: "ecoCoin.rw5Name", descKey: "ecoCoin.rw5Desc", cost: 750, icon: "♻️" },
  { id: "6", nameKey: "ecoCoin.rw6Name", descKey: "ecoCoin.rw6Desc", cost: 1500, icon: "🎁" },
] as const;

export function Rewards(): JSX.Element {
  const { t, dir, language } = useLanguage();

  return (
    <div dir={dir} className="mx-auto max-w-5xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("ecoCoin.rewards")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("ecoCoin.rewardsSubtitle")}</p>
      </header>

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {REWARDS.map((rw) => (
          <article key={rw.id} className="flex h-full flex-col rounded-xl border border-gray-200 bg-white p-5">
            <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-emerald-50 text-3xl">{rw.icon}</div>
            <h3 className="mt-4 text-sm font-semibold text-gray-900">{t(rw.nameKey)}</h3>
            <p className="mt-1 flex-1 text-xs leading-5 text-gray-600">{t(rw.descKey)}</p>
            <div className="mt-4 flex items-center justify-between">
              <span className="text-sm font-bold text-emerald-600">{formatNumber(rw.cost, language)} ECO</span>
              <button
                type="button"
                className="rounded-lg border border-emerald-600 px-3 py-1.5 text-xs font-medium text-emerald-700 transition hover:bg-emerald-50"
              >
                {t("ecoCoin.redeem")}
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
