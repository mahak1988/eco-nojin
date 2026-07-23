// apps/web/src/components/risks/RiskStats.tsx
import { Shield, AlertTriangle, Flame, CheckCircle2 } from "lucide-react";
import { SectionReveal } from "../eco/SectionReveal";
import { AnimatedCounter } from "../eco/AnimatedCounter";
import type { Risk } from "./risksData";
import { countOpen, countMitigated, countHighCritical } from "./risksData";
import type { RiskStrings } from "./risksI18n";

interface Props { risks: Risk[]; strings: RiskStrings; }

export function RiskStats({ risks, strings: s }: Props) {
  const cards = [
    { icon: Shield, label: s.statTotal, value: risks.length, color: "text-stone-700", bg: "bg-stone-100" },
    { icon: AlertTriangle, label: s.statOpen, value: countOpen(risks), color: "text-amber-700", bg: "bg-amber-50" },
    { icon: Flame, label: s.statHigh, value: countHighCritical(risks), color: "text-red-700", bg: "bg-red-50" },
    { icon: CheckCircle2, label: s.statMitigated, value: countMitigated(risks), color: "text-green-700", bg: "bg-green-50" },
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