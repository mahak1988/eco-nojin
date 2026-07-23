// apps/web/src/components/policies/PolicyStats.tsx
import { FileText, CheckCircle2, Clock, FileEdit } from "lucide-react";
import { SectionReveal } from "../eco/SectionReveal";
import { AnimatedCounter } from "../eco/AnimatedCounter";
import type { Policy } from "./policiesData";
import { countByStatus } from "./policiesData";
import type { PolicyStrings } from "./policiesI18n";

interface Props { policies: Policy[]; strings: PolicyStrings; }

export function PolicyStats({ policies, strings: s }: Props) {
  const cards = [
    { icon: FileText, label: s.statTotal, value: policies.length, color: "text-stone-700", bg: "bg-stone-100" },
    { icon: CheckCircle2, label: s.statActive, value: countByStatus(policies, "active"), color: "text-green-700", bg: "bg-green-50" },
    { icon: Clock, label: s.statReview, value: countByStatus(policies, "review"), color: "text-amber-700", bg: "bg-amber-50" },
    { icon: FileEdit, label: s.statDraft, value: countByStatus(policies, "draft"), color: "text-blue-700", bg: "bg-blue-50" },
  ];
  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {cards.map((c, i) => (
        <SectionReveal key={c.label} delay={i * 70}>
          <div className={`flex items-center gap-3 rounded-2xl border border-stone-200/80 p-4 shadow-sm ${c.bg}`}>
            <c.icon className={`h-5 w-5 shrink-0 ${c.color}`} />
            <div>
              <p className={`font-display text-2xl font-black tabular-nums leading-none ${c.color}`}>
                <AnimatedCounter end={c.value} />
              </p>
              <p className="mt-1 text-xs font-medium text-stone-600">{c.label}</p>
            </div>
          </div>
        </SectionReveal>
      ))}
    </div>
  );
}