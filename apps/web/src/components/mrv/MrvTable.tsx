// apps/web/src/components/mrv/MrvTable.tsx
// table دسکتاپ (a11y) + card موبایل + verify/reject برای pending.
import { Recycle, CheckCircle2, Clock, XCircle, Download, FileText, Check, Ban, ArrowUp, ArrowDown, ArrowUpDown } from "lucide-react";
import type { MrvReport, MrvStatus, SortKey, SortDir } from "./mrvData";
import { formatCarbon, formatDate } from "./mrvData";
import { mrvText, statusText, localeOf, type MrvStrings, type MrvLang } from "./mrvI18n";

const STATUS_STYLE: Record<MrvStatus, { icon: typeof CheckCircle2; chip: string }> = {
  verified: { icon: CheckCircle2, chip: "bg-green-50 text-green-700 ring-green-600/15" },
  pending: { icon: Clock, chip: "bg-amber-50 text-amber-700 ring-amber-600/15" },
  rejected: { icon: XCircle, chip: "bg-red-50 text-red-700 ring-red-600/15" },
};

interface Props {
  reports: MrvReport[];
  strings: MrvStrings;
  lang: MrvLang;
  sortKey: SortKey;
  sortDir: SortDir;
  onSort: (k: SortKey) => void;
  onVerify: (id: string) => void;
  onReject: (id: string) => void;
  onDownloadOne: (r: MrvReport) => void;
}

function SortIcon({ active, dir }: { active: boolean; dir: SortDir }) {
  if (!active) return <ArrowUpDown className="h-3.5 w-3.5 opacity-40" />;
  return dir === "asc" ? <ArrowUp className="h-3.5 w-3.5" /> : <ArrowDown className="h-3.5 w-3.5" />;
}

function StatusBadge({ status, strings: s }: { status: MrvStatus; strings: MrvStrings }) {
  const cfg = STATUS_STYLE[status];
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-bold ring-1 ${cfg.chip}`}>
      <cfg.icon className="h-3.5 w-3.5" />{statusText(s, status)}
    </span>
  );
}

export function MrvTable({ reports, strings: s, lang, sortKey, sortDir, onSort, onVerify, onReject, onDownloadOne }: Props) {
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
      {/* ── دسکتاپ ── */}
      <div className="hidden overflow-x-auto md:block">
        <table className="w-full min-w-[760px] border-collapse text-sm">
          <thead>
            <tr className="border-b border-stone-200 bg-stone-50">
              <th scope="col" className={thBase}>{s.colProject}</th>
              <th scope="col" className={thBase}>
                <button onClick={() => onSort("date")} className="inline-flex items-center gap-1 hover:text-stone-700">
                  {s.colDate}<SortIcon active={sortKey === "date"} dir={sortDir} />
                </button>
              </th>
              <th scope="col" className={thBase}>{s.colMethod}</th>
              <th scope="col" className={`${thBase} !text-end`}>
                <button onClick={() => onSort("carbon")} className="inline-flex items-center gap-1 hover:text-stone-700">
                  {s.colCarbon}<SortIcon active={sortKey === "carbon"} dir={sortDir} />
                </button>
              </th>
              <th scope="col" className={thBase}>{s.colStatus}</th>
              <th scope="col" className={`${thBase} !text-end`}>{s.colActions}</th>
            </tr>
          </thead>
          <tbody>
            {reports.map((r) => (
              <tr key={r.id} className="border-b border-stone-100 transition-colors last:border-0 hover:bg-stone-50">
                <td className="p-4">
                  <div className="flex items-center gap-2.5">
                    <span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-emerald-50 text-emerald-700 ring-1 ring-emerald-600/15">
                      <Recycle className="h-4 w-4" />
                    </span>
                    <div>
                      <p className="font-semibold text-stone-800">{mrvText(s, r.projectKey)}</p>
                      <p className="font-mono text-[11px] text-stone-400">{r.id}</p>
                    </div>
                  </div>
                </td>
                <td className="p-4 text-stone-600">{formatDate(r.date, locale)}</td>
                <td className="p-4">
                  <span className="rounded-md bg-stone-100 px-2 py-1 text-xs font-bold text-stone-600">{mrvText(s, r.methodology)}</span>
                </td>
                <td className="p-4 text-end font-display font-black tabular-nums text-stone-800">
                  {r.status === "verified" ? `${formatCarbon(r.carbon, locale)} ${s.carbonUnit}` : "—"}
                </td>
                <td className="p-4"><StatusBadge status={r.status} strings={s} /></td>
                <td className="p-4">
                  <div className="flex items-center justify-end gap-1">
                    {r.status === "pending" && (
                      <>
                        <button onClick={() => onVerify(r.id)} title={s.verify}
                          className="inline-flex items-center gap-1 rounded-lg bg-green-50 px-2.5 py-1.5 text-xs font-bold text-green-700 transition-colors hover:bg-green-100">
                          <Check className="h-3.5 w-3.5" />{s.verify}
                        </button>
                        <button onClick={() => onReject(r.id)} title={s.reject}
                          className="inline-flex items-center gap-1 rounded-lg bg-red-50 px-2.5 py-1.5 text-xs font-bold text-red-700 transition-colors hover:bg-red-100">
                          <Ban className="h-3.5 w-3.5" />{s.reject}
                        </button>
                      </>
                    )}
                    <button onClick={() => onDownloadOne(r)} title={s.download}
                      className="inline-grid h-8 w-8 place-items-center rounded-lg text-stone-500 transition-colors hover:bg-stone-100 hover:text-green-700">
                      <Download className="h-4 w-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* ── موبایل ── */}
      <div className="divide-y divide-stone-100 md:hidden">
        {reports.map((r) => (
          <div key={r.id} className="p-4">
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-start gap-2.5">
                <span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-emerald-50 text-emerald-700 ring-1 ring-emerald-600/15">
                  <Recycle className="h-4 w-4" />
                </span>
                <div>
                  <p className="font-semibold text-stone-800">{mrvText(s, r.projectKey)}</p>
                  <p className="mt-0.5 text-xs text-stone-500">{formatDate(r.date, locale)} · {mrvText(s, r.methodology)}</p>
                </div>
              </div>
              <StatusBadge status={r.status} strings={s} />
            </div>
            <div className="mt-3 flex items-center justify-between">
              <span className="font-display text-lg font-black tabular-nums text-stone-800">
                {r.status === "verified" ? `${formatCarbon(r.carbon, locale)} ${s.carbonUnit}` : "—"}
              </span>
              <div className="flex items-center gap-1">
                {r.status === "pending" && (
                  <>
                    <button onClick={() => onVerify(r.id)} className="rounded-lg bg-green-50 px-2.5 py-1.5 text-xs font-bold text-green-700">{s.verify}</button>
                    <button onClick={() => onReject(r.id)} className="rounded-lg bg-red-50 px-2.5 py-1.5 text-xs font-bold text-red-700">{s.reject}</button>
                  </>
                )}
                <button onClick={() => onDownloadOne(r)} className="grid h-8 w-8 place-items-center rounded-lg text-stone-500 hover:bg-stone-100">
                  <Download className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}