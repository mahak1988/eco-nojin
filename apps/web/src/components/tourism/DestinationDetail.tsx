// apps/web/src/components/tourism/DestinationDetail.tsx
// panel جزئیات غنی + نقشهٔ موقعیت CSS خالص (درس vite: بدون کتابخانه/chunk).
import { Compass, ShieldCheck, Footprints, CalendarDays, Map } from "lucide-react";
import type { Destination, AmenityKey } from "./tourismData";
import { CONSERVATION_STYLE } from "./tourismData";
import { tourText, consText, accessText, seasonText, amenityText, localeOf, type TourismStrings, type TourLang } from "./tourismI18n";

const AMENITY_ICON: Record<AmenityKey, typeof Compass> = {
  amenity_guide: Compass, amenity_camping: Map, amenity_trail: Footprints, amenity_photo: Compass,
  amenity_wildlife: Compass, amenity_water: Compass, amenity_shelter: Map, amenity_permit: ShieldCheck,
};

interface Props { destination: Destination; strings: TourismStrings; lang: TourLang; }

export function DestinationDetail({ destination: d, strings: s, lang }: Props) {
  const locale = localeOf(lang);
  const cs = CONSERVATION_STYLE[d.conservation];

  return (
    <div key={d.id} className="space-y-4" style={{ animation: "fade-up .3s var(--ease-out)" }}>
      {/* conservation + accessibility */}
      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-2xl border border-stone-200/80 bg-white p-4 shadow-sm">
          <div className="mb-2 flex items-center justify-between">
            <span className="inline-flex items-center gap-1.5 text-xs font-bold text-stone-600"><ShieldCheck className="h-4 w-4 text-emerald-700" />{s.conservationScore}</span>
            <span className={`rounded-full px-2 py-0.5 text-[11px] font-bold ring-1 ${cs.chip}`}>{consText(s, d.conservation)}</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-stone-100">
            <div className={`h-full rounded-full transition-[width] duration-700 ease-out ${cs.bar}`} style={{ width: `${d.conservationScore}%` }} />
          </div>
          <p className="mt-1.5 text-end text-xs font-black tabular-nums" style={{ color: cs.text.includes("green") ? "#15803d" : cs.text.includes("amber") ? "#b45309" : "#b91c1c" }}>{d.conservationScore.toLocaleString(locale)}٪</p>
        </div>
        <div className="rounded-2xl border border-stone-200/80 bg-white p-4 shadow-sm">
          <span className="mb-2 inline-flex items-center gap-1.5 text-xs font-bold text-stone-600"><Footprints className="h-4 w-4 text-blue-700" />{s.accessibility}</span>
          <p className="font-display text-lg font-black text-stone-800">{accessText(s, d.accessibility)}</p>
          <p className="mt-1 inline-flex items-center gap-1 text-xs text-stone-500"><CalendarDays className="h-3 w-3" />{tourText(s, d.openKey)}</p>
        </div>
      </div>

      {/* seasons */}
      <div className="rounded-2xl border border-stone-200/80 bg-white p-4 shadow-sm">
        <p className="mb-2 text-xs font-bold uppercase tracking-wide text-stone-400">{s.bestSeasons}</p>
        <div className="flex flex-wrap gap-2">
          {d.seasons.map((k) => (
            <span key={k} className="rounded-full bg-green-50 px-3 py-1 text-xs font-bold text-green-700 ring-1 ring-green-600/15">{seasonText(s, k)}</span>
          ))}
        </div>
      </div>

      {/* amenities */}
      <div className="rounded-2xl border border-stone-200/80 bg-white p-4 shadow-sm">
        <p className="mb-2 text-xs font-bold uppercase tracking-wide text-stone-400">{s.amenities}</p>
        <div className="grid grid-cols-2 gap-2">
          {d.amenities.map((k) => {
            const Icon = AMENITY_ICON[k];
            return (
              <span key={k} className="inline-flex items-center gap-2 rounded-xl bg-stone-50 px-3 py-2 text-xs font-bold text-stone-700">
                <Icon className="h-4 w-4 text-green-700" />{amenityText(s, k)}
              </span>
            );
          })}
        </div>
      </div>

      {/* location map (CSS خالص) */}
      <div className="rounded-2xl border border-stone-200/80 bg-white p-4 shadow-sm">
        <p className="mb-2 text-xs font-bold uppercase tracking-wide text-stone-400">{s.location}</p>
        <div className="relative aspect-[2/1] w-full overflow-hidden rounded-xl bg-gradient-to-br from-emerald-50 to-sky-50 ring-1 ring-stone-200">
          <div className="absolute inset-0 opacity-30" style={{ backgroundImage: "linear-gradient(#94a3b8 1px,transparent 1px),linear-gradient(90deg,#94a3b8 1px,transparent 1px)", backgroundSize: "24px 24px" }} />
          <span className="absolute -translate-x-1/2 -translate-y-1/2" style={{ left: `${d.pos.x}%`, top: `${d.pos.y}%` }}>
            <span className="relative grid h-5 w-5 place-items-center rounded-full bg-red-600 shadow-[0_0_0_4px_rgba(220,38,38,0.25)]">
              <span className="h-1.5 w-1.5 rounded-full bg-white" />
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-red-500 opacity-50" />
            </span>
          </span>
        </div>
      </div>
    </div>
  );
}