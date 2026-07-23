// apps/web/src/components/payments/PaymentStats.tsx
import { CheckCircle2, Clock, XCircle, TrendingUp } from "lucide-react";
import { SectionReveal } from "../eco/SectionReveal";
import { AnimatedCounter } from "../eco/AnimatedCounter";
import type { Payment } from "./paymentsData";
import { countByStatus, successRate } from "./paymentsData";
import { localeOf, type PaymentStrings, type PayLang } from "./paymentsI18n";

interface Props {
  payments: Payment[];
  strings: PaymentStrings;
  lang: PayLang;
}

export function PaymentStats({ payments, strings: s, lang }: Props) {
  const locale = localeOf(lang);
  const rate = successRate(payments);
  const cards = [
    { icon: CheckCircle2, label: s.statCompleted, value: countByStatus(payments, "completed"), color: "text-green-700", bg: "bg-green-50", pct: false },
    { icon: Clock, label: s.statPending, value: countByStatus(payments, "pending"), color: "text-amber-700", bg: "bg-amber-50", pct: false },
    { icon: XCircle, label: s.statFailed, value: countByStatus(payments, "failed"), color: "text-red-700", bg: "bg-red-50", pct: false },
    { icon: TrendingUp, label: s.statSuccess, value: rate, color: "text-blue-700", bg: "bg-blue-50", pct: true },
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
              <AnimatedCounter end={c.value} />{c.pct && <span className="ms-0.5">٪</span>}
            </p>
          </div>
        </SectionReveal>
      ))}
    </div>
  );
}