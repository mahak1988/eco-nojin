// apps/web/src/components/satellite/ImageryViewport.tsx
// viewport خالص CSS/SVG (درس Vite: بدون کتابخانهٔ نقشه/chunk). layer switching + zoom واقعی.
import { useState } from "react";
import { ZoomIn, ZoomOut, Satellite, Sprout, Thermometer } from "lucide-react";
import type { Tile, Layer } from "./satelliteData";
import { SATELLITE_IMGS, viewportBg, ndviColor, thermalColor, NDVI_GRADIENT, THERMAL_GRADIENT, formatNdvi } from "./satelliteData";
import { layerText, satText, localeOf, type SatelliteStrings, type SatLang } from "./satelliteI18n";

const LAYER_ICON: Record<Layer, typeof Satellite> = { satellite: Satellite, ndvi: Sprout, thermal: Thermometer };

function SmartImg({ src, alt, fallback, className }: { src: string; alt: string; fallback: string; className?: string }) {
  const [err, setErr] = useState(false);
  if (err) return <div className={className} style={{ background: fallback }} />;
  return <img src={src} alt={alt} loading="lazy" decoding="async" onError={() => setErr(true)} className={className} />;
}

interface Props { tile: Tile; strings: SatelliteStrings; lang: SatLang; }

export function ImageryViewport({ tile, strings: s, lang }: Props) {
  const locale = localeOf(lang);
  const [layer, setLayer] = useState<Layer>("ndvi");
  const [zoom, setZoom] = useState(1);

  const bg = viewportBg(layer, tile);
  const metric = layer === "ndvi" ? `NDVI ${formatNdvi(tile.ndvi, locale)}`
    : layer === "thermal" ? `${satText(s, "surfaceTemp")} ${Math.round(20 + tile.thermal * 30)}°`
    : satText(s, "layer_satellite");
  const metricColor = layer === "ndvi" ? ndviColor(tile.ndvi) : layer === "thermal" ? thermalColor(tile.thermal) : "#e2e8f0";

  return (
    <div className="overflow-hidden rounded-2xl border border-stone-800 bg-black shadow-lg">
      {/* toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 p-3">
        <div className="flex items-center gap-2">
          <button onClick={() => setZoom((z) => Math.min(3, +(z + 0.5).toFixed(1)))} aria-label={s.zoomIn}
            className="grid h-9 w-9 place-items-center rounded-lg border border-white/20 text-white/80 transition-colors hover:bg-white/10 hover:text-white">
            <ZoomIn className="h-4 w-4" />
          </button>
          <button onClick={() => setZoom((z) => Math.max(1, +(z - 0.5).toFixed(1)))} aria-label={s.zoomOut}
            className="grid h-9 w-9 place-items-center rounded-lg border border-white/20 text-white/80 transition-colors hover:bg-white/10 hover:text-white">
            <ZoomOut className="h-4 w-4" />
          </button>
          <span className="ms-1 rounded-md bg-white/10 px-2 py-1 font-mono text-xs text-white/70">{zoom.toFixed(1)}×</span>
        </div>
        <div role="group" aria-label={s.selectTile} className="flex overflow-hidden rounded-lg border border-white/20">
          {(["satellite", "ndvi", "thermal"] as Layer[]).map((l) => {
            const Icon = LAYER_ICON[l];
            const active = layer === l;
            return (
              <button key={l} onClick={() => setLayer(l)} aria-pressed={active}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-bold transition-colors ${active ? "bg-white text-black" : "text-white/70 hover:bg-white/10 hover:text-white"}`}>
                <Icon className="h-3.5 w-3.5" />{layerText(s, l)}
              </button>
            );
          })}
        </div>
      </div>

      {/* viewport */}
      <div className="relative aspect-video overflow-hidden">
        <div className="absolute inset-0 transition-transform duration-500 ease-out" style={{ transform: `scale(${zoom})`, background: bg }}>
          {layer === "satellite" && (
            <SmartImg src={SATELLITE_IMGS[tile.imgIndex]} alt={satText(s, tile.nameKey)} fallback={bg}
              className="absolute inset-0 h-full w-full object-cover opacity-90" />
          )}
          {/* grid overlay */}
          <div className="absolute inset-0 opacity-20" style={{ backgroundImage: "linear-gradient(#fff 1px,transparent 1px),linear-gradient(90deg,#fff 1px,transparent 1px)", backgroundSize: "40px 40px" }} />
          {/* marker */}
          <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
            <span className="block h-3 w-3 rounded-full bg-white shadow-[0_0_0_4px_rgba(255,255,255,0.3)] animate-pulse" />
          </div>
        </div>

        {/* metric badge */}
        <div className="absolute start-3 top-3 inline-flex items-center gap-2 rounded-full bg-black/55 px-3 py-1.5 text-xs font-bold text-white backdrop-blur">
          <span className="h-2.5 w-2.5 rounded-full" style={{ background: metricColor }} />{metric}
        </div>
        {/* cloud badge */}
        <div className="absolute end-3 top-3 rounded-full bg-black/55 px-3 py-1.5 text-xs font-bold text-white backdrop-blur">
          ☁ {tile.cloud.toLocaleString(locale)}٪
        </div>
      </div>

      {/* legend */}
      <div className="border-t border-white/10 p-3">
        {layer === "ndvi" && <Legend gradient={NDVI_GRADIENT} label={s.ndviLegend} left={s.bare} right={s.dense} />}
        {layer === "thermal" && <Legend gradient={THERMAL_GRADIENT} label={s.thermalLegend} left={s.cold} right={s.hot} />}
        {layer === "satellite" && <p className="text-center text-xs text-white/50">{satText(s, tile.nameKey)}</p>}
      </div>
    </div>
  );
}

function Legend({ gradient, label, left, right }: { gradient: string; label: string; left: string; right: string }) {
  return (
    <div>
      <p className="mb-1.5 text-center text-[11px] font-medium text-white/60">{label}</p>
      <div className="flex items-center gap-2">
        <span className="text-[10px] font-bold text-white/60">{left}</span>
        <span className="h-2 flex-1 rounded-full" style={{ background: gradient }} />
        <span className="text-[10px] font-bold text-white/60">{right}</span>
      </div>
    </div>
  );
}