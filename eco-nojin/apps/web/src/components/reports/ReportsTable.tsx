// apps/web/src/components/reports/ReportsTable.tsx
import { DollarSign, Leaf, Recycle, BarChart3, FileText, Download, Share2, Eye, Check, ArrowUp, ArrowDown, ArrowUpDown } from "lucide-react";
import type { Report, ReportType, ReportStatus, SortKey, SortDir } from "./reportsData";
import { formatDate } from "./reportsData";
import { reportName, typeText, statusText, localeOf, type ReportStrings, type RepLang } from "./reportsI18n";

export const TYPE_ICON: Record<ReportType, typeof FileText> = {
  financial: DollarSign, impact: Leaf, mrv: Recycle, analytics: BarChart3,
};
const TYPE_ACCENT: Record<ReportType, string> = {
  financial: "bg-blue-50 text-blue-700 ring-blue-600/15",
  impact: "bg-green-50 text-green-700 ring-green-600/15",
  mrv: "bg-emerald-50 text-emerald-700 ring-emerald-600/15",
  analytics: "bg-violet-50 text-violet-700 ring-violet-600/15",
};
const STATUS_STYLE: Record<ReportStatus, string> = {
  published: "bg-green-50 text-green-700 ring-green-600/15",
  draft: "bg-amber-50 text-amber-700 ring-amber-600/15",
  generating: "bg-blue-50 text-blue-700 ring-blue-600/15",
};

interface Props {
  reports: Report[];
  strings: ReportStrings;
  lang: RepLang;
  sharedId: string | null;
  sortKey: SortKey;
  sortDir: SortDir;
  onSort: (k: SortKey) => void;
  onPreview: (r: Report) => void;
  onDownload: (r: Report) => void;
  onShare: (r: Report) => void;
}

function SortIcon({ active, dir }: { active: boolean; dir: SortDir }) {
  if (!active) return <ArrowUpDown className="h-3.5 w-3.5 opacity-40" />;
  return dir === "asc" ? <ArrowUp className="h-3.5 w-3.5" /> : <ArrowDown className="h-3.5 w-3.5" />;
}

export function ReportsTable({ reports, strings: s, lang, sharedId, sortKey, sortDir, onSort, onPreview, onDownload, onShare }: Props) {
  const locale = localeOf(lang);

  if (reports.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-stone-300 bg-white py-16 text-center">
        <FileText className="h-10 w-10 text-stone-300" />
        <p className="text-stone-500">{s.noReports}</p>
      </div>
    );
  }

  const thBase = "p-4 text-start text-xs font-bold uppercase tracking-wide text-stone-500";

  return (
    <div className="overflow-hidden rounded-2xl border border-stone-200/80 bg-white shadow-sm">
      {/* دسکتاپ */}
      <div className="hidden overflow-x-auto md:block">
        <table className="w-full min-w-[760px] border-collapse text-sm">
          <thead>
            <tr className="border-b border-stone-200 bg-stone-50">
              <th scope="col" className={thBase}>
                <button onClick={() => onSort("name")} className="inline-flex items-center gap-1 hover:text-stone-700">{s.colName}<SortIcon active={sortKey === "name"} dir={sortDir} /></button>
              </th>
              <th scope="col" className={thBase}>
                <button onClick={() => onSort("date")} className="inline-flex items-center gap-1 hover:text-stone-700">{s.colDate}<SortIcon active={sortKey === "date"} dir={sortDir} /></button>
              </th>
              <th scope="col" className={thBase}>{s.colType}</th>
              <th scope="col" className={thBase}>{s.colStatus}</th>
              <th scope="col" className={`${thBase} !text-end`}>
                <button onClick={() => onSort("downloads")} className="inline-flex items-center gap-1 hover:text-stone-700">{s.statDownloads}<SortIcon active={sortKey === "downloads"} dir={sortDir} /></button>
              </th>
              <th scope="col" className={`${thBase} !text-end`}>{s.colActions}</th>
            </tr>
          </thead>
          <tbody>
            {reports.map((r) => {
              const Icon = TYPE_ICON[r.type];
              const shared = sharedId === r.id;
              return (
                <tr key={r.id} className="border-b border-stone-100 transition-colors last:border-0 hover:bg-stone-50">
                  <td className="p-4">
                    <div className="flex items-center gap-2.5">
                      <span className={`grid h-9 w-9 shrink-0 place-items-center rounded-xl ring-1 ${TYPE_ACCENT[r.type]}`}><Icon className="h-4 w-4" /></span>
                      <span className="font-semibold text-stone-800">{reportName(r, s)}</span>
                    </div>
                  </td>
                  <td className="p-4 text-stone-600">{formatDate(r.date, locale)}</td>
                  <td className="p-4"><span className={`rounded-full px-2 py-0.5 text-[11px] font-bold ring-1 ${TYPE_ACCENT[r.type]}`}>{typeText(s, r.type)}</span></td>
                  <td className="p-4"><span className={`rounded-full px-2 py-0.5 text-[11px] font-bold ring-1 ${STATUS_STYLE[r.status]}`}>{statusText(s, r.status)}</span></td>
                  <td className="p-4 text-end font-display font-black tabular-nums text-stone-700">{r.downloads.toLocaleString(locale)}</td>
                  <td className="p-4">
                    <div className="flex items-center justify-end gap-1">
                      <button onClick={() => onPreview(r)} title={s.preview} className="grid h-8 w-8 place-items-center rounded-lg text-stone-500 transition-colors hover:bg-stone-100 hover:text-green-700"><Eye className="h-4 w-4" /></button>
                      <button onClick={() => onDownload(r)} title={s.download} className="grid h-8 w-8 place-items-center rounded-lg text-stone-500 transition-colors hover:bg-stone-100 hover:text-green-700"><Download className="h-4 w-4" /></button>
                      <button onClick={() => onShare(r)} title={s.share} className={`grid h-8 w-8 place-items-center rounded-lg transition-colors ${shared ? "bg-green-50 text-green-700" : "text-stone-500 hover:bg-stone-100 hover:text-green-700"}`}>{shared ? <Check className="h-4 w-4" /> : <Share2 className="h-4 w-4" />}</button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* موبایل */}
      <div className="divide-y divide-stone-100 md:hidden">
        {reports.map((r) => {
          const Icon = TYPE_ICON[r.type];
          const shared = sharedId === r.id;
          return (
            <div key={r.id} className="p-4">
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-start gap-2.5">
                  <span className={`grid h-9 w-9 shrink-0 place-items-center rounded-xl ring-1 ${TYPE_ACCENT[r.type]}`}><Icon className="h-4 w-4" /></span>
                  <div>
                    <p className="font-semibold text-stone-800">{reportName(r, s)}</p>
                    <p className="mt-0.5 text-xs text-stone-500">{formatDate(r.date, locale)}</p>
                  </div>
                </div>
                <span className={`rounded-full px-2 py-0.5 text-[11px] font-bold ring-1 ${STATUS_STYLE[r.status]}`}>{statusText(s, r.status)}</span>
              </div>
              <div className="mt-3 flex items-center justify-between">
                <span className={`rounded-full px-2 py-0.5 text-[11px] font-bold ring-1 ${TYPE_ACCENT[r.type]}`}>{typeText(s, r.type)}</span>
                <div className="flex items-center gap-1">
                  <button onClick={() => onPreview(r)} className="grid h-8 w-8 place-items-center rounded-lg text-stone-500 hover:bg-stone-100"><Eye className="h-4 w-4" /></button>
                  <button onClick={() => onDownload(r)} className="grid h-8 w-8 place-items-center rounded-lg text-stone-500 hover:bg-stone-100"><Download className="h-4 w-4" /></button>
                  <button onClick={() => onShare(r)} className={`grid h-8 w-8 place-items-center rounded-lg ${shared ? "bg-green-50 text-green-700" : "text-stone-500 hover:bg-stone-100"}`}>{shared ? <Check className="h-4 w-4" /> : <Share2 className="h-4 w-4" />}</button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}