// apps/web/src/components/games/ChallengeCard.tsx
import { Trophy, Users, Clock, Check, Play, Plus, Lock } from "lucide-react";
import type { Challenge, DifficultyKey } from "./gamesData";
import { gameText, diffText, deadlineText, localeOf, type GameStrings, type GameLang } from "./gamesI18n";

const DIFF_STYLE: Record<DifficultyKey, string> = {
  diff_easy: "bg-green-50 text-green-700",
  diff_medium: "bg-amber-50 text-amber-700",
  diff_hard: "bg-red-50 text-red-700",
};

interface Props {
  challenge: Challenge;
  strings: GameStrings;
  lang: GameLang;
  onJoin: (id: string) => void;
  onAdvance: (id: string) => void;
  onClaim: (id: string) => void;
}

export function ChallengeCard({ challenge: c, strings: s, lang, onJoin, onAdvance, onClaim }: Props) {
  const locale = localeOf(lang);
  const dl = deadlineText(c.deadline, lang);
  const pct = Math.round((c.progress / c.goal) * 100);
  const complete = c.progress >= c.goal;
  const claimable = c.joined && complete && !c.claimed;

  return (
    <article className="rounded-2xl border border-stone-200/80 bg-white p-5 shadow-sm transition-all hover:shadow-md">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-stone-50 text-2xl ring-1 ring-stone-200">{c.icon}</span>
          <div>
            <h3 className="font-display text-lg leading-snug text-stone-800">{gameText(s, c.titleKey)}</h3>
            <p className="mt-0.5 text-sm text-stone-600">{gameText(s, c.descKey)}</p>
          </div>
        </div>
        <span className={`shrink-0 rounded-full px-2.5 py-1 text-[11px] font-bold ${DIFF_STYLE[c.difficultyKey]}`}>
          {diffText(s, c.difficultyKey)}
        </span>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-stone-600">
        <span className="inline-flex items-center gap-1 font-bold text-amber-700"><Trophy className="h-3.5 w-3.5" />{c.points.toLocaleString(locale)}</span>
        <span className="inline-flex items-center gap-1"><Users className="h-3.5 w-3.5" />{c.participants.toLocaleString(locale)} {s.participants}</span>
        <span className={`inline-flex items-center gap-1 ${dl.expired ? "text-stone-400" : dl.urgent ? "font-bold text-red-700" : ""}`}>
          <Clock className="h-3.5 w-3.5" />{dl.text}
        </span>
      </div>

      {/* progress (after join) */}
      {c.joined && (
        <div className="mt-3">
          <div className="mb-1 flex items-center justify-between text-[11px] font-bold text-stone-600">
            <span>{c.progress.toLocaleString(locale)}/{c.goal.toLocaleString(locale)}</span>
            <span className={c.claimed ? "text-green-700" : "text-violet-700"}>{pct.toLocaleString(locale)}٪</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-stone-100">
            <div className={`h-full rounded-full transition-[width] duration-700 ease-out ${c.claimed ? "bg-green-500" : "bg-gradient-to-r from-violet-500 to-fuchsia-400"}`}
              style={{ width: `${pct}%` }} />
          </div>
        </div>
      )}

      {/* actions */}
      <div className="mt-4 flex items-center gap-2">
        {!c.joined ? (
          <button onClick={() => onJoin(c.id)} disabled={dl.expired}
            className="inline-flex flex-1 items-center justify-center gap-1.5 rounded-xl bg-violet-600 px-4 py-2 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-violet-700 disabled:cursor-not-allowed disabled:bg-stone-300">
            <Play className="h-3.5 w-3.5" />{s.join}
          </button>
        ) : c.claimed ? (
          <span className="inline-flex flex-1 items-center justify-center gap-1.5 rounded-xl bg-green-50 px-4 py-2 text-sm font-bold text-green-700">
            <Check className="h-4 w-4" />{s.claimed}
          </span>
        ) : complete ? (
          <button onClick={() => onClaim(c.id)}
            className="inline-flex flex-1 items-center justify-center gap-1.5 rounded-xl bg-green-600 px-4 py-2 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-green-700">
            <Trophy className="h-3.5 w-3.5" />{s.claim}
          </button>
        ) : (
          <>
            <span className="inline-flex items-center justify-center gap-1.5 rounded-xl bg-violet-50 px-4 py-2 text-sm font-bold text-violet-700">
              <Check className="h-3.5 w-3.5" />{s.joined}
            </span>
            <button onClick={() => onAdvance(c.id)}
              className="inline-flex flex-1 items-center justify-center gap-1.5 rounded-xl bg-violet-600 px-4 py-2 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-violet-700">
              <Plus className="h-3.5 w-3.5" />{s.advance}
            </button>
          </>
        )}
      </div>
    </article>
  );
}