// apps/web/src/components/reports/ReportPreviewModal.tsx
// پیش‌نمایش (الهام Brilliant: ببین قبل از آنکه بگیری) + دانلود/اشتراک.
import { useEffect, useState } from "react";
import { X, Download, Share2, Check } from "lucide-react";
import type { Report } from "./reportsData";
import { REPORT_TEMPLATE, formatDate, downloadText, copyToClipboard, reportShareLink } from "./reportsData";
import { TYPE_ICON } from "./ReportsTable";
import {
  reportName, typeText, statusText, periodText, repText, unitText, buildReportDoc, localeOf,
  type ReportStrings, type RepLang,
} from "./reportsI18n";

interface Props { report: Report | null; strings: ReportStrings; lang: RepLang; onClose: () => void; }

export function ReportPreviewModal({ report: r, strings: s, lang, onClose }: Props) {
  const locale = localeOf(lang);
  const [shared, setShared] = useState(false);
  useEffect(() => {
    if (!r) return;
    setShared(false);
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [r, onClose]);

  if (!r) return null;
  const Icon = TYPE_ICON[r.type];
  const tpl = REPORT_TEMPLATE[r.type];
  const name = reportName(r, s);

  const download = () => downloadText(`${r.id}.txt`, buildReportDoc(r, s, locale));
  const share = async () => {
    const ok = await copyToClipboard(reportShareLink(r.id));
    if (ok) { setShared(true); setTimeout(() => setShared(false), 1800); }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div onClick={onClose} className="absolute inset-0 bg-stone-900/40 backdrop-blur-sm" style={{ animation: "fade-in .2s ease-out" }} />
      <div role="dialog" aria-modal="true" aria-label={name}
        className="relative flex max-h-[90vh] w-full max-w-2xl flex-col overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-xl"
        style={{ animation: "fade-up .25s var(--ease-out)" }}>
        <div className="flex items-start justify-between gap-3 border-b border-stone-100 p-5 sm:p-6">
          <div className="flex items-start gap-3">
            <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-green-50 text-green-700 ring-1 ring-green-600/15"><Icon className="h-5 w-5" /></span>
            <div>
              <h2 className="font-display text-xl text-stone-800">{name}</h2>
              <p className="mt-1 text-xs text-stone-500">{typeText(s, r.type)} · {periodText(s, r.period)} · {statusText(s, r.status)} · {formatDate(r.date, locale)}</p>
            </div>
          </div>
          <button onClick={onClose} className="grid h-8 w-8 shrink-0 place-items-center rounded-lg text-stone-500 transition-colors hover:bg-stone-100"><X className="h-4 w-4" /></button>
        </div>

        <div className="flex-1 space-y-5 overflow-y-auto p-5 sm:p-6">
          <div>
            <p className="mb-1.5 text-[11px] font-bold uppercase tracking-wide text-stone-400">{s.summaryLabel}</p>
            <p className="rounded-xl bg-stone-50 p-4 text-sm leading-relaxed text-stone-700">{repText(s, tpl.summaryKey)}</p>
          </div>
          <div>
            <p className="mb-2 text-[11px] font-bold uppercase tracking-wide text-stone-400">{s.metricsLabel}</p>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
              {tpl.metrics.map((m) => {
                const u = unitText(s, m.unitKey);
                return (
                  <div key={m.labelKey} className="rounded-xl border border-stone-200 bg-white p-4 text-center shadow-sm">
                    <p className="font-display text-2xl font-black tabular-nums text-stone-800">{m.value.toLocaleString(locale)}</p>
                    <p className="mt-1 text-xs font-medium text-stone-600">{repText(s, m.labelKey)}{u ? ` · ${u}` : ""}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-2 border-t border-stone-100 p-4">
          <button onClick={download} className="inline-flex flex-1 items-center justify-center gap-1.5 rounded-xl bg-green-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-green-700"><Download className="h-4 w-4" />{s.download}</button>
          <button onClick={share} className={`inline-flex items-center justify-center gap-1.5 rounded-xl px-4 py-2.5 text-sm font-bold transition-colors ${shared ? "bg-green-50 text-green-700" : "border border-stone-200 text-stone-700 hover:bg-stone-50"}`}>{shared ? <><Check className="h-4 w-4" />{s.shared}</> : <><Share2 className="h-4 w-4" />{s.share}</>}</button>
          <button onClick={onClose} className="rounded-xl border border-stone-200 px-4 py-2.5 text-sm font-bold text-stone-700 transition-colors hover:bg-stone-50">{s.close}</button>
        </div>
      </div>
    </div>
  );
}