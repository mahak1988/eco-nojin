/**
 * ============================================================================
 *  EcoCoin Challenges — environmental challenges (i18n-aware)
 * ============================================================================
 */

import { useLanguage } from "@/hooks/useLanguage";
import { formatNumber } from "@/lib/i18n-utils";
import { cn } from "@/lib/utils";

interface Challenge { id: string; titleKey: string; descKey: string; reward: number; status: "active" | "completed"; }
const CHALLENGES: readonly Challenge[] = [
  { id: "1", titleKey: "ecoCoin.ch1Title", descKey: "ecoCoin.ch1Desc", reward: 50, status: "active" },
  { id: "2", titleKey: "ecoCoin.ch2Title", descKey: "ecoCoin.ch2Desc", reward: 100, status: "active" },
  { id: "3", titleKey: "ecoCoin.ch3Title", descKey: "ecoCoin.ch3Desc", reward: 30, status: "completed" },
  { id: "4", titleKey: "ecoCoin.ch4Title", descKey: "ecoCoin.ch4Desc", reward: 75, status: "active" },
  { id: "5", titleKey: "ecoCoin.ch5Title", descKey: "ecoCoin.ch5Desc", reward: 200, status: "active" },
] as const;

export function Challenges(): JSX.Element {
  const { t, dir, language } = useLanguage();

  return (
    <div dir={dir} className="mx-auto max-w-4xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("ecoCoin.challenges")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("ecoCoin.challengesSubtitle")}</p>
      </header>

      <div className="grid gap-4 sm:grid-cols-2">
        {CHALLENGES.map((ch) => (
          <article key={ch.id} className="rounded-xl border border-gray-200 bg-white p-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h3 className="text-base font-semibold text-gray-900">{t(ch.titleKey)}</h3>
                <p className="mt-1 text-sm text-gray-600">{t(ch.descKey)}</p>
              </div>
              <span className={cn(
                "shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium",
                ch.status === "completed" ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700",
              )}>
                {ch.status === "completed" ? t("ecoCoin.completed") : t("ecoCoin.active")}
              </span>
            </div>
            <div className="mt-4 flex items-center justify-between">
              <span className="text-sm font-semibold text-emerald-600">+{formatNumber(ch.reward, language)} ECO</span>
              {ch.status === "active" && (
                <button type="button" className="rounded-lg bg-emerald-600 px-4 py-1.5 text-xs font-medium text-white hover:bg-emerald-700">
                  {t("ecoCoin.startChallenge")}
                </button>
              )}
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
