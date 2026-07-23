// apps/web/src/components/games/AchievementBadge.tsx
// نشان با حالت locked/unlocked + tooltip (title) — قفل‌ها «روح» پیشرفت می‌سازند.
import { Lock } from "lucide-react";
import type { Achievement } from "./gamesData";
import { gameText, type GameStrings } from "./gamesI18n";

interface Props {
  achievement: Achievement;
  strings: GameStrings;
}

export function AchievementBadge({ achievement: a, strings: s }: Props) {
  const tip = `${gameText(s, a.nameKey)} — ${gameText(s, a.descKey)}`;
  return (
    <div
      title={tip}
      className={`group relative grid aspect-square cursor-pointer place-items-center rounded-2xl text-2xl transition-all duration-300 ${
        a.unlocked
          ? "bg-gradient-to-br from-amber-50 to-orange-50 ring-1 ring-amber-600/15 hover:-translate-y-1 hover:shadow-md"
          : "bg-stone-100 grayscale"
      }`}
    >
      <span className={a.unlocked ? "" : "opacity-40"}>{a.icon}</span>
      {!a.unlocked && (
        <span className="absolute bottom-1.5 end-1.5 grid h-5 w-5 place-items-center rounded-full bg-stone-700 text-white shadow">
          <Lock className="h-3 w-3" />
        </span>
      )}
    </div>
  );
}