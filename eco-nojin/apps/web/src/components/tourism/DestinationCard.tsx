// apps/web/src/components/tourism/DestinationCard.tsx
import { useState } from "react";
import { MapPin, Users } from "lucide-react";
import type { Destination } from "./tourismData";
import { formatRating } from "./tourismData";
import { StarBar } from "./DestinationHero";
import { tourText, localeOf, type TourismStrings, type TourLang } from "./tourismI18n";

function SmartImg({ src, alt, fallback, className }: { src: string; alt: string; fallback: string; className?: string }) {
  const [err, setErr] = useState(false);
  if (err) return <div className={className} style={{ background: fallback }} />;
  return <img src={src} alt={alt} loading="lazy" decoding="async" onError={() => setErr(true)} className={className} />;
}

interface Props {
  destination: Destination;
  selected: boolean;
  strings: TourismStrings;
  lang: TourLang;
  onSelect: (id: string) => void;
}

export function DestinationCard({ destination: d, selected, strings: s, lang, onSelect }: Props) {
  const locale = localeOf(lang);
  return (
    <button onClick={() => onSelect(d.id)} aria-pressed={selected}
      className={`flex w-full items-center gap-3 rounded-2xl border p-2.5 text-start transition-all hover:-translate-y-0.5 hover:shadow-sm ${
        selected ? "border-green-500 bg-green-50/60 ring-1 ring-green-600/20" : "border-stone-200 bg-white"
      }`}>
      <SmartImg src={d.image} alt={tourText(s, d.nameKey)} fallback={d.accent}
        className="h-14 w-14 shrink-0 rounded-xl object-cover" />
      <span className="min-w-0 flex-1">
        <span className="block truncate font-semibold text-stone-800">{tourText(s, d.nameKey)}</span>
        <span className="mt-0.5 flex items-center gap-1 text-[11px] text-stone-500"><MapPin className="h-3 w-3" />{tourText(s, d.regionKey)}</span>
        <span className="mt-1 flex items-center gap-2">
          <StarBar rating={d.rating} />
          <span className="text-[11px] font-bold tabular-nums text-amber-700">{formatRating(d.rating, locale)}</span>
        </span>
      </span>
      <span className="shrink-0 text-end">
        <span className="inline-flex items-center gap-1 text-[11px] font-bold text-stone-500"><Users className="h-3 w-3" />{d.visitors.toLocaleString(locale)}</span>
      </span>
    </button>
  );
}