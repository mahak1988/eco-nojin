// apps/web/src/components/satellite/TileList.tsx
import { Cloud, Sprout } from "lucide-react";
import type { Tile } from "./satelliteData";
import { ndviColor, formatNdvi, formatDate } from "./satelliteData";
import { satText, localeOf, type SatelliteStrings, type SatLang } from "./satelliteI18n";

interface Props {
  tiles: Tile[];
  selectedId: string;
  strings: SatelliteStrings;
  lang: SatLang;
  onSelect: (id: string) => void;
}

export function TileList({ tiles, selectedId, strings: s, lang, onSelect }: Props) {
  const locale = localeOf(lang);

  if (tiles.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-2 rounded-2xl border border-dashed border-stone-300 bg-white py-12 text-center">
        <Sprout className="h-8 w-8 text-stone-300" />
        <p className="text-sm text-stone-500">{s.noTiles}</p>
      </div>
    );
  }

  return (
    <div className="space-y-2.5">
      {tiles.map((t) => {
        const active = t.id === selectedId;
        return (
          <button key={t.id} onClick={() => onSelect(t.id)} aria-pressed={active}
            className={`w-full rounded-xl border p-3 text-start transition-all hover:-translate-y-0.5 hover:shadow-sm ${active ? "border-green-500 bg-green-50/60 ring-1 ring-green-600/20" : "border-stone-200 bg-stone-50/70"}`}>
            <div className="mb-1.5 flex items-center justify-between gap-2">
              <span className="truncate text-sm font-semibold text-stone-800">{satText(s, t.nameKey)}</span>
              <span className="shrink-0 text-[11px] text-stone-500">{formatDate(t.date, locale)}</span>
            </div>
            <div className="mb-2 flex items-center justify-between text-[11px] font-bold">
              <span className="inline-flex items-center gap-1 text-sky-700"><Cloud className="h-3 w-3" />{t.cloud.toLocaleString(locale)}٪</span>
              <span className="inline-flex items-center gap-1" style={{ color: ndviColor(t.ndvi) }}><Sprout className="h-3 w-3" />{formatNdvi(t.ndvi, locale)}</span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-stone-200">
              <div className="h-full rounded-full transition-[width] duration-700 ease-out" style={{ width: `${t.coverage}%`, background: ndviColor(t.ndvi) }} />
            </div>
          </button>
        );
      })}
    </div>
  );
}