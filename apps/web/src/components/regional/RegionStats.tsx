// apps/web/src/components/regional/RegionStats.tsx
import { Globe, FolderKanban, Users, Leaf } from "lucide-react";
import { SectionReveal } from "../eco/SectionReveal";
import { AnimatedCounter } from "../eco/AnimatedCounter";
import type { Region } from "./regionalData";
import { countActive, sumProjects, sumBeneficiaries, sumCarbon } from "./regionalData";
import type { RegionalStrings } from "./regionalI18n";

interface Props { regions: Region[]; strings: RegionalStrings; }

export function RegionStats({ regions, strings: s }: Props) {
  const cards = [
    { icon: Globe, label: s.statRegions, value: countActive(regions), color: "text-green-700", bg: "bg-green-50", unit: "" },
    { icon: FolderKanban, label: s.statProjects, value: sumProjects(regions), color: "text-blue-700", bg: "bg-blue-50", unit: "" },
    { icon: Users, label: s.statBeneficiaries, value: sumBeneficiaries(regions), color: "text-amber-700", bg: "bg-amber-50", unit: "" },
    { icon: Leaf, label: s.statCarbon, value: sumCarbon(regions), color: "text-emerald-700", bg: "bg-emerald-50", unit: s.carbonUnit },
  ];
  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {cards.map((c, i) => (
        <SectionReveal key={c.label} delay={i * 70}>
          <div className={`flex items-center gap-3 rounded-2xl border border-stone-200/80 p-4 shadow-sm ${c.bg}`}>
            <c.icon className={`h-5 w-5 shrink-0 ${c.color}`} />
            <div className="min-w-0">
              <p className={`font-display text-2xl font-black tabular-nums leading-none ${c.color}`}>
                <AnimatedCounter end={c.value} />
              </p>
              <p className="mt-1 truncate text-xs font-medium text-stone-600">{c.label}{c.unit && ` (${c.unit})`}</p>
            </div>
          </div>
        </SectionReveal>
      ))}
    </div>
  );
}