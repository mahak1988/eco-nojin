// apps/web/src/pages/PilotsPage.tsx
import { useMemo, useState } from "react";
import { Lightbulb, Search } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { PilotStats } from "../components/pilots/PilotStats";
import { PilotCard } from "../components/pilots/PilotCard";
import { PilotDetailModal } from "../components/pilots/PilotDetailModal";
import { PILOT_STR, pilotText, phaseText, localeOf, type PilotLang } from "../components/pilots/pilotsI18n";
import { PILOTS, PHASE_FILTERS, type Pilot, type PilotPhase, type SortKey, type SortDir } from "../components/pilots/pilotsData";

export default function PilotsPage() {
  const { lang } = useLang();
  const s = PILOT_STR[lang as PilotLang];

  const [search, setSearch] = useState("");
  const [phaseFilter, setPhaseFilter] = useState<"all" | PilotPhase>("all");
  const [sortKey, setSortKey] = useState<SortKey>("progress");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [open, setOpen] = useState<Pilot | null>(null);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    const list = PILOTS.filter((p) =>
      (phaseFilter === "all" || p.phase === phaseFilter) &&
      (q === "" || pilotText(s, p.nameKey).toLowerCase().includes(q) || pilotText(s, p.locationKey).toLowerCase().includes(q))
    );
    list.sort((a, b) => {
      let cmp = 0;
      if (sortKey === "progress") cmp = a.progress - b.progress;
      else if (sortKey === "beneficiaries") cmp = a.beneficiaries - b.beneficiaries;
      else cmp = pilotText(s, a.nameKey).localeCompare(pilotText(s, b.nameKey));
      return sortDir === "asc" ? cmp : -cmp;
    });
    return list;
  }, [search, phaseFilter, sortKey, sortDir, lang]); // eslint-disable-line react-hooks/exhaustive-deps

  const selectCls = "rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm font-bold text-stone-700 outline-none focus:border-green-500 focus:ring-2 focus:ring-green-500/15";

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
      <SectionReveal>
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-amber-50 ring-1 ring-amber-600/15">
            <Lightbulb className="h-5 w-5 text-amber-600" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
            <p className="mt-0.5 text-stone-600">{s.subtitle}</p>
          </div>
        </div>
      </SectionReveal>

      <PilotStats pilots={PILOTS} strings={s} />

      <SectionReveal delay={100}>
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative min-w-[220px] flex-1">
            <Search className="pointer-events-none absolute top-1/2 start-3 h-4 w-4 -translate-y-1/2 text-stone-400" />
            <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder={s.searchPlaceholder}
              className="w-full rounded-xl border border-stone-200 bg-white py-2.5 ps-9 pe-3 text-sm text-stone-800 outline-none transition-colors placeholder:text-stone-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/15" />
          </div>
          <div className="flex flex-wrap items-center gap-1 rounded-full border border-stone-200 bg-white p-1">
            {PHASE_FILTERS.map((f) => (
              <button key={f} onClick={() => setPhaseFilter(f)}
                className={`rounded-full px-3 py-1.5 text-xs font-bold transition-colors ${phaseFilter === f ? "bg-green-600 text-white shadow-sm" : "text-stone-600 hover:bg-stone-100"}`}>
                {f === "all" ? s.filterAll : phaseText(s, f)}
              </button>
            ))}
          </div>
          <select value={`${sortKey}-${sortDir}`}
            onChange={(e) => { const [k, dd] = e.target.value.split("-") as [SortKey, SortDir]; setSortKey(k); setSortDir(dd); }}
            className={selectCls} aria-label={s.sortLabel}>
            <option value="progress-desc">{s.sortProgress} ↓</option>
            <option value="progress-asc">{s.sortProgress} ↑</option>
            <option value="beneficiaries-desc">{s.sortBeneficiaries} ↓</option>
            <option value="beneficiaries-asc">{s.sortBeneficiaries} ↑</option>
            <option value="name-asc">{s.sortName} ↑</option>
          </select>
        </div>
      </SectionReveal>

      {filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-stone-300 bg-white py-16 text-center">
          <Lightbulb className="h-10 w-10 text-stone-300" />
          <p className="text-stone-500">{s.noPilots}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((p, i) => (
            <SectionReveal key={p.id} delay={Math.min(i * 60, 240)}>
              <PilotCard pilot={p} strings={s} lang={lang as PilotLang} onOpen={setOpen} />
            </SectionReveal>
          ))}
        </div>
      )}

      <PilotDetailModal pilot={open} strings={s} lang={lang as PilotLang} onClose={() => setOpen(null)} />
    </div>
  );
}