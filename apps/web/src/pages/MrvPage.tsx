// apps/web/src/pages/MrvPage.tsx — live API when available; no fake project table
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Recycle, Download, Search, Check, Loader2 } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { MrvStats } from "../components/mrv/MrvStats";
import { MrvTable } from "../components/mrv/MrvTable";
import { SafeguardsPanel } from "../components/mrv/SafeguardsPanel";
import { MRV_STR, mrvText, statusText, localeOf, type MrvLang } from "../components/mrv/mrvI18n";
import {
  INITIAL_SAFEGUARDS,
  STATUS_FILTERS,
  mrvToCSV,
  downloadCSV,
  type MrvReport,
  type MrvStatus,
  type Safeguard,
  type SortKey,
  type SortDir,
} from "../components/mrv/mrvData";
import { MrvNavGrid } from "./MrvHubPages";
import { apiFetch, v1 } from "../api/http";

export default function MrvPage() {
  const { lang } = useLang();
  const s = MRV_STR[lang as MrvLang];

  const [reports, setReports] = useState<MrvReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [apiNote, setApiNote] = useState<string | null>(null);
  const [safeguards, setSafeguards] = useState<Safeguard[]>(INITIAL_SAFEGUARDS);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | MrvStatus>("all");
  const [sortKey, setSortKey] = useState<SortKey>("date");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [exported, setExported] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        // Prefer standards / claims endpoints if present
        const data = await apiFetch<{ data?: unknown[]; items?: unknown[] }>(
          v1("/mrv/standards/projects"),
          {},
          10_000,
        ).catch(() => null);
        const raw = (data?.data || data?.items || []) as Array<Record<string, unknown>>;
        if (!cancelled && raw.length) {
          setReports(
            raw.map((r, i) => ({
              id: String(r.id ?? `mrv-${i}`),
              projectKey: String(r.name ?? r.project ?? r.id ?? `p${i}`),
              status: (String(r.status ?? "pending") as MrvStatus) || "pending",
              date: String(r.date ?? r.created_at ?? new Date().toISOString()),
              methodology: String(r.methodology ?? "—"),
              carbon: Number(r.carbon ?? r.tco2e ?? 0),
            })) as MrvReport[],
          );
          setApiNote(null);
        } else if (!cancelled) {
          setReports([]);
          setApiNote(
            lang === "fa"
              ? "هنوز پروژه MRV در دیتابیس نیست — داده نمایشی حذف شد. از /mrv/claim یا science/e2e ثبت کنید."
              : "No MRV projects in database yet — demo rows removed. Use claim or science E2E.",
          );
        }
      } catch (e) {
        if (!cancelled) {
          setReports([]);
          setApiNote(e instanceof Error ? e.message : "API error");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [lang]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    const list = reports.filter(
      (r) =>
        (statusFilter === "all" || r.status === statusFilter) &&
        (q === "" ||
          mrvText(s, r.projectKey).toLowerCase().includes(q) ||
          r.id.toLowerCase().includes(q) ||
          r.projectKey.toLowerCase().includes(q)),
    );
    list.sort((a, b) => {
      const cmp =
        sortKey === "date" ? +new Date(a.date) - +new Date(b.date) : a.carbon - b.carbon;
      return sortDir === "asc" ? cmp : -cmp;
    });
    return list;
  }, [reports, statusFilter, search, sortKey, sortDir, s]);

  const onSort = (k: SortKey) => {
    if (k === sortKey) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else {
      setSortKey(k);
      setSortDir("desc");
    }
  };

  const verify = (id: string) =>
    setReports((prev) => prev.map((r) => (r.id === id ? { ...r, status: "verified" as MrvStatus } : r)));
  const reject = (id: string) =>
    setReports((prev) =>
      prev.map((r) => (r.id === id ? { ...r, status: "rejected" as MrvStatus, carbon: 0 } : r)),
    );
  const toggleSafeguard = (id: string) =>
    setSafeguards((prev) => prev.map((sg) => (sg.id === id ? { ...sg, passed: !sg.passed } : sg)));

  const resolveRow = (r: MrvReport) => [
    r.id,
    r.projectKey,
    statusText(s, r.status),
    r.date.slice(0, 10),
    r.methodology,
    String(r.carbon),
  ];
  const headers = s.csvHeaders.split(",");
  const exportAll = () => {
    downloadCSV("mrv-reports.csv", mrvToCSV(filtered, resolveRow, headers));
    setExported(true);
    setTimeout(() => setExported(false), 1800);
  };
  const exportOne = (r: MrvReport) => downloadCSV(`${r.id}.csv`, mrvToCSV([r], resolveRow, headers));

  const selectCls =
    "rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm font-bold text-stone-700 outline-none focus:border-green-500 focus:ring-2 focus:ring-green-500/15";

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
      <SectionReveal>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-xl bg-emerald-50 ring-1 ring-emerald-600/15">
              <Recycle className="h-5 w-5 text-emerald-700" />
            </div>
            <div>
              <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
              <p className="mt-0.5 text-stone-600">{s.subtitle}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={exportAll}
            disabled={filtered.length === 0}
            className={`inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-bold shadow-sm transition-all hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50 ${
              exported ? "bg-green-50 text-green-700" : "bg-green-600 text-white hover:bg-green-700"
            }`}
          >
            {exported ? <Check className="h-4 w-4" /> : <Download className="h-4 w-4" />}
            {s.exportAll}
          </button>
        </div>
      </SectionReveal>

      <SectionReveal delay={40}>
        <MrvNavGrid />
      </SectionReveal>

      {apiNote && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          {apiNote}{" "}
          <Link className="font-bold underline" to="/science/e2e">
            Science E2E
          </Link>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-emerald-600" />
        </div>
      ) : (
        <>
          <MrvStats reports={reports} strings={s} lang={lang as MrvLang} />
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <div className="space-y-4 lg:col-span-2">
              <SectionReveal delay={100}>
                <div className="flex flex-wrap items-center gap-3">
                  <div className="relative min-w-[200px] flex-1">
                    <Search className="pointer-events-none absolute top-1/2 start-3 h-4 w-4 -translate-y-1/2 text-stone-400" />
                    <input
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                      placeholder={s.searchPlaceholder}
                      className="w-full rounded-xl border border-stone-200 bg-white py-2.5 ps-9 pe-3 text-sm"
                    />
                  </div>
                  <div className="flex flex-wrap items-center gap-1 rounded-full border border-stone-200 bg-white p-1">
                    {STATUS_FILTERS.map((f) => (
                      <button
                        key={f}
                        type="button"
                        onClick={() => setStatusFilter(f)}
                        className={`rounded-full px-3 py-1.5 text-xs font-bold ${
                          statusFilter === f ? "bg-green-600 text-white" : "text-stone-600"
                        }`}
                      >
                        {f === "all" ? s.filterAll : statusText(s, f)}
                      </button>
                    ))}
                  </div>
                  <select
                    value={`${sortKey}-${sortDir}`}
                    onChange={(e) => {
                      const [k, d] = e.target.value.split("-") as [SortKey, SortDir];
                      setSortKey(k);
                      setSortDir(d);
                    }}
                    className={selectCls}
                  >
                    <option value="date-desc">{s.sortDate} ↓</option>
                    <option value="date-asc">{s.sortDate} ↑</option>
                    <option value="carbon-desc">{s.sortCarbon} ↓</option>
                    <option value="carbon-asc">{s.sortCarbon} ↑</option>
                  </select>
                </div>
              </SectionReveal>
              <SectionReveal delay={120}>
                {filtered.length === 0 ? (
                  <div className="rounded-2xl border border-dashed border-stone-300 py-16 text-center text-sm text-stone-500">
                    {lang === "fa" ? "لیست خالی — بدون داده آزمایشی" : "Empty list — no demo data"}
                  </div>
                ) : (
                  <MrvTable
                    reports={filtered}
                    strings={s}
                    lang={lang as MrvLang}
                    sortKey={sortKey}
                    sortDir={sortDir}
                    onSort={onSort}
                    onVerify={verify}
                    onReject={reject}
                    onDownloadOne={exportOne}
                  />
                )}
              </SectionReveal>
            </div>
            <div className="lg:col-span-1">
              <SafeguardsPanel
                safeguards={safeguards}
                strings={s}
                lang={lang as MrvLang}
                onToggle={toggleSafeguard}
              />
            </div>
          </div>
        </>
      )}
    </div>
  );
}
