// apps/web/src/components/mrv/SafeguardsPanel.tsx
// چک‌لیست انطباق safeguard + نوار compliance (روحِ بخش Safeguards که فایل اصلی نداشت).
import { ShieldCheck, ShieldAlert, Check } from "lucide-react";
import { SectionReveal } from "../eco/SectionReveal";
import type { Safeguard } from "./mrvData";
import { complianceRate } from "./mrvData";
import { mrvText, localeOf, type MrvStrings, type MrvLang } from "./mrvI18n";

interface Props {
  safeguards: Safeguard[];
  strings: MrvStrings;
  lang: MrvLang;
  onToggle: (id: string) => void;
}

export function SafeguardsPanel({ safeguards, strings: s, lang, onToggle }: Props) {
  const locale = localeOf(lang);
  const rate = complianceRate(safeguards);
  const passedN = safeguards.filter((x) => x.passed).length;
  const allMet = rate === 100;

  return (
    <SectionReveal delay={120}>
      <div className="rounded-2xl border border-stone-200/80 bg-white p-5 shadow-sm sm:p-6">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            {allMet
              ? <ShieldCheck className="h-5 w-5 text-green-700" />
              : <ShieldAlert className="h-5 w-5 text-amber-700" />}
            <div>
              <h2 className="font-display text-lg text-stone-800">{s.safeguardsTitle}</h2>
              <p className="text-sm text-stone-600">{s.safeguardsSub}</p>
            </div>
          </div>
          <div className="text-end">
            <p className="text-xs font-medium text-stone-500">{s.compliance}</p>
            <p className={`font-display text-2xl font-black tabular-nums ${allMet ? "text-green-700" : "text-amber-700"}`}>
              {rate.toLocaleString(locale)}٪
            </p>
          </div>
        </div>

        {/* compliance bar */}
        <div className="mb-5 h-2 overflow-hidden rounded-full bg-stone-100">
          <div className={`h-full rounded-full transition-[width] duration-700 ease-out ${allMet ? "bg-green-500" : "bg-gradient-to-r from-amber-500 to-orange-400"}`}
            style={{ width: `${rate}%` }} />
        </div>

        <ul className="space-y-2">
          {safeguards.map((sg) => (
            <li key={sg.id}>
              <button onClick={() => onToggle(sg.id)} aria-pressed={sg.passed}
                className={`flex w-full items-start gap-3 rounded-xl border p-3 text-start transition-all ${
                  sg.passed ? "border-green-200 bg-green-50/50" : "border-stone-200 hover:border-stone-300"
                }`}>
                <span className={`mt-0.5 grid h-6 w-6 shrink-0 place-items-center rounded-full border-2 transition-all ${
                  sg.passed ? "border-transparent bg-green-600 text-white" : "border-stone-300 text-transparent"
                }`}>
                  <Check className="h-3.5 w-3.5" />
                </span>
                <span className="min-w-0 flex-1">
                  <span className={`block font-semibold ${sg.passed ? "text-stone-800" : "text-stone-600"}`}>{mrvText(s, sg.nameKey)}</span>
                  <span className="mt-0.5 block text-sm text-stone-500">{mrvText(s, sg.descKey)}</span>
                </span>
                <span className={`shrink-0 text-xs font-bold ${sg.passed ? "text-green-700" : "text-stone-400"}`}>
                  {sg.passed ? s.passed : s.todo}
                </span>
              </button>
            </li>
          ))}
        </ul>

        <p className="mt-4 text-center text-xs text-stone-500">
          {passedN.toLocaleString(locale)} {s.passedOf} {safeguards.length.toLocaleString(locale)}
        </p>
      </div>
    </SectionReveal>
  );
}