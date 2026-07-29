// apps/web/src/components/satellite/SatelliteStats.tsx
import { Sprout, Cloud, Layers, Trophy } from "lucide-react";
import { SectionReveal } from "../eco/SectionReveal";
import { AnimatedCounter } from "../eco/AnimatedCounter";
import type { Tile } from "./satelliteData";
import { meanNdvi, meanCloud, bestTile, formatNdvi } from "./satelliteData";
import { satText, localeOf, type SatelliteStrings, type SatLang } from "./satelliteI18n";

interface Props { tiles: Tile[]; strings: SatelliteStrings; lang: SatLang; }

export function SatelliteStats({ tiles, strings: s, lang }: Props) {
  const locale = localeOf(lang);
  const best = bestTile(tiles);
  const cards = [
    { icon: Sprout, label: s.statAvgNdvi, node: <span>{formatNdvi(meanNdvi(tiles), locale)}</span>, color: "text-green-700", bg: "bg-green-50" },
    { icon: Cloud, label: s.statAvgCloud, node: <><AnimatedCounter end={Math.round(meanCloud(tiles))} /><span className="ms-0.5">٪</span></>, color: "text-sky-700", bg: "bg-sky-50" },
    { icon: Layers, label: s.statTiles, node: <AnimatedCounter end={tiles.length} />, color: "text-violet-700", bg: "bg-violet-50" },
    { icon: Trophy, label: s.statBest, node: <span className="text-sm font-bold leading-tight">{best ? satText(s, best.nameKey) : "—"}</span>, color: "text-amber-700", bg: "bg-amber-50" },
  ];
  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {cards.map((c, i) => (
        <SectionReveal key={c.label} delay={i * 70}>
          <div className={`flex items-center gap-3 rounded-2xl border border-stone-200/80 p-4 shadow-sm ${c.bg}`}>
            <c.icon className={`h-5 w-5 shrink-0 ${c.color}`} />
            <div className="min-w-0">
              <p className={`font-display text-2xl font-black tabular-nums leading-none ${c.color}`}>{c.node}</p>
              <p className="mt-1 truncate text-xs font-medium text-stone-600">{c.label}</p>
            </div>
          </div>
        </SectionReveal>
      ))}
    </div>
  );
}