// apps/web/src/components/policies/PolicyDetailModal.tsx
// نمایش متن کامل سیاست (بندهای شماره‌گذاری‌شده) + دانلود.
import { useEffect } from "react";
import { X, Download } from "lucide-react";
import type { Policy } from "./policiesData";
import { formatDate, downloadText } from "./policiesData";
import { CATEGORY_ICON } from "./PolicyList";
import { polText, statusText, catText, localeOf, type PolicyStrings, type PolLang } from "./policiesI18n";

interface Props { policy: Policy | null; strings: PolicyStrings; lang: PolLang; onClose: () => void; }

export function PolicyDetailModal({ policy: p, strings: s, lang, onClose }: Props) {
  const locale = localeOf(lang);
  useEffect(() => {
    if (!p) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [p, onClose]);

  if (!p) return null;
  const Icon = CATEGORY_ICON[p.category];
  const title = polText(s, p.titleKey);

  const buildDoc = () =>
    [
      title,
      "=".repeat(Math.max(title.length, 12)),
      `${s.version}: ${p.version}   •   ${s.updated}: ${formatDate(p.updated, locale)}`,
      `${s.status}: ${statusText(s, p.status)}   •   ${catText(s, p.category)}`,
      "",
      polText(s, p.summaryKey),
      "",
      ...p.clauses.map((c, i) => `${i + 1}. ${polText(s, c.key)}`),
      "",
    ].join("\n");

  const download = () => downloadText(`${p.id}-${p.version}.txt`, buildDoc());

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div onClick={onClose} className="absolute inset-0 bg-stone-900/40 backdrop-blur-sm" style={{ animation: "fade-in .2s ease-out" }} />
      <div role="dialog" aria-modal="true" aria-label={title}
        className="relative flex max-h-[90vh] w-full max-w-2xl flex-col overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-xl"
        style={{ animation: "fade-up .25s var(--ease-out)" }}>
        <div className="flex items-start justify-between gap-3 border-b border-stone-100 p-5 sm:p-6">
          <div className="flex items-start gap-3">
            <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-green-50 text-green-700 ring-1 ring-green-600/15">
              <Icon className="h-5 w-5" />
            </span>
            <div>
              <h2 className="font-display text-xl text-stone-800">{title}</h2>
              <p className="mt-1 text-xs text-stone-500">
                {s.version} {p.version} · {s.updated} {formatDate(p.updated, locale)} · {statusText(s, p.status)}
              </p>
            </div>
          </div>
          <button onClick={onClose} className="grid h-8 w-8 shrink-0 place-items-center rounded-lg text-stone-500 transition-colors hover:bg-stone-100">
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="flex-1 space-y-4 overflow-y-auto p-5 sm:p-6">
          <p className="rounded-xl bg-stone-50 p-4 text-sm leading-relaxed text-stone-700">{polText(s, p.summaryKey)}</p>
          <ol className="space-y-3">
            {p.clauses.map((c, i) => (
              <li key={c.key} className="flex items-start gap-3">
                <span className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-green-100 text-xs font-black text-green-700">
                  {(i + 1).toLocaleString(locale)}
                </span>
                <p className="pt-0.5 text-sm leading-relaxed text-stone-700">{polText(s, c.key)}</p>
              </li>
            ))}
          </ol>
        </div>

        <div className="flex shrink-0 items-center gap-2 border-t border-stone-100 p-4">
          <button onClick={download}
            className="inline-flex flex-1 items-center justify-center gap-1.5 rounded-xl bg-green-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-green-700">
            <Download className="h-4 w-4" />{s.download}
          </button>
          <button onClick={onClose} className="rounded-xl border border-stone-200 px-4 py-2.5 text-sm font-bold text-stone-700 transition-colors hover:bg-stone-50">
            {s.close}
          </button>
        </div>
      </div>
    </div>
  );
}