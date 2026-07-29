// apps/web/src/components/pilots/PilotCard.tsx
// کارت پایلوت: تصویر + SmartImg fallback (درس gamecoca) + phase timeline افقی.
import { useState } from "react";
import { Lightbulb, MapPin, Users, ArrowLeft } from "lucide-react";
import { AnimatedCounter } from "../eco/AnimatedCounter";
import type { Pilot, PilotPhase } from "./pilotsData";
import { PHASE_ORDER, PHASE_STYLE, phaseIndex } from "./pilotsData";
import { pilotText, phaseText, localeOf, type PilotStrings, type PilotLang } from "./pilotsI18n";

function SmartImg({ src, alt, fallback, className }: { src: string; alt: string; fallback: string; className?: string }) {
  const [err, setErr] = useState(false);
  if (err) return <div className={className} style={{ background: fallback }} />;
  return <img src={src} alt={alt} loading="lazy" decoding="async" onError={() => setErr(true)} className={className} />;
}

// آیکون phase (JSX → در .tsx)
const PHASE_ICON: Record<PilotPhase, string> = { planning: "📋", active: "⚡", monitoring: "📡", completed: "✅" };

interface Props { pilot: Pilot; strings: PilotStrings; lang: PilotLang; onOpen: (p: Pilot) => void; }

export function PilotCard({ pilot: p, strings: s, lang, onOpen }: Props) {
  const locale = localeOf(lang);
  const st = PHASE_STYLE[p.phase];
  const cur = phaseIndex(p.phase);

  return (
    <article className="group flex h-full flex-col overflow-hidden rounded-2xl border border-stone-200/80 bg-white shadow-sm transition-all hover:-translate-y-1 hover:shadow-md">
      <div className="relative h-40 overflow-hidden">
        <SmartImg src={p.image} alt={pilotText(s, p.nameKey)} fallback={st.grad}
          className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/55 to-transparent" />
        <span className="absolute top-3 start-3 grid h-9 w-9 place-items-center rounded-xl bg-white/90 text-lg shadow-sm backdrop-blur">
          <Lightbulb className="h-4 w-4 text-amber-600" />
        </span>
        <span className={`absolute top-3 end-3 inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-[11px] font-bold ring-1 ${st.chip}`}>
          {PHASE_ICON[p.phase]}{phaseText(s, p.phase)}
        </span>
      </div>

      <div className="flex flex-1 flex-col p-5">
        <h3 className="font-display text-lg leading-snug text-stone-800">{pilotText(s, p.nameKey)}</h3>
        <p className="mt-1.5 flex-1 text-sm leading-relaxed text-stone-600">{pilotText(s, p.descKey)}</p>

        <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-stone-500">
          <span className="inline-flex items-center gap-1"><MapPin className="h-3.5 w-3.5" />{pilotText(s, p.locationKey)}</span>
          <span className="inline-flex items-center gap-1"><Users className="h-3.5 w-3.5" /><AnimatedCounter end={p.beneficiaries} /> {s.beneficiaries}</span>
        </div>

        {/* phase timeline افقی */}
        <div className="relative mt-4 flex items-center justify-between px-1">
          <div className="absolute inset-x-1 top-1/2 h-0.5 -translate-y-1/2 bg-stone-200" />
          <div className="absolute inset-x-1 top-1/2 h-0.5 -translate-y-1/2 transition-all duration-700"
            style={{ width: `${(cur / (PHASE_ORDER.length - 1)) * 100}%`, background: "var(--v-green)" }} />
          {PHASE_ORDER.map((ph, i) => {
            const done = i <= cur;
            const isCur = i === cur;
            return (
              <span key={ph} title={phaseText(s, ph)}
                className={`relative z-10 grid h-5 w-5 place-items-center rounded-full border-2 transition-all ${
                  done ? "border-transparent text-white" : "border-stone-300 bg-white"
                }`}
                style={done ? { background: PHASE_STYLE[ph].dot.includes("green") ? "#16a34a" : PHASE_STYLE[ph].dot.includes("amber") ? "#f59e0b" : PHASE_STYLE[ph].dot.includes("blue") ? "#2563eb" : "#7c3aed" } : undefined}>
                {isCur && <span className="absolute inline-flex h-full w-full animate-ping rounded-full opacity-40" style={{ background: "currentColor" }} />}
                <span className="h-1.5 w-1.5 rounded-full bg-current" />
              </span>
            );
          })}
        </div>

        {/* progress */}
        <div className="mt-4">
          <div className="mb-1 flex items-center justify-between text-[11px] font-bold text-stone-500">
            <span>{s.progress}</span>
            <span className={st.text}><AnimatedCounter end={p.progress} />٪</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-stone-100">
            <div className={`h-full rounded-full transition-[width] duration-700 ease-out ${st.bar}`} style={{ width: `${p.progress}%` }} />
          </div>
        </div>

        <button onClick={() => onOpen(p)}
          className={`mt-4 inline-flex items-center justify-center gap-1.5 rounded-xl px-4 py-2 text-sm font-bold transition-all hover:-translate-y-0.5 ${st.chip} ring-1 hover:opacity-90`}>
          {s.viewDetails}<ArrowLeft className="h-4 w-4 rtl:rotate-180" />
        </button>
      </div>
    </article>
  );
}