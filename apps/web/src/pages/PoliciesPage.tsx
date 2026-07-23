// apps/web/src/pages/PoliciesPage.tsx
import { useMemo, useState } from "react";
import { Scale, Search, Download, Check } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { PolicyStats } from "../components/policies/PolicyStats";
import { PolicyList, CATEGORY_ICON } from "../components/policies/PolicyList";
import { PolicyDetailModal } from "../components/policies/PolicyDetailModal";
import { POL_STR, polText, statusText, catText, localeOf, type PolLang } from "../components/policies/policiesI18n";
import {
  POLICIES, CATEGORY_ORDER, STATUS_FILTERS, countByCategory, compareVersion,
  formatDate, downloadText, downloadCSV, policiesToCSV,
  type Policy, type PolicyStatus, type PolicyCategory, type SortKey, type SortDir,
} from "../components/policies/policiesData";

export default function PoliciesPage() {
  const { lang } = useLang();
  const s = POL_STR[lang as PolLang];
  const locale = localeOf(lang as PolLang);

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | PolicyStatus>("all");
  const [catFilter, setCatFilter] = useState<"all" | PolicyCategory>("all");
  const [sortKey, setSortKey] = useState<SortKey>("updated");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [open, setOpen] = useState<Policy | null>(null);
  const [exported, setExported] = useState(false);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    const list = POLICIES.filter((p) =>
      (statusFilter === "all" || p.status === statusFilter) &&
      (catFilter === "all" || p.category === catFilter) &&
      (q === "" || polText(s, p.titleKey).toLowerCase().includes(q) || polText(s, p.summaryKey).toLowerCase().includes(q))
    );
    list.sort((a, b) => {
      let cmp = 0;
      if (sortKey === "updated") cmp = +new Date(a.updated) - +new Date(b.updated);
      else if (sortKey === "version") cmp = compareVersion(a.version, b.version);
      else cmp = polText(s, a.titleKey).localeCompare(polText(s, b.titleKey));
      return sortDir === "asc" ? cmp : -cmp;
    });
    return list;
  }, [search, statusFilter, catFilter, sortKey, sortDir, lang]); // eslint-disable-line react-hooks/exhaustive-deps

  const buildDoc = (p: Policy) =>
    [
      polText(s, p.titleKey),
      `${s.version}: ${p.version}   •   ${s.updated}: ${formatDate(p.updated, locale)}`,
      `${s.status}: ${statusText(s, p.status)}   •   ${catText(s, p.category)}`,
      "", polText(s, p.summaryKey), "",
      ...p.clauses.map((c, i) => `${i + 1}. ${polText(s, c.key)}`), "",
    ].join("\n");

  const downloadOne = (p: Policy) => downloadText(`${p.id}-${p.version}.txt`, buildDoc(p));
  const exportAll = () => {
    const headers = s.csvHeaders.split(",");
    const rows = filtered.map((p) => [p.id, polText(s, p.titleKey), catText(s, p.category), p.version, statusText(s, p.status), p.updated.slice(0, 10)]);
    downloadCSV("policies.csv", policiesToCSV(filtered, () => [], headers).replace(/\n$/, "") === headers.join(",") ? [headers.join(",")].join("\n") : policiesToCSV(filtered, (p) => [p.id, polText(s, p.titleKey), catText(s, p.category), p.version, statusText(s, p.status), p.updated.slice(0, 10)], headers));
    void rows;
    setExported(true); setTimeout(() => setExported(false), 1800);
  };

  const selectCls = "rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm font-bold text-stone-700 outline-none focus:border-green-500 focus:ring-2 focus:ring-green-500/15";

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-5 sm:p-8">
      <SectionReveal>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-xl bg-green-50 ring-1 ring-green-600/15">
              <Scale className="h-5 w-5 text-green-700" />
            </div>
            <div>
              <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
              <p className="mt-0.5 text-stone-600">{s.subtitle}</p>
            </div>
          </div>
          <button onClick={exportAll} disabled={filtered.length === 0}
            className={`inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-bold shadow-sm transition-all hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50 ${exported ? "bg-green-50 text-green-700" : "bg-green-600 text-white hover:bg-green-700"}`}>
            {exported ? <Check className="h-4 w-4" /> : <Download className="h-4 w-4" />}{s.exportAll}
          </button>
        </div>
      </SectionReveal>

      <PolicyStats policies={POLICIES} strings={s} />

      {/* دسته‌بندی‌ها به‌عنوان فیلتر سریع */}
      <SectionReveal delay={90}>
        <div>
          <p className="mb-2 text-xs font-bold uppercase tracking-wide text-stone-400">{s.categoriesTitle}</p>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
            {CATEGORY_ORDER.map((c) => {
              const Icon = CATEGORY_ICON[c];
              const active = catFilter === c;
              return (
                <button key={c} onClick={() => setCatFilter(active ? "all" : c)}
                  className={`flex items-center gap-2.5 rounded-2xl border p-3 text-start transition-all hover:-translate-y-0.5 hover:shadow-sm ${active ? "border-green-400 bg-green-50/60 ring-1 ring-green-600/15" : "border-stone-200 bg-white"}`}>
                  <span className={`grid h-9 w-9 shrink-0 place-items-center rounded-xl ${active ? "bg-green-600 text-white" : "bg-stone-100 text-stone-600"}`}>
                    <Icon className="h-4 w-4" />
                  </span>
                  <span className="min-w-0">
                    <span className="block truncate text-xs font-bold text-stone-800">{catText(s, c)}</span>
                    <span className="block text-[11px] tabular-nums text-stone-500">{countByCategory(POLICIES, c)}</span>
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </SectionReveal>

      {/* toolbar */}
      <SectionReveal delay={110}>
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative min-w-[200px] flex-1">
            <Search className="pointer-events-none absolute top-1/2 start-3 h-4 w-4 -translate-y-1/2 text-stone-400" />
            <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder={s.searchPlaceholder}
              className="w-full rounded-xl border border-stone-200 bg-white py-2.5 ps-9 pe-3 text-sm text-stone-800 outline-none transition-colors placeholder:text-stone-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/15" />
          </div>
          <div className="flex flex-wrap items-center gap-1 rounded-full border border-stone-200 bg-white p-1">
            {STATUS_FILTERS.map((f) => (
              <button key={f} onClick={() => setStatusFilter(f)}
                className={`rounded-full px-3 py-1.5 text-xs font-bold transition-colors ${statusFilter === f ? "bg-green-600 text-white shadow-sm" : "text-stone-600 hover:bg-stone-100"}`}>
                {f === "all" ? s.filterAllStatus : statusText(s, f)}
              </button>
            ))}
          </div>
          <select value={`${sortKey}-${sortDir}`}
            onChange={(e) => { const [k, dd] = e.target.value.split("-") as [SortKey, SortDir]; setSortKey(k); setSortDir(dd); }}
            className={selectCls} aria-label={s.sortLabel}>
            <option value="updated-desc">{s.sortUpdated} ↓</option>
            <option value="updated-asc">{s.sortUpdated} ↑</option>
            <option value="version-desc">{s.sortVersion} ↓</option>
            <option value="version-asc">{s.sortVersion} ↑</option>
            <option value="title-asc">{s.sortTitle} ↑</option>
          </select>
        </div>
      </SectionReveal>

      <SectionReveal delay={130}>
        <PolicyList policies={filtered} strings={s} lang={lang as PolLang} onView={setOpen} onDownload={downloadOne} />
      </SectionReveal>

      <PolicyDetailModal policy={open} strings={s} lang={lang as PolLang} onClose={() => setOpen(null)} />
    </div>
  );
}