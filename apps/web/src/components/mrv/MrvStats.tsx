// apps/web/src/components/mrv/MrvStats.tsx
import { CheckCircle2, Clock, XCircle, Leaf } from "lucide-react";
import { SectionReveal } from "../eco/SectionReveal";
import { AnimatedCounter } from "../eco/AnimatedCounter";
import type { MrvReport } from "./mrvData";
import { countByStatus, totalVerifiedOffset, formatCarbon } from "./mrvData";
import { localeOf, type MrvStrings, type MrvLang } from "./mrvI18n";

interface Props {
  reports: MrvReport[];
  strings: MrvStrings;
  lang: MrvLang;
}

export function MrvStats({ reports, strings: s, lang }: Props) {
  const locale = localeOf(lang);
  const offset = totalVerifiedOffset(reports);

  const cards = [
    { icon: CheckCircle2, label: s.statVerified, value: countByStatus(reports, "verified"), color: "text-green-700", bg: "bg-green-50", money: false },
    { icon: Clock, label: s.statPending, value: countByStatus(reports, "pending"), color: "text-amber-700", bg: "bg-amber-50", money: false },
    { icon: XCircle, label: s.statRejected, value: countByStatus(reports, "rejected"), color: "text-red-700", bg: "bg-red-50", money: false },
    { icon: Leaf, label: s.statOffset, value: offset, color: "text-green-700", bg: "bg-emerald-50", money: true },
  ];

  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {cards.map((c, i) => (
        <SectionReveal key={c.label} delay={i * 70}>
          <div className={`rounded-2xl border border-stone-200/80 p-4 shadow-sm ${c.bg}`}>
            <div className="flex items-center gap-2">
              <c.icon className={`h-4 w-4 ${c.color}`} />
              <p className="text-sm font-medium text-stone-600">{c.label}</p>
            </div>
            <p className={`mt-2 font-display text-2xl font-black tabular-nums ${c.color}`}>
              <AnimatedCounter end={c.value} />
              {c.money && <span className="ms-1 text-xs font-bold text-stone-500">{s.carbonUnit}</span>}
            </p>
            {c.money && <p className="mt-1 text-[11px] text-stone-500">{s.verifiedOnly}</p>}
          </div>
        </SectionReveal>
      ))}
    </div>
  );
}