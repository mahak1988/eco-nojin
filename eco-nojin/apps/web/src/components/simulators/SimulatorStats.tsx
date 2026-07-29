// apps/web/src/components/simulators/SimulatorStats.tsx
import { Play, Activity, CheckCircle2, FlaskConical } from "lucide-react";
import { SectionReveal } from "../eco/SectionReveal";
import { AnimatedCounter } from "../eco/AnimatedCounter";
import type { SimState } from "./simulatorsData";
import { totalRuns, countStatus, SIM_CONFIGS } from "./simulatorsData";
import type { SimStrings } from "./simulatorsI18n";

interface Props { states: Record<string, SimState>; strings: SimStrings; }

export function SimulatorStats({ states, strings: s }: Props) {
  const cards = [
    { icon: Play, label: s.kpi_runs, value: totalRuns(states), color: "text-green-700", bg: "bg-green-50" },
    { icon: Activity, label: s.kpi_running, value: countStatus(states, "running"), color: "text-amber-700", bg: "bg-amber-50" },
    { icon: CheckCircle2, label: s.kpi_done, value: countStatus(states, "done"), color: "text-blue-700", bg: "bg-blue-50" },
    { icon: FlaskConical, label: s.kpi_models, value: SIM_CONFIGS.length, color: "text-violet-700", bg: "bg-violet-50" },
  ];
  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {cards.map((c, i) => (
        <SectionReveal key={c.label} delay={i * 70}>
          <div className={`flex items-center gap-3 rounded-2xl border border-stone-200/80 p-4 shadow-sm ${c.bg}`}>
            <c.icon className={`h-5 w-5 shrink-0 ${c.color}`} />
            <div className="min-w-0">
              <p className={`font-display text-2xl font-black tabular-nums leading-none ${c.color}`}><AnimatedCounter end={c.value} /></p>
              <p className="mt-1 truncate text-xs font-medium text-stone-600">{c.label}</p>
            </div>
          </div>
        </SectionReveal>
      ))}
    </div>
  );
}