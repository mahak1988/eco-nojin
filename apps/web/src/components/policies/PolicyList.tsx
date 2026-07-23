// apps/web/src/components/policies/PolicyList.tsx
import { Shield, FileText, Leaf, Database, Lock, Recycle, Globe, Eye, Download, Scale } from "lucide-react";
import type { Policy, PolicyCategory, PolicyStatus } from "./policiesData";
import { formatDate } from "./policiesData";
import { polText, statusText, catText, localeOf, type PolicyStrings, type PolLang } from "./policiesI18n";

export const CATEGORY_ICON: Record<PolicyCategory, typeof Shield> = {
  privacy: Shield, terms: FileText, environmental: Leaf, data: Database,
  security: Lock, sustainability: Recycle, compliance: Globe,
};
const CATEGORY_ACCENT: Record<PolicyCategory, string> = {
  privacy: "bg-blue-50 text-blue-700 ring-blue-600/15",
  terms: "bg-stone-100 text-stone-700 ring-stone-600/15",
  environmental: "bg-green-50 text-green-700 ring-green-600/15",
  data: "bg-violet-50 text-violet-700 ring-violet-600/15",
  security: "bg-red-50 text-red-700 ring-red-600/15",
  sustainability: "bg-emerald-50 text-emerald-700 ring-emerald-600/15",
  compliance: "bg-sky-50 text-sky-700 ring-sky-600/15",
};
const STATUS_STYLE: Record<PolicyStatus, string> = {
  active: "bg-green-50 text-green-700 ring-green-600/15",
  review: "bg-amber-50 text-amber-700 ring-amber-600/15",
  draft: "bg-blue-50 text-blue-700 ring-blue-600/15",
};

interface Props {
  policies: Policy[];
  strings: PolicyStrings;
  lang: PolLang;
  onView: (p: Policy) => void;
  onDownload: (p: Policy) => void;
}

export function PolicyList({ policies, strings: s, lang, onView, onDownload }: Props) {
  const locale = localeOf(lang);

  if (policies.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-stone-300 bg-white py-16 text-center">
        <Scale className="h-10 w-10 text-stone-300" />
        <p className="text-stone-500">{s.noPolicies}</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {policies.map((p) => {
        const Icon = CATEGORY_ICON[p.category];
        return (
          <article key={p.id}
            className="flex flex-col gap-3 rounded-2xl border border-stone-200/80 bg-white p-4 shadow-sm transition-all hover:border-green-300 hover:shadow-md sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-start gap-3">
              <span className={`grid h-10 w-10 shrink-0 place-items-center rounded-xl ring-1 ${CATEGORY_ACCENT[p.category]}`}>
                <Icon className="h-5 w-5" />
              </span>
              <div className="min-w-0">
                <h3 className="font-semibold text-stone-800">{polText(s, p.titleKey)}</h3>
                <p className="mt-0.5 text-xs text-stone-500">
                  {s.version} {p.version} · {s.updated} {formatDate(p.updated, locale)}
                </p>
                <div className="mt-1.5 flex flex-wrap items-center gap-1.5">
                  <span className={`rounded-full px-2 py-0.5 text-[11px] font-bold ring-1 ${CATEGORY_ACCENT[p.category]}`}>{catText(s, p.category)}</span>
                  <span className={`rounded-full px-2 py-0.5 text-[11px] font-bold ring-1 ${STATUS_STYLE[p.status]}`}>{statusText(s, p.status)}</span>
                </div>
              </div>
            </div>
            <div className="flex shrink-0 items-center gap-2">
              <button onClick={() => onView(p)}
                className="inline-flex items-center gap-1.5 rounded-xl bg-green-600 px-3.5 py-2 text-xs font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-green-700">
                <Eye className="h-3.5 w-3.5" />{s.view}
              </button>
              <button onClick={() => onDownload(p)} title={s.download}
                className="grid h-9 w-9 place-items-center rounded-xl border border-stone-200 text-stone-600 transition-colors hover:bg-stone-50 hover:text-green-700">
                <Download className="h-4 w-4" />
              </button>
            </div>
          </article>
        );
      })}
    </div>
  );
}