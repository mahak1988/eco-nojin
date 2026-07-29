// apps/web/src/components/tourism/TourismStats.tsx
import { MapPin, Star, Users, ShieldCheck } from "lucide-react";
import { SectionReveal } from "../eco/SectionReveal";
import { AnimatedCounter } from "../eco/AnimatedCounter";
import type { Destination } from "./tourismData";
import { avgRating, totalVisitors, avgConservation, formatRating } from "./tourismData";
import type { TourismStrings } from "./tourismI18n";
import { localeOf, type TourLang } from "./tourismI18n";

interface Props { destinations: Destination[]; strings: TourismStrings; lang: TourLang; }

export function TourismStats({ destinations, strings: s, lang }: Props) {
  const locale = localeOf(lang);
  const cards = [
    { icon: MapPin, label: s.statDest, node: <AnimatedCounter end={destinations.length} />, color: "text-green-700", bg: "bg-green-50" },
    { icon: Star, label: s.statRating, node: <span>{formatRating(avgRating(destinations), locale)}</span>, color: "text-amber-700", bg: "bg-amber-50" },
    { icon: Users, label: s.statVisitors, node: <AnimatedCounter end={totalVisitors(destinations)} />, color: "text-blue-700", bg: "bg-blue-50" },
    { icon: ShieldCheck, label: s.statConservation, node: <><AnimatedCounter end={avgConservation(destinations)} /><span className="ms-0.5">٪</span></>, color: "text-emerald-700", bg: "bg-emerald-50" },
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