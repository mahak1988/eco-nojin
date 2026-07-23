// apps/web/src/pages/RisksPage.tsx
import { useMemo, useState } from "react";
import { ShieldAlert, Search, Download, Check } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { RiskStats } from "../components/risks/RiskStats";
import { RiskMatrix, type MatrixFilter } from "../components/risks/RiskMatrix";
import { RiskRegistry } from "../components/risks/RiskRegistry";
import { RISK_STR, riskText, impactText, likelihoodText, scoreText, mitigationText, priorityText, localeOf, type RiskLang } from "../components/risks/risksI18n";
import {
  INITIAL_RISKS, IMPACTS, MITIGATIONS, scoreOf, IMPACT_NUM, PRIORITY_NUM, SCORE_NUM, downloadCSV,
  type Risk, type Impact, type Mitigation, type SortKey, type SortDir,
} from "../components/risks/risksData";

export default function RisksPage() {
  const { lang } = useLang();
  const s = RISK_STR[lang as RiskLang];
  const locale = localeOf(lang as RiskLang);

  const [risks, setRisks] = useState<Risk[]>(INITIAL_RISKS);
  const [search, setSearch] = useState("");
  const [sevFilter, setSevFilter] = useState<"all" | Impact>("all");
  const [mitFilter, setMitFilter] = useState<"all" | Mitigation>("all");
  const [matrixFilter, setMatrixFilter] = useState<MatrixFilter | null>(null);
  const [sortKey, setSortKey] = useState<SortKey>("score");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [exported, setExported] = useState(false);

  // پایهٔ ماتریس: همهٔ فیلترها جز ماتریس (تا ماتریس خودش را صفر نکند)
  const matrixBase = useMemo(() => {
    const q = search.trim().toLowerCase();
    return risks.filter((r) =>
      (sevFilter === "all" || r.impact === sevFilter) &&
      (mitFilter === "all" || r.mitigation === mitFilter) &&
      (q === "" || riskText(s, r.titleKey).toLowerCase().includes(q) || r.owner.toLowerCase().includes(q))
    );
  }, [risks, sevFilter, mitFilter, search, lang]); // eslint-disable-line react-hooks/exhaustive-deps

  // لیست نمایش: پایه + فیلتر ماتریس + sort
  const display = useMemo(() => {
    const list = matrixBase.filter((r) =>
      !matrixFilter || (r.impact === matrixFilter.impact && r.likelihood === matrixFilter.likelihood)
    );
    list.sort((a, b) => {
      let cmp = 0;
      if (sortKey === "score") cmp = SCORE_NUM[scoreOf(a)] - SCORE_NUM[scoreOf(b)];
      else if (sortKey === "impact") cmp = IMPACT_NUM[a.impact] - IMPACT_NUM[b.impact];
      else if (sortKey === "priority") cmp = PRIORITY_NUM[a.priority] - PRIORITY_NUM[b.priority];
      else cmp = riskText(s, a.titleKey).localeCompare(riskText(s, b.titleKey));
      return sortDir === "asc" ? cmp : -cmp;
    });
    return list;
  }, [matrixBase, matrixFilter, sortKey, sortDir, lang]); // eslint-disable-line react-hooks/exhaustive-deps

  const onSort = (k: SortKey) => {
    if (k === sortKey) setSortDir((dd) => (dd === "asc" ? "desc" : "asc"));
    else { setSortKey(k); setSortDir(k === "title" ? "asc" : "desc"); }
  };
  const onToggleMatrix = (f: MatrixFilter) =>
    setMatrixFilter((cur) => (cur && cur.impact === f.impact && cur.likelihood === f.likelihood ? null : f));
  const changeMitigation = (id: string, m: Mitigation) =>
    setRisks((prev) => prev.map((r) => (r.id === id ? { ...r, mitigation: m } : r)));

  const exportAll = () => {
    const header = s.csvHeaders.split(",");
    const rows = display.map((r) => [
      r.id, riskText(s, r.titleKey), r.owner, impactText(s, r.impact), likelihoodText(s, r.likelihood),
      scoreText(s, scoreOf(r)), mitigationText(s, r.mitigation), priorityText(s, r.priority), r.due.slice(0, 10),
    ].map((c) => `"${c.replace(/"/g, '""')}"`).join(","));
    downloadCSV("risks.csv", [header.join(","), ...rows].join("\n"));
    setExported(true); setTimeout(() => setExported(false), 1800);
  };

  const selectCls = "rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm font-bold text-stone-700 outline-none focus:border-green-500 focus:ring-2 focus:ring-green-500/15";

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
      <SectionReveal>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-xl bg-red-50 ring-1 ring-red-600/15"><ShieldAlert className="h-5 w-5 text-red-700" /></div>
            <div>
              <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
              <p className="mt-0.5 text-stone-600">{s.subtitle}</p>
            </div>
          </div>
          <button onClick={exportAll} disabled={display.length === 0}
            className={`inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-bold shadow-sm transition-all hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50 ${exported ? "bg-green-50 text-green-700" : "bg-green-600 text-white hover:bg-green-700"}`}>
            {exported ? <Check className="h-4 w-4" /> : <Download className="h-4 w-4" />}{s.exportAll}
          </button>
        </div>
      </SectionReveal>

      <RiskStats risks={risks} strings={s} />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <RiskMatrix risks={matrixBase} filter={matrixFilter} onToggle={onToggleMatrix} strings={s} lang={lang as RiskLang} />

        <SectionReveal delay={110}>
          <div className="flex h-full flex-col gap-3 rounded-2xl border border-stone-200/80 bg-white p-5 shadow-sm">
            <div className="relative">
              <Search className="pointer-events-none absolute top-1/2 start-3 h-4 w-4 -translate-y-1/2 text-stone-400" />
              <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder={s.searchPlaceholder}
                className="w-full rounded-xl border border-stone-200 bg-white py-2.5 ps-9 pe-3 text-sm text-stone-800 outline-none transition-colors placeholder:text-stone-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/15" />
            </div>
            <div className="flex flex-wrap items-center gap-1 rounded-full border border-stone-200 bg-stone-50 p-1">
              {(["all", ...IMPACTS] as ("all" | Impact)[]).map((f) => (
                <button key={f} onClick={() => setSevFilter(f)}
                  className={`rounded-full px-3 py-1.5 text-xs font-bold transition-colors ${sevFilter === f ? "bg-green-600 text-white shadow-sm" : "text-stone-600 hover:bg-stone-100"}`}>
                  {f === "all" ? s.filterAllSev : impactText(s, f)}
                </button>
              ))}
            </div>
            <div className="flex flex-wrap items-center gap-1 rounded-full border border-stone-200 bg-stone-50 p-1">
              {(["all", ...MITIGATIONS] as ("all" | Mitigation)[]).map((f) => (
                <button key={f} onClick={() => setMitFilter(f)}
                  className={`rounded-full px-3 py-1.5 text-xs font-bold transition-colors ${mitFilter === f ? "bg-green-600 text-white shadow-sm" : "text-stone-600 hover:bg-stone-100"}`}>
                  {f === "all" ? s.filterAllMit : mitigationText(s, f)}
                </button>
              ))}
            </div>
            <select value={`${sortKey}-${sortDir}`}
              onChange={(e) => { const [k, dd] = e.target.value.split("-") as [SortKey, SortDir]; setSortKey(k); setSortDir(dd); }}
              className={selectCls} aria-label={s.sortLabel}>
              <option value="score-desc">{s.sortScore} ↓</option>
              <option value="score-asc">{s.sortScore} ↑</option>
              <option value="impact-desc">{s.sortImpact} ↓</option>
              <option value="priority-desc">{s.sortPriority} ↓</option>
              <option value="title-asc">{s.sortTitle} ↑</option>
            </select>
            {matrixFilter && (
              <button onClick={() => setMatrixFilter(null)}
                className="self-start rounded-full bg-stone-800 px-3 py-1 text-xs font-bold text-white transition-colors hover:bg-stone-700">
                ✕ {impactText(s, matrixFilter.impact)} × {likelihoodText(s, matrixFilter.likelihood)}
              </button>
            )}
          </div>
        </SectionReveal>
      </div>

      <SectionReveal delay={130}>
        <h2 className="mb-3 font-display text-xl text-stone-800">{s.registryTitle}</h2>
      </SectionReveal>
      <SectionReveal delay={150}>
        <RiskRegistry risks={display} strings={s} lang={lang as RiskLang} onChangeMitigation={changeMitigation} />
      </SectionReveal>
    </div>
  );
}