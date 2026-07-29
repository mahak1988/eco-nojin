// apps/web/src/components/games/StreakLevelBar.tsx
// نوار streak/level/daily-goal — الهام مستقیم از Brilliant:
// "Streaks, levels, and daily goals motivate you to build on your progress."
import { Flame, TrendingUp, CheckCircle2 } from "lucide-react";
import { AnimatedCounter } from "../eco/AnimatedCounter";
import type { UserGameStats } from "./gamesData";
import type { GameStrings, GameLang } from "./gamesI18n";
import { localeOf } from "./gamesI18n";

interface Props {
  user: UserGameStats;
  strings: GameStrings;
  lang: GameLang;
}

export function StreakLevelBar({ user, strings: s, lang }: Props) {
  const locale = localeOf(lang);
  const xpPct = Math.min(100, Math.round((user.xp / user.xpToNext) * 100));
  const dailyPct = Math.min(100, Math.round((user.dailyDone / user.dailyGoal) * 100));
  const dailyComplete = user.dailyDone >= user.dailyGoal;

  return (
    <div className="relative overflow-hidden rounded-3xl p-5 text-white shadow-xl sm:p-6"
      style={{ background: "linear-gradient(135deg, #4c1d95 0%, #6d28d9 45%, #7c3aed 100%)" }}>
      <div className="pointer-events-none absolute -top-16 -end-16 h-48 w-48 rounded-full bg-fuchsia-300/20 blur-2xl" />
      <div className="pointer-events-none absolute -bottom-20 -start-10 h-48 w-48 rounded-full bg-amber-300/10 blur-2xl" />

      <div className="relative grid grid-cols-1 gap-5 sm:grid-cols-3 sm:gap-6">
        {/* streak */}
        <div className="flex items-center gap-3">
          <span className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-white/15 text-2xl backdrop-blur"
            style={{ animation: "pulse-glow 2.4s ease-in-out infinite" }}>🔥</span>
          <div>
            <p className="font-display text-3xl font-black tabular-nums leading-none">
              <AnimatedCounter end={user.streak} />
            </p>
            <p className="mt-1 text-xs font-medium text-violet-100/85">{s.streak}</p>
          </div>
        </div>

        {/* level + XP */}
        <div className="sm:border-s sm:border-white/15 sm:ps-6">
          <div className="flex items-center justify-between">
            <span className="inline-flex items-center gap-1.5 text-xs font-bold text-violet-100/85">
              <TrendingUp className="h-3.5 w-3.5" />{s.level}
            </span>
            <span className="font-display text-2xl font-black tabular-nums">{user.level.toLocaleString(locale)}</span>
          </div>
          <div className="mt-2 h-2 overflow-hidden rounded-full bg-white/15">
            <div className="h-full rounded-full bg-gradient-to-r from-amber-300 to-amber-400 transition-[width] duration-700 ease-out"
              style={{ width: `${xpPct}%` }} />
          </div>
          <p className="mt-1 text-[11px] text-violet-100/75">
            {user.xp.toLocaleString(locale)} / {user.xpToNext.toLocaleString(locale)} {s.xpToNext}
          </p>
        </div>

        {/* daily goal */}
        <div className="sm:border-s sm:border-white/15 sm:ps-6">
          <div className="flex items-center justify-between">
            <span className="inline-flex items-center gap-1.5 text-xs font-bold text-violet-100/85">
              <CheckCircle2 className="h-3.5 w-3.5" />{s.dailyGoal}
            </span>
            <span className="font-display text-2xl font-black tabular-nums">
              {user.dailyDone.toLocaleString(locale)}/{user.dailyGoal.toLocaleString(locale)}
            </span>
          </div>
          <div className="mt-2 h-2 overflow-hidden rounded-full bg-white/15">
            <div className={`h-full rounded-full transition-[width] duration-700 ease-out ${dailyComplete ? "bg-emerald-300" : "bg-gradient-to-r from-emerald-300 to-teal-300"}`}
              style={{ width: `${dailyPct}%` }} />
          </div>
          <p className="mt-1 text-[11px] text-violet-100/75">{s.dailyDone}</p>
        </div>
      </div>

      <p className="relative mt-4 text-center text-xs font-medium text-violet-100/80 sm:text-start">{s.keepGoing}</p>
    </div>
  );
}