// apps/web/src/components/news/NewsCard.tsx
import { useState } from "react";
import { Calendar, Clock, Eye, ArrowLeft } from "lucide-react";
import type { NewsItem } from "./newsData";
import { CATEGORY_ACCENT, formatDate } from "./newsData";
import { newsText, catText, localeOf, type NewsStrings, type NewsLang } from "./newsI18n";

function SmartImg({ src, alt, className, fallback }: { src: string; alt: string; className?: string; fallback: string }) {
  const [err, setErr] = useState(false);
  if (err) return <div className={className} style={{ background: fallback }} />;
  return <img src={src} alt={alt} loading="lazy" decoding="async" onError={() => setErr(true)} className={className} />;
}

interface Props {
  item: NewsItem;
  strings: NewsStrings;
  lang: NewsLang;
}

export function NewsCard({ item, strings: s, lang }: Props) {
  const locale = localeOf(lang);
  const accent = CATEGORY_ACCENT[item.category];

  return (
    <article className="group flex h-full flex-col overflow-hidden rounded-2xl border border-stone-200/80 bg-white shadow-sm transition-all hover:-translate-y-1 hover:shadow-md">
      <div className="relative h-44 overflow-hidden">
        <SmartImg src={item.image} alt={newsText(s, item.titleKey)} fallback={`linear-gradient(135deg, ${accent.grad.includes("green") ? "#059669,#10b981" : accent.grad.includes("blue") ? "#2563eb,#0ea5e9" : accent.grad.includes("amber") ? "#d97706,#f59e0b" : accent.grad.includes("violet") ? "#7c3aed,#a855f7" : "#e11d48,#f43f5e"})`}
          className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110" />
        <span className={`absolute top-3 start-3 rounded-full px-2.5 py-1 text-[11px] font-bold ring-1 ${accent.chip}`}>{catText(s, item.category)}</span>
      </div>

      <div className="flex flex-1 flex-col p-5">
        <div className="mb-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-stone-500">
          <span className="inline-flex items-center gap-1"><Calendar className="h-3 w-3" />{formatDate(item.date, locale)}</span>
          <span className="inline-flex items-center gap-1"><Clock className="h-3 w-3" />{item.readMinutes.toLocaleString(locale)} {s.readTime}</span>
        </div>

        <h3 className="font-display text-lg leading-snug text-stone-800">{newsText(s, item.titleKey)}</h3>
        <p className="mt-2 flex-1 text-sm leading-relaxed text-stone-600">{newsText(s, item.excerptKey)}</p>

        <div className="mt-4 flex items-center justify-between border-t border-stone-100 pt-3">
          <span className="inline-flex items-center gap-1 text-xs text-stone-500"><Eye className="h-3.5 w-3.5" />{item.views.toLocaleString(locale)}</span>
          <button className={`inline-flex items-center gap-1 text-xs font-bold ${accent.text} transition-colors hover:opacity-80`}>
            {s.readMore}<ArrowLeft className="h-3.5 w-3.5 rtl:rotate-180" />
          </button>
        </div>
      </div>
    </article>
  );
}