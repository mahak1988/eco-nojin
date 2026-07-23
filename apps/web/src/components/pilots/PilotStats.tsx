// apps/web/src/components/pilots/PilotStats.tsx
import { Activity, ClipboardList, Users, TrendingUp } from "lucide-react";
import { SectionReveal } from "../eco/SectionReveal";
import { AnimatedCounter } from "../eco/AnimatedCounter";
import type { Pilot } from "./pilotsData";
import { countByPhase, totalBeneficiaries, avgProgress } from "./pilotsData";
import type { PilotStrings } from "./pilotsI18n";

interface Props { pilots: Pilot[]; strings: PilotStrings; }

export function PilotStats({ pilots, strings: s }: Props) {
  const cards = [
    { icon: Activity, label: s.statActive, value: countByPhase(pilots, "active"), color: "text-green-700", bg: "bg-green-50", pct: false },
    { icon: ClipboardList, label: s.statPlanning, value: countByPhase(pilots, "planning"), color: "text-amber-700", bg: "bg-amber-50", pct: false },
    { icon: Users, label: s.statBeneficiaries, value: totalBeneficiaries(pilots), color: "text-blue-700", bg: "bg-blue-50", pct: false },
    { icon: TrendingUp, label: s.statAvgProgress, value: avgProgress(pilots), color: "text-violet-700", bg: "bg-violet-50", pct: true },
  ];
  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {cards.map((c, i) => (
        <SectionReveal key={c.label} delay={i * 70}>
          <div className={`flex items-center gap-3 rounded-2xl border border-stone-200/80 p-4 shadow-sm ${c.bg}`}>
            <c.icon className={`h-5 w-5 shrink-0 ${c.color}`} />
            <div>
              <p className={`font-display text-2xl font-black tabular-nums leading-none ${c.color}`}>
                <AnimatedCounter end={c.value} />{c.pct && <span className="ms-0.5">٪</span>}
              </p>
              <p className="mt-1 text-xs font-medium text-stone-600">{c.label}</p>
            </div>
          </div>
        </SectionReveal>
      ))}
    </div>
  );
}