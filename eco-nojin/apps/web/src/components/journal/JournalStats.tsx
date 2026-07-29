// apps/web/src/components/journal/JournalStats.tsx
import { ArrowUpRight, ArrowDownRight, Scale, BookOpen } from "lucide-react";
import { SectionReveal } from "../eco/SectionReveal";
import { AnimatedCounter } from "../eco/AnimatedCounter";
import type { JournalEntry } from "./journalData";
import { allTotals } from "./journalData";
import { formatMoney, type JournalStrings, type JrLang } from "./journalI18n";

interface Props {
  entries: JournalEntry[];
  strings: JournalStrings;
  lang: JrLang;
}

export function JournalStats({ entries, strings: s, lang }: Props) {
  const t = allTotals(entries);
  const isBalanced = Math.abs(t.balance) < 0.001;

  const cards = [
    { icon: ArrowUpRight, label: s.totalDebits, value: t.totalDebit, color: "text-green-700", bg: "bg-green-50", money: true },
    { icon: ArrowDownRight, label: s.totalCredits, value: t.totalCredit, color: "text-blue-700", bg: "bg-blue-50", money: true },
    {
      icon: Scale, label: s.balance, value: Math.abs(t.balance),
      color: isBalanced ? "text-green-700" : "text-red-700",
      bg: isBalanced ? "bg-green-50" : "bg-red-50",
      money: true, balancedFlag: isBalanced,
    },
    { icon: BookOpen, label: s.totalEntries, value: t.count, color: "text-violet-700", bg: "bg-violet-50", money: false },
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
              {"balancedFlag" in c ? (
                c.balancedFlag ? s.balanced : <AnimatedCounter end={c.value} prefix="$" />
              ) : c.money ? (
                <AnimatedCounter end={c.value} prefix="$" />
              ) : (
                <AnimatedCounter end={c.value} />
              )}
            </p>
          </div>
        </SectionReveal>
      ))}
    </div>
  );
}