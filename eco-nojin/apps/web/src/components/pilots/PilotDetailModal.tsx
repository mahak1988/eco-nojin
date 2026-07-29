// apps/web/src/components/pilots/PilotDetailModal.tsx
// جزئیات پایلوت: phase timeline عمودی + اهداف + متریک‌ها.
import { useEffect } from "react";
import { X, MapPin, Users, Wallet, Calendar, Target, CheckCircle2 } from "lucide-react";
import type { Pilot, PilotPhase } from "./pilotsData";
import { PHASE_ORDER, PHASE_STYLE, phaseIndex, formatNumber, formatBudget, formatDate } from "./pilotsData";
import { pilotText, phaseText, phaseDesc, localeOf, type PilotStrings, type PilotLang } from "./pilotsI18n";

const PHASE_ICON: Record<PilotPhase, string> = { planning: "📋", active: "⚡", monitoring: "📡", completed: "✅" };

interface Props { pilot: Pilot | null; strings: PilotStrings; lang: PilotLang; onClose: () => void; }

export function PilotDetailModal({ pilot: p, strings: s, lang, onClose }: Props) {
  const locale = localeOf(lang);
  useEffect(() => {
    if (!p) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [p, onClose]);

  if (!p) return null;
  const st = PHASE_STYLE[p.phase];
  const cur = phaseIndex(p.phase);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div onClick={onClose} className="absolute inset-0 bg-stone-900/40 backdrop-blur-sm" style={{ animation: "fade-in .2s ease-out" }} />
      <div role="dialog" aria-modal="true" aria-label={pilotText(s, p.nameKey)}
        className="relative flex max-h-[90vh] w-full max-w-2xl flex-col overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-xl"
        style={{ animation: "fade-up .25s var(--ease-out)" }}>
        {/* header image */}
        <div className="relative h-32 shrink-0" style={{ background: st.grad }}>
          <div className="absolute inset-0 bg-black/10" />
          <button onClick={onClose} className="absolute top-3 end-3 grid h-8 w-8 place-items-center rounded-full bg-white/90 text-stone-700 shadow transition-colors hover:bg-white">
            <X className="h-4 w-4" />
          </button>
          <div className="absolute bottom-3 start-5 flex items-center gap-2">
            <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-[11px] font-bold ring-1 ${st.chip}`}>{PHASE_ICON[p.phase]}{phaseText(s, p.phase)}</span>
          </div>
        </div>

        <div className="flex-1 space-y-5 overflow-y-auto p-5 sm:p-6">
          <div>
            <h2 className="font-display text-2xl text-stone-800">{pilotText(s, p.nameKey)}</h2>
            <p className="mt-1 text-sm leading-relaxed text-stone-600">{pilotText(s, p.descKey)}</p>
          </div>

          {/* metrics */}
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {[
              { icon: MapPin, label: pilotText(s, p.locationKey), v: "" },
              { icon: Users, label: s.beneficiaries, v: formatNumber(p.beneficiaries, locale) },
              { icon: Wallet, label: s.budget, v: formatBudget(p.budgetUsd, locale) },
              { icon: Calendar, label: s.startDate, v: formatDate(p.startDate, locale) },
            ].map((m, i) => (
              <div key={i} className="rounded-xl border border-stone-200 bg-stone-50 p-3">
                <m.icon className="mb-1 h-4 w-4 text-stone-400" />
                <p className="text-[11px] font-bold uppercase text-stone-400">{m.v ? m.label : ""}</p>
                <p className="truncate text-sm font-bold text-stone-800">{m.v || m.label}</p>
              </div>
            ))}
          </div>

          {/* goal */}
          <div className="flex items-start gap-2 rounded-xl bg-green-50/60 p-3 ring-1 ring-green-600/10">
            <Target className="mt-0.5 h-4 w-4 shrink-0 text-green-700" />
            <div>
              <p className="text-[11px] font-bold uppercase text-green-700">{s.goal}</p>
              <p className="text-sm font-medium text-stone-700">{pilotText(s, p.goalKey)}</p>
            </div>
          </div>

          {/* phase timeline عمودی */}
          <div>
            <p className="mb-2 text-[11px] font-bold uppercase text-stone-400">{s.phase}</p>
            <ol className="relative space-y-3 ps-2">
              {PHASE_ORDER.map((ph, i) => {
                const done = i <= cur;
                const isCur = i === cur;
                const last = i === PHASE_ORDER.length - 1;
                return (
                  <li key={ph} className="relative flex items-start gap-3">
                    {!last && <span className="absolute top-6 start-[9px] h-[calc(100%-4px)] w-0.5" style={{ background: i < cur ? "#16a34a" : "#e7e5e4" }} />}
                    <span className={`relative z-10 grid h-5 w-5 shrink-0 place-items-center rounded-full text-[10px] ${done ? "text-white" : "border-2 border-stone-300 bg-white"}`}
                      style={done ? { background: i === 0 ? "#f59e0b" : i === 1 ? "#16a34a" : i === 2 ? "#2563eb" : "#7c3aed" } : undefined}>
                      {done && <CheckCircle2 className="h-3 w-3" />}
                    </span>
                    <div className={isCur ? "" : "opacity-70"}>
                      <p className={`text-sm font-bold ${isCur ? st.text : "text-stone-700"}`}>{phaseText(s, ph)}</p>
                      <p className="text-xs text-stone-500">{phaseDesc(s, ph)}</p>
                    </div>
                  </li>
                );
              })}
            </ol>
          </div>

          {/* objectives */}
          <div>
            <p className="mb-2 text-[11px] font-bold uppercase text-stone-400">{s.objectives}</p>
            <ul className="space-y-1.5">
              {p.objectives.map((o) => (
                <li key={o.key} className="flex items-center gap-2 rounded-lg bg-stone-50 px-3 py-2 text-sm text-stone-700">
                  <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${st.dot}`} />
                  {pilotText(s, o.key)}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="shrink-0 border-t border-stone-100 p-4">
          <button onClick={onClose} className="w-full rounded-xl border border-stone-200 py-2.5 text-sm font-bold text-stone-700 transition-colors hover:bg-stone-50">{s.close}</button>
        </div>
      </div>
    </div>
  );
}
