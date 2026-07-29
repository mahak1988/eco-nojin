// apps/web/src/components/regional/RegionDetail.tsx
// جزئیات per-region — با تغییر انتخاب، زنده به‌روز می‌شود (باگ «اعداد ثابت» فایل اصلی رفع شد).
import { MapPin, FolderKanban, Users, Leaf, Calendar, CheckCircle2 } from "lucide-react";
import { SectionReveal } from "../eco/SectionReveal";
import { AnimatedCounter } from "../eco/AnimatedCounter";
import type { Region } from "./regionalData";
import { formatNumber } from "./regionalData";
import { regText, statusText, localeOf, type RegionalStrings, type RegLang } from "./regionalI18n";

interface Props { region: Region; strings: RegionalStrings; lang: RegLang; }

export function RegionDetail({ region: r, strings: s, lang }: Props) {
  const locale = localeOf(lang);
  const active = r.status === "active";

  const metrics = [
    { icon: FolderKanban, label: s.activePrograms, value: r.programs, color: "text-blue-700", bg: "bg-blue-50", unit: "" },
    { icon: Users, label: s.beneficiaries, value: r.beneficiaries, color: "text-amber-700", bg: "bg-amber-50", unit: "" },
    { icon: Leaf, label: s.carbonOffset, value: r.carbonT, color: "text-emerald-700", bg: "bg-emerald-50", unit: s.carbonUnit },
    { icon: MapPin, label: s.projects, value: r.projects, color: "text-green-700", bg: "bg-green-50", unit: "" },
  ];

  return (
    <SectionReveal delay={120}>
      {/* key={r.id} → انیمیشن fade هنگام تعویض منطقه */}
      <div key={r.id} className="rounded-2xl border border-stone-200/80 bg-white p-6 shadow-sm" style={{ animation: "fade-up .3s var(--ease-out)" }}>
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <span className={`grid h-12 w-12 place-items-center rounded-2xl font-display text-base font-black text-white ${active ? "bg-emerald-600" : "bg-amber-500"}`}>
              {r.code}
            </span>
            <div>
              <h2 className="font-display text-xl text-stone-800">{regText(s, r.nameKey)}</h2>
              <p className="mt-0.5 flex items-center gap-2 text-xs text-stone-500">
                <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 font-bold ring-1 ${active ? "bg-green-50 text-green-700 ring-green-600/15" : "bg-amber-50 text-amber-700 ring-amber-600/15"}`}>
                  {statusText(s, r.status)}
                </span>
                <span className="inline-flex items-center gap-1"><Calendar className="h-3 w-3" />{s.since} {r.since}</span>
              </p>
            </div>
          </div>
        </div>

        {/* metrics */}
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          {metrics.map((m) => (
            <div key={m.label} className={`rounded-xl p-4 ${m.bg}`}>
              <m.icon className={`mb-2 h-4 w-4 ${m.color}`} />
              <p className={`font-display text-2xl font-black tabular-nums ${m.color}`}>
                <AnimatedCounter end={m.value} />
              </p>
              <p className="mt-0.5 text-xs font-medium text-stone-600">{m.label}{m.unit && ` · ${m.unit}`}</p>
            </div>
          ))}
        </div>

        {/* progress */}
        <div className="mt-5">
          <div className="mb-1.5 flex items-center justify-between text-xs font-bold text-stone-600">
            <span>{s.progress}</span>
            <span className={active ? "text-green-700" : "text-amber-700"}>{formatNumber(r.progress, locale)}٪</span>
          </div>
          <div className="h-2.5 overflow-hidden rounded-full bg-stone-100">
            <div className={`h-full rounded-full transition-[width] duration-700 ease-out ${active ? "bg-gradient-to-r from-green-500 to-emerald-400" : "bg-gradient-to-r from-amber-500 to-orange-400"}`}
              style={{ width: `${r.progress}%` }} />
          </div>
        </div>

        {/* highlights */}
        <div className="mt-5">
          <p className="mb-2 text-[11px] font-bold uppercase tracking-wide text-stone-400">{s.highlightsTitle}</p>
          <ul className="space-y-2">
            {r.highlights.map((h) => (
              <li key={h.key} className="flex items-start gap-2.5 rounded-lg bg-stone-50 px-3 py-2.5 text-sm text-stone-700">
                <CheckCircle2 className={`mt-0.5 h-4 w-4 shrink-0 ${active ? "text-green-600" : "text-amber-500"}`} />
                {regText(s, h.key)}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </SectionReveal>
  );
}