// apps/web/src/components/tourism/DestinationHero.tsx
// hero editorial تمام‌عرض (الهام awwwards) + SmartImg fallback (درس gamecoca) + StarBar.
import { useState } from "react";
import { MapPin, Users, Star, Calendar } from "lucide-react";
import type { Destination } from "./tourismData";
import { CONSERVATION_STYLE, formatRating } from "./tourismData";
import { tourText, consText, localeOf, type TourismStrings, type TourLang } from "./tourismI18n";

export function StarBar({ rating }: { rating: number }) {
  const pct = (Math.max(0, Math.min(5, rating)) / 5) * 100;
  return (
    <span className="relative inline-block align-middle" style={{ width: 80, height: 16 }}>
      <span className="absolute inset-0 flex text-stone-300">{[0, 1, 2, 3, 4].map((i) => <Star key={i} className="h-4 w-4 fill-current" />)}</span>
      <span className="absolute inset-0 flex overflow-hidden text-amber-500" style={{ width: `${pct}%` }}>{[0, 1, 2, 3, 4].map((i) => <Star key={i} className="h-4 w-4 shrink-0 fill-current" />)}</span>
    </span>
  );
}

function SmartImg({ src, alt, fallback, className }: { src: string; alt: string; fallback: string; className?: string }) {
  const [err, setErr] = useState(false);
  if (err) return <div className={className} style={{ background: fallback }} />;
  return <img src={src} alt={alt} loading="eager" decoding="async" onError={() => setErr(true)} className={className} />;
}

interface Props { destination: Destination; strings: TourismStrings; lang: TourLang; }

export function DestinationHero({ destination: d, strings: s, lang }: Props) {
  const locale = localeOf(lang);
  const cs = CONSERVATION_STYLE[d.conservation];

  return (
    <SectionReveal delay={90}>
      <article key={d.id} className="relative overflow-hidden rounded-3xl border border-stone-200/80 shadow-lg" style={{ animation: "fade-up .35s var(--ease-out)" }}>
        <div className="relative h-64 sm:h-80 lg:h-96">
          <SmartImg src={d.image} alt={tourText(s, d.nameKey)} fallback={d.accent}
            className="absolute inset-0 h-full w-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/35 to-transparent" />

          <div className="absolute inset-x-0 bottom-0 p-6 sm:p-8">
            <div className="mb-3 flex flex-wrap items-center gap-2">
              <span className={`rounded-full px-2.5 py-1 text-[11px] font-bold ring-1 ${cs.chip}`}>{consText(s, d.conservation)}</span>
              <span className="inline-flex items-center gap-1 rounded-full bg-white/15 px-2.5 py-1 text-[11px] font-bold text-white backdrop-blur">
                <MapPin className="h-3 w-3" />{tourText(s, d.regionKey)}
              </span>
            </div>
            <h2 className="font-display text-3xl text-white drop-soft sm:text-4xl">{tourText(s, d.nameKey)}</h2>
            <p className="mt-2 max-w-2xl text-sm leading-relaxed text-stone-200 sm:text-base">{tourText(s, d.descKey)}</p>

            <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-2 text-sm font-medium text-white">
              <span className="inline-flex items-center gap-1.5"><StarBar rating={d.rating} /><span className="tabular-nums">{formatRating(d.rating, locale)}</span></span>
              <span className="inline-flex items-center gap-1.5"><Users className="h-4 w-4" />{d.visitors.toLocaleString(locale)} {s.visitors}</span>
              <span className="inline-flex items-center gap-1.5"><Calendar className="h-4 w-4" />{tourText(s, d.openKey)}</span>
            </div>
          </div>
        </div>
      </article>
    </SectionReveal>
  );
}