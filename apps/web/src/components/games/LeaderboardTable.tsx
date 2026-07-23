// apps/web/src/components/games/LeaderboardTable.tsx
// جدول RTL-safe (text-start/end) + مدال + highlight کاربر خودتان.
import type { LeaderEntry } from "./gamesData";
import { localeOf, type GameStrings, type GameLang } from "./gamesI18n";

const MEDAL: Record<number, string> = { 1: "🥇", 2: "🥈", 3: "🥉" };
const RANK_CHIP: Record<number, string> = {
  1: "bg-amber-50 text-amber-700",
  2: "bg-stone-100 text-stone-600",
  3: "bg-orange-50 text-orange-700",
};

interface Props {
  entries: LeaderEntry[];
  strings: GameStrings;
  lang: GameLang;
}

export function LeaderboardTable({ entries, strings: s, lang }: Props) {
  const locale = localeOf(lang);

  return (
    <div className="overflow-hidden rounded-2xl border border-stone-200/80 bg-white shadow-sm">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[420px] border-collapse text-sm">
          <thead>
            <tr className="border-b border-stone-200 bg-stone-50 text-xs font-bold uppercase tracking-wide text-stone-500">
              <th scope="col" className="p-4 text-start">{s.colRank}</th>
              <th scope="col" className="p-4 text-start">{s.colUser}</th>
              <th scope="col" className="p-4 text-end">{s.colPoints}</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((u) => {
              const medal = MEDAL[u.rank];
              const chip = RANK_CHIP[u.rank];
              return (
                <tr key={u.rank}
                  className={`border-b border-stone-100 transition-colors last:border-0 ${u.isYou ? "bg-violet-50/70" : "hover:bg-stone-50"}`}>
                  <td className="p-4 text-start">
                    {medal ? (
                      <span className="text-xl" aria-label={`rank ${u.rank}`}>{medal}</span>
                    ) : (
                      <span className={`inline-grid h-8 w-8 place-items-center rounded-full text-xs font-bold ${chip ?? "bg-stone-50 text-stone-500"}`}>
                        {u.rank.toLocaleString(locale)}
                      </span>
                    )}
                  </td>
                  <td className="p-4 text-start">
                    <span className="flex items-center gap-2.5">
                      <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-stone-100 text-base">{u.avatar}</span>
                      <span className={`font-semibold ${u.isYou ? "text-violet-800" : "text-stone-800"}`}>
                        {u.name}{u.isYou && <span className="ms-1.5 rounded-full bg-violet-100 px-2 py-0.5 text-[10px] font-bold text-violet-700">{s.you}</span>}
                      </span>
                    </span>
                  </td>
                  <td className={`p-4 text-end font-display font-black tabular-nums ${u.isYou ? "text-violet-700" : "text-stone-800"}`}>
                    {u.points.toLocaleString(locale)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}