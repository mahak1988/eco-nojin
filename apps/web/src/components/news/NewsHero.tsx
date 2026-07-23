// apps/web/src/components/news/NewsHero.tsx
// hero editorial برای خبر ویژه — تصویر تمام‌عرض + overlay + SmartImg fallback (درس gamecoca).
import { useState } from "react";
import { Calendar, Clock, Eye, ArrowLeft } from "lucide-react";
import type { NewsItem, NewsCategory } from "./newsData";
import { CATEGORY_ACCENT, formatDate } from "./newsData";
import { newsText, catText, localeOf, type NewsStrings, type NewsLang } from "./newsI18n";

function SmartImg({ src, alt, className, fallback }: { src: string; alt: string; className?: string; fallback: string }) {
  const [err, setErr] = useState(false);
  if (err) return <div className={className} style={{ background: fallback }} />;
  return <img src={src} alt={alt} loading="eager" decoding="async" onError={() => setErr(true)} className={className} />;
}

interface Props {
  item: NewsItem;
  strings: NewsStrings;
  lang: NewsLang;
}

export function NewsHero({ item, strings: s, lang }: Props) {
  const locale = localeOf(lang);
  const accent = CATEGORY_ACCENT[item.category];

  return (
    <article className="group relative overflow-hidden rounded-3xl border border-stone-200/80 shadow-md">
      <div className="relative h-72 sm:h-96 lg:h-[28rem]">
        <SmartImg src={item.image} alt={newsText(s, item.titleKey)} fallback={`linear-gradient(135deg, var(--v-ink), #1e293b)`}
          className="absolute inset-0 h-full w-full object-cover transition-transform duration-700 group-hover:scale-105" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/40 to-transparent" />

        <div className="absolute inset-x-0 bottom-0 p-6 sm:p-8 lg:p-10">
          <div className="mb-3 flex flex-wrap items-center gap-2">
            <span className={`rounded-full px-3 py-1 text-xs font-bold ring-1 ${accent.chip}`}>{catText(s, item.category)}</span>
            <span className="rounded-full bg-white/15 px-3 py-1 text-xs font-bold text-white backdrop-blur">{s.featured}</span>
          </div>
          <h2 className="font-display text-2xl leading-tight text-white drop-soft sm:text-3xl lg:text-4xl">
            {newsText(s, item.titleKey)}
          </h2>
          <p className="mt-3 max-w-2xl text-sm leading-relaxed text-stone-200 sm:text-base">{newsText(s, item.excerptKey)}</p>

          <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-2 text-xs font-medium text-stone-300">
            <span className="inline-flex items-center gap-1"><Calendar className="h-3.5 w-3.5" />{formatDate(item.date, locale)}</span>
            <span className="inline-flex items-center gap-1"><Clock className="h-3.5 w-3.5" />{item.readMinutes.toLocaleString(locale)} {s.readTime}</span>
            <span className="inline-flex items-center gap-1"><Eye className="h-3.5 w-3.5" />{item.views.toLocaleString(locale)} {s.views}</span>
            <button className="ms-auto inline-flex items-center gap-1 rounded-full bg-white px-4 py-1.5 text-xs font-bold text-stone-800 transition-all hover:-translate-y-0.5 hover:bg-stone-100">
              {s.readMore}<ArrowLeft className="h-3.5 w-3.5 rtl:rotate-180" />
            </button>
          </div>
        </div>
      </div>
    </article>
  );
}