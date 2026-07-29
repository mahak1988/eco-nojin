// apps/web/src/components/reports/ReportStats.tsx
import { FileText, CheckCircle2, FileEdit, Download } from "lucide-react";
import { SectionReveal } from "../eco/SectionReveal";
import { AnimatedCounter } from "../eco/AnimatedCounter";
import type { Report } from "./reportsData";
import { countByStatus, sumDownloads } from "./reportsData";
import type { ReportStrings } from "./reportsI18n";

interface Props { reports: Report[]; strings: ReportStrings; }

export function ReportStats({ reports, strings: s }: Props) {
  const cards = [
    { icon: FileText, label: s.statTotal, value: reports.length, color: "text-stone-700", bg: "bg-stone-100" },
    { icon: CheckCircle2, label: s.statPublished, value: countByStatus(reports, "published"), color: "text-green-700", bg: "bg-green-50" },
    { icon: FileEdit, label: s.statDraft, value: countByStatus(reports, "draft"), color: "text-amber-700", bg: "bg-amber-50" },
    { icon: Download, label: s.statDownloads, value: sumDownloads(reports), color: "text-blue-700", bg: "bg-blue-50" },
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
              <p className="mt-1 truncate text-xs font-medium text-stone-600">{c.label}</p>
            </div>
          </div>
        </SectionReveal>
      ))}
    </div>
  );
}