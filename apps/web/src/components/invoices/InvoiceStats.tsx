// apps/web/src/components/invoices/InvoiceStats.tsx
import { Receipt, CheckCircle2, Clock, AlertTriangle } from "lucide-react";
import { SectionReveal } from "../eco/SectionReveal";
import { AnimatedCounter } from "../eco/AnimatedCounter";
import type { Invoice } from "./invoicesData";
import { sumByStatus } from "./invoicesData";
import { formatMoney, type InvoiceStrings, type InvLang } from "./invoicesI18n";

interface Props {
  invoices: Invoice[];
  strings: InvoiceStrings;
  lang: InvLang;
}

export function InvoiceStats({ invoices, strings: s, lang }: Props) {
  const cards = [
    { icon: Receipt, label: s.totalInvoiced, value: sumByStatus(invoices), color: "text-blue-700", bg: "bg-blue-50" },
    { icon: CheckCircle2, label: s.totalPaid, value: sumByStatus(invoices, "paid"), color: "text-green-700", bg: "bg-green-50" },
    { icon: Clock, label: s.totalPending, value: sumByStatus(invoices, "pending"), color: "text-amber-700", bg: "bg-amber-50" },
    { icon: AlertTriangle, label: s.totalOverdue, value: sumByStatus(invoices, "overdue"), color: "text-red-700", bg: "bg-red-50" },
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
              <AnimatedCounter end={c.value} prefix="$" />
            </p>
          </div>
        </SectionReveal>
      ))}
    </div>
  );
}