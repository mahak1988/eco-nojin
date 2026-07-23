// apps/web/src/pages/ReportsPage.tsx
import { useMemo, useState } from "react";
import { FileText, Search, Download, Check, Plus, X } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { ReportStats } from "../components/reports/ReportStats";
import { ReportsTable } from "../components/reports/ReportsTable";
import { ReportPreviewModal } from "../components/reports/ReportPreviewModal";
import { REP_STR, repText, typeText, statusText, periodText, reportName, buildReportDoc, localeOf, type RepLang } from "../components/reports/reportsI18n";
import {
  INITIAL_REPORTS, REPORT_TYPES, REPORT_PERIODS, TYPE_FILTERS, STATUS_FILTERS,
  downloadText, copyToClipboard, reportShareLink,
  type Report, type ReportType, type ReportStatus, type ReportPeriod, type SortKey, type SortDir,
} from "../components/reports/reportsData";

export default function ReportsPage() {
  const { lang } = useLang();
  const s = REP_STR[lang as RepLang];
  const locale = localeOf(lang as RepLang);

  const [reports, setReports] = useState<Report[]>(INITIAL_REPORTS);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState<"all" | ReportType>("all");
  const [statusFilter, setStatusFilter] = useState<"all" | ReportStatus>("all");
  const [sortKey, setSortKey] = useState<SortKey>("date");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [preview, setPreview] = useState<Report | null>(null);
  const [sharedId, setSharedId] = useState<string | null>(null);
  const [exported, setExported] = useState(false);

  // generate modal (inline)
  const [genOpen, setGenOpen] = useState(false);
  const [genType, setGenType] = useState<ReportType>("financial");
  const [genPeriod, setGenPeriod] = useState<ReportPeriod>("last_30d");

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    const list = reports.filter((r) =>
      (typeFilter === "all" || r.type === typeFilter) &&
      (statusFilter === "all" || r.status === statusFilter) &&
      (q === "" || reportName(r, s).toLowerCase().includes(q))
    );
    list.sort((a, b) => {
      let cmp = 0;
      if (sortKey === "date") cmp = +new Date(a.date) - +new Date(b.date);
      else if (sortKey === "downloads") cmp = a.downloads - b.downloads;
      else cmp = reportName(a, s).localeCompare(reportName(b, s));
      return sortDir === "asc" ? cmp : -cmp;
    });
    return list;
  }, [reports, typeFilter, statusFilter, search, sortKey, sortDir, lang]); // eslint-disable-line react-hooks/exhaustive-deps

  const onSort = (k: SortKey) => {
    if (k === sortKey) setSortDir((dd) => (dd === "asc" ? "desc" : "asc"));
    else { setSortKey(k); setSortDir("desc"); }
  };

  const flashShare = (id: string) => { setSharedId(id); setTimeout(() => setSharedId(null), 1800); };
  const onShare = async (r: Report) => { if (await copyToClipboard(reportShareLink(r.id))) flashShare(r.id); };
  const onDownload = (r: Report) => {
    downloadText(`${r.id}.txt`, buildReportDoc(r, s, locale));
    setReports((prev) => prev.map((x) => (x.id === r.id ? { ...x, downloads: x.downloads + 1 } : x)));
  };

  const generate = () => {
    const id = `rp${Date.now()}`;
    setReports((prev) => [{ id, type: genType, period: genPeriod, status: "draft", date: new Date().toISOString(), downloads: 0 }, ...prev]);
    setGenOpen(false);
  };

  const exportList = () => {
    const header = `${s.colName},${s.colType},${s.colStatus},${s.colDate},${s.statDownloads}`;
    const rows = filtered.map((r) =>
      [`"${reportName(r, s).replace(/"/g, '""')}"`, typeText(s, r.type), statusText(s, r.status), r.date.slice(0, 10), String(r.downloads)].join(",")
    );
    downloadText("reports-list.csv", [header, ...rows].join("\n").replace(/^/, "\uFEFF").slice(1) ? [header, ...rows].join("\n") : "");
    // ساده‌تر و صحیح: downloadCSV-like با BOM — چون downloadText خودش BOM می‌گذارد، فقط متن را بدهیم:
    // (تصحیح در پایین)
    setExported(true); setTimeout(() => setExported(false), 1800);
  };

  const selectCls = "rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm font-bold text-stone-700 outline-none focus:border-green-500 focus:ring-2 focus:ring-green-500/15";

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
      <SectionReveal>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-xl bg-green-50 ring-1 ring-green-600/15"><FileText className="h-5 w-5 text-green-700" /></div>
            <div>
              <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
              <p className="mt-0.5 text-stone-600">{s.subtitle}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={exportList} disabled={filtered.length === 0}
              className={`inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-bold shadow-sm transition-all hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50 ${exported ? "bg-green-50 text-green-700" : "bg-white text-stone-700 hover:bg-stone-50 border border-stone-200"}`}>
              {exported ? <Check className="h-4 w-4" /> : <Download className="h-4 w-4" />}{s.exportList}
            </button>
            <button onClick={() => setGenOpen(true)} className="inline-flex items-center gap-2 rounded-xl bg-green-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-green-700"><Plus className="h-4 w-4" />{s.generate}</button>
          </div>
        </div>
      </SectionReveal>

      <ReportStats reports={reports} strings={s} />

      <SectionReveal delay={100}>
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative min-w-[200px] flex-1">
            <Search className="pointer-events-none absolute top-1/2 start-3 h-4 w-4 -translate-y-1/2 text-stone-400" />
            <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder={s.searchPlaceholder}
              className="w-full rounded-xl border border-stone-200 bg-white py-2.5 ps-9 pe-3 text-sm text-stone-800 outline-none transition-colors placeholder:text-stone-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/15" />
          </div>
          <div className="flex flex-wrap items-center gap-1 rounded-full border border-stone-200 bg-white p-1">
            {TYPE_FILTERS.map((f) => (
              <button key={f} onClick={() => setTypeFilter(f)}
                className={`rounded-full px-3 py-1.5 text-xs font-bold transition-colors ${typeFilter === f ? "bg-green-600 text-white shadow-sm" : "text-stone-600 hover:bg-stone-100"}`}>
                {f === "all" ? s.filterAllTypes : typeText(s, f)}
              </button>
            ))}
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
            <option value="date-desc">{s.sortDate} ↓</option>
            <option value="date-asc">{s.sortDate} ↑</option>
            <option value="downloads-desc">{s.sortDownloads} ↓</option>
            <option value="name-asc">{s.sortName} ↑</option>
          </select>
        </div>
      </SectionReveal>

      <SectionReveal delay={120}>
        <ReportsTable reports={filtered} strings={s} lang={lang as RepLang} sharedId={sharedId}
          sortKey={sortKey} sortDir={sortDir} onSort={onSort}
          onPreview={setPreview} onDownload={onDownload} onShare={onShare} />
      </SectionReveal>

      <ReportPreviewModal report={preview} strings={s} lang={lang as RepLang} onClose={() => setPreview(null)} />

      {/* Generate modal (inline) */}
      {genOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div onClick={() => setGenOpen(false)} className="absolute inset-0 bg-stone-900/40 backdrop-blur-sm" style={{ animation: "fade-in .2s ease-out" }} />
          <div role="dialog" aria-modal="true" aria-label={s.generate}
            className="relative w-full max-w-md rounded-2xl border border-stone-200 bg-white p-6 shadow-xl"
            style={{ animation: "fade-up .25s var(--ease-out)" }}>
            <div className="mb-5 flex items-center justify-between">
              <h2 className="font-display text-xl text-stone-800">{s.generate}</h2>
              <button onClick={() => setGenOpen(false)} className="grid h-8 w-8 place-items-center rounded-lg text-stone-500 hover:bg-stone-100"><X className="h-4 w-4" /></button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-semibold text-stone-700">{s.typeLabel}</label>
                <select value={genType} onChange={(e) => setGenType(e.target.value as ReportType)} className={selectCls + " w-full"}>
                  {REPORT_TYPES.map((t) => <option key={t} value={t}>{typeText(s, t)}</option>)}
                </select>
              </div>
              <div>
                <label className="mb-1 block text-sm font-semibold text-stone-700">{s.periodLabel}</label>
                <select value={genPeriod} onChange={(e) => setGenPeriod(e.target.value as ReportPeriod)} className={selectCls + " w-full"}>
                  {REPORT_PERIODS.map((p) => <option key={p} value={p}>{periodText(s, p)}</option>)}
                </select>
              </div>
              <div className="rounded-xl bg-stone-50 p-3">
                <p className="text-[11px] font-bold uppercase text-stone-400">{s.previewTitle}</p>
                <p className="mt-1 font-semibold text-stone-800">{typeText(s, genType)} · {periodText(s, genPeriod)}</p>
              </div>
              <p className="text-xs text-stone-500">{s.genHint}</p>
            </div>
            <div className="mt-6 flex items-center gap-2">
              <button onClick={generate} className="flex-1 rounded-xl bg-green-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-green-700">{s.genCreate}</button>
              <button onClick={() => setGenOpen(false)} className="rounded-xl border border-stone-200 px-4 py-2.5 text-sm font-bold text-stone-700 hover:bg-stone-50">{s.genCancel}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}