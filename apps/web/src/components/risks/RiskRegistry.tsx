// apps/web/src/components/risks/RiskRegistry.tsx
// دفتر ریسک: کارت per-risk با تغییر mitigation (زنده) + expand جزئیات.
import { useState } from "react";
import { ChevronDown, User, CalendarDays, ShieldAlert } from "lucide-react";
import type { Risk, Mitigation } from "./risksData";
import { scoreOf, IMPACT_NUM, PRIORITY_NUM, SCORE_STYLE, MITIGATION_STYLE, PRIORITY_STYLE, MITIGATIONS, formatDate } from "./risksData";
import { riskText, impactText, likelihoodText, scoreText, mitigationText, priorityText, localeOf, type RiskStrings, type RiskLang } from "./risksI18n";

interface Props {
  risks: Risk[];
  strings: RiskStrings;
  lang: RiskLang;
  onChangeMitigation: (id: string, m: Mitigation) => void;
}

export function RiskRegistry({ risks, strings: s, lang, onChangeMitigation }: Props) {
  const locale = localeOf(lang);
  const [open, setOpen] = useState<Record<string, boolean>>({});

  if (risks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-stone-300 bg-white py-16 text-center">
        <ShieldAlert className="h-10 w-10 text-stone-300" />
        <p className="text-stone-500">{s.noRisks}</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {risks.map((r) => {
        const sc = scoreOf(r);
        const st = SCORE_STYLE[sc];
        const expanded = !!open[r.id];
        return (
          <article key={r.id} className="overflow-hidden rounded-2xl border border-stone-200/80 bg-white shadow-sm transition-all hover:shadow-md">
            <div className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between">
              <button onClick={() => setOpen((p) => ({ ...p, [r.id]: !p[r.id] }))} className="flex min-w-0 flex-1 items-start gap-3 text-start">
                <span className={`grid h-10 w-10 shrink-0 place-items-center rounded-xl font-display text-sm font-black ring-1 ${st.chip}`}>
                  {sc[0].toUpperCase()}
                </span>
                <span className="min-w-0">
                  <span className="block font-semibold text-stone-800">{riskText(s, r.titleKey)}</span>
                  <span className="mt-1 flex flex-wrap items-center gap-1.5">
                    <span className={`rounded-full px-2 py-0.5 text-[11px] font-bold ring-1 ${st.chip}`}>{s.scoreLabel}: {scoreText(s, sc)}</span>
                    <span className={`rounded-full px-2 py-0.5 text-[11px] font-bold ring-1 ${PRIORITY_STYLE[r.priority]}`}>{priorityText(s, r.priority)}</span>
                  </span>
                </span>
              </button>

              <div className="flex shrink-0 items-center gap-2">
                <label className="sr-only" htmlFor={`mit-${r.id}`}>{s.mitigationLabel}</label>
                <select id={`mit-${r.id}`} value={r.mitigation} onChange={(e) => onChangeMitigation(r.id, e.target.value as Mitigation)}
                  className={`cursor-pointer rounded-full px-2.5 py-1 text-[11px] font-bold ring-1 outline-none ${MITIGATION_STYLE[r.mitigation]}`}>
                  {MITIGATIONS.map((m) => <option key={m} value={m}>{mitigationText(s, m)}</option>)}
                </select>
                <button onClick={() => setOpen((p) => ({ ...p, [r.id]: !p[r.id] }))} aria-label={s.details}
                  className="grid h-8 w-8 place-items-center rounded-lg text-stone-400 transition-colors hover:bg-stone-100 hover:text-stone-700">
                  <ChevronDown className={`h-4 w-4 transition-transform ${expanded ? "rotate-180" : ""}`} />
                </button>
              </div>
            </div>

            {expanded && (
              <div className="space-y-3 border-t border-stone-100 bg-stone-50/60 p-4" style={{ animation: "fade-up .25s var(--ease-out)" }}>
                <p className="text-sm leading-relaxed text-stone-700">{riskText(s, r.descKey)}</p>
                <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                  <Meta icon={User} label={s.owner} value={r.owner} />
                  <Meta icon={CalendarDays} label={s.due} value={formatDate(r.due, locale)} />
                  <div className="rounded-xl border border-stone-200 bg-white p-2.5">
                    <p className="text-[10px] font-bold uppercase text-stone-400">{s.impactLabel}</p>
                    <p className="text-sm font-bold text-stone-800">{impactText(s, r.impact)} ({IMPACT_NUM[r.impact]})</p>
                  </div>
                  <div className="rounded-xl border border-stone-200 bg-white p-2.5">
                    <p className="text-[10px] font-bold uppercase text-stone-400">{s.likelihoodLabel}</p>
                    <p className="text-sm font-bold text-stone-800">{likelihoodText(s, r.likelihood)} ({PRIORITY_NUM[r.priority] /* placeholder, see note */ || 0})</p>
                  </div>
                </div>
              </div>
            )}
          </article>
        );
      })}
    </div>
  );
}

function Meta({ icon: Icon, label, value }: { icon: typeof User; label: string; value: string }) {
  return (
    <div className="rounded-xl border border-stone-200 bg-white p-2.5">
      <p className="flex items-center gap-1 text-[10px] font-bold uppercase text-stone-400"><Icon className="h-3 w-3" />{label}</p>
      <p className="truncate text-sm font-bold text-stone-800">{value}</p>
    </div>
  );
}