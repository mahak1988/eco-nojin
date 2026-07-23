// apps/web/src/components/ecocoin/ChallengeCard.tsx
import { Trophy, Check } from "lucide-react";
import type { Challenge } from "./ecocoinData";
import { ecoText, localeOf, type EcoStrings, type EcoLang } from "./ecocoinI18n";

interface Props {
  challenge: Challenge;
  strings: EcoStrings;
  lang: EcoLang;
  onClaim: (id: string) => void;
}

export function ChallengeCard({ challenge: c, strings: s, lang, onClaim }: Props) {
  const locale = localeOf(lang);
  const pct = Math.min(100, Math.round((c.progress / c.goal) * 100));
  const complete = c.progress >= c.goal;
  const claimable = complete && !c.claimed;

  return (
    <article className="flex flex-col rounded-2xl border border-stone-200/80 bg-white p-5 shadow-sm transition-all hover:shadow-md">
      <div className="mb-3 flex items-start justify-between gap-2">
        <span className="text-3xl">{c.icon}</span>
        <span className="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2.5 py-1 text-xs font-bold text-amber-700">
          <Trophy className="h-3.5 w-3.5" />+{c.reward.toLocaleString(locale)}
        </span>
      </div>
      <h3 className="font-bold text-stone-800">{ecoText(s, c.titleKey)}</h3>

      <div className="mt-3 flex items-center justify-between text-xs font-bold text-stone-600">
        <span>{s.progress}</span>
        <span className="tabular-nums">{c.progress.toLocaleString(locale)}/{c.goal.toLocaleString(locale)}</span>
      </div>
      <div className="mt-1.5 h-2 overflow-hidden rounded-full bg-stone-100">
        <div className="h-full rounded-full bg-gradient-to-r from-green-500 to-emerald-400 transition-[width] duration-700 ease-out"
          style={{ width: `${pct}%` }} />
      </div>

      <button
        onClick={() => claimable && onClaim(c.id)}
        disabled={!claimable}
        className={`mt-4 inline-flex items-center justify-center gap-1.5 rounded-xl px-4 py-2 text-sm font-bold transition-all ${
          c.claimed
            ? "cursor-default bg-stone-100 text-stone-500"
            : claimable
            ? "bg-green-600 text-white shadow-sm hover:-translate-y-0.5 hover:bg-green-700"
            : "cursor-not-allowed bg-stone-100 text-stone-400"
        }`}
      >
        {c.claimed ? <><Check className="h-4 w-4" />{s.claimed}</> : s.claim}
      </button>
    </article>
  );
}