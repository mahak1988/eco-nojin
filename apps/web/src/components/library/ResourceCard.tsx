// apps/web/src/components/library/ResourceCard.tsx
import { useState } from "react";
import { FileText, Video, Headphones, File, Download, Check, ArrowDownToLine } from "lucide-react";
import type { Resource, ResourceType } from "./libraryData";
import { formatSize, formatDate } from "./libraryData";
import { libText, typeText, catText, localeOf, type LibraryStrings, type LibLang } from "./libraryI18n";

const TYPE_STYLE: Record<ResourceType, { icon: typeof FileText; chip: string; ring: string; grad: string }> = {
  pdf:   { icon: FileText,   chip: "bg-red-50 text-red-700",     ring: "ring-red-600/15",     grad: "from-red-500 to-rose-400" },
  video: { icon: Video,      chip: "bg-violet-50 text-violet-700", ring: "ring-violet-600/15", grad: "from-violet-500 to-purple-400" },
  audio: { icon: Headphones, chip: "bg-amber-50 text-amber-700", ring: "ring-amber-600/15",  grad: "from-amber-500 to-orange-400" },
  doc:   { icon: File,       chip: "bg-blue-50 text-blue-700",   ring: "ring-blue-600/15",   grad: "from-blue-500 to-sky-400" },
};

interface Props {
  resource: Resource;
  strings: LibraryStrings;
  lang: LibLang;
  onDownload: (r: Resource) => void;
}

export function ResourceCard({ resource: r, strings: s, lang, onDownload }: Props) {
  const [done, setDone] = useState(false);
  const locale = localeOf(lang);
  const st = TYPE_STYLE[r.type];
  const Icon = st.icon;

  const handleDownload = () => {
    onDownload(r);
    setDone(true);
    setTimeout(() => setDone(false), 1800);
  };

  return (
    <article className="flex flex-col rounded-2xl border border-stone-200/80 bg-white p-5 shadow-sm transition-all hover:-translate-y-1 hover:shadow-md">
      <div className="flex items-start gap-3">
        <span className={`grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-gradient-to-br ${st.grad} text-white shadow-sm`}>
          <Icon className="h-5 w-5" />
        </span>
        <div className="min-w-0 flex-1">
          <h3 className="font-display text-lg leading-snug text-stone-800">{libText(s, r.titleKey)}</h3>
          <div className="mt-1 flex flex-wrap items-center gap-2">
            <span className={`rounded-full px-2 py-0.5 text-[11px] font-bold ring-1 ${st.chip} ${st.ring}`}>{typeText(s, r.type)}</span>
            <span className="rounded-full bg-stone-100 px-2 py-0.5 text-[11px] font-bold text-stone-600">{catText(s, r.category)}</span>
          </div>
        </div>
      </div>

      <p className="mt-3 flex-1 text-sm leading-relaxed text-stone-600">{libText(s, r.summaryKey)}</p>

      <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-stone-500">
        <span className="inline-flex items-center gap-1"><ArrowDownToLine className="h-3.5 w-3.5" />{r.downloads.toLocaleString(locale)} {s.downloadsLabel}</span>
        <span>{formatSize(r.sizeKb, locale)}</span>
        <span>{formatDate(r.updated, locale)}</span>
      </div>

      <button onClick={handleDownload}
        className={`mt-4 inline-flex items-center justify-center gap-1.5 rounded-xl px-4 py-2 text-sm font-bold transition-all ${
          done ? "bg-green-50 text-green-700" : "bg-green-600 text-white shadow-sm hover:-translate-y-0.5 hover:bg-green-700"
        }`}>
        {done ? <Check className="h-4 w-4" /> : <Download className="h-4 w-4" />}
        {done ? s.downloaded : s.download}
      </button>
    </article>
  );
}