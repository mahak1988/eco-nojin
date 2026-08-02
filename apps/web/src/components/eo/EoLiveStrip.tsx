/** Compact live EO cards — real API only (no fake numbers). */
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Loader2, Mountain, Leaf, Thermometer, AlertTriangle } from "lucide-react";
import {
  fetchEoDem,
  fetchEoErosion,
  fetchNdvi,
  fetchVci,
  type NdviPoint,
  type EoDem,
  type EoErosion,
  type VciPack,
} from "../../lib/eoApi";

type Props = {
  lat?: number;
  lon?: number;
  compact?: boolean;
};

export function EoLiveStrip({ lat = 32.65, lon = 51.67, compact = false }: Props) {
  const [ndvi, setNdvi] = useState<NdviPoint | null>(null);
  const [vci, setVci] = useState<VciPack | null>(null);
  const [dem, setDem] = useState<EoDem | null>(null);
  const [eros, setEros] = useState<EoErosion | null>(null);
  const [loading, setLoading] = useState(true);
  const [slow, setSlow] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const slowTimer = window.setTimeout(() => {
      if (!cancelled) setSlow(true);
    }, 12_000);

    (async () => {
      setLoading(true);
      setErr(null);
      setSlow(false);
      try {
        // Fast paths first (Open-Meteo DEM) so UI is not blank while NDVI runs
        const d = await fetchEoDem(lat, lon).catch(() => null);
        if (cancelled) return;
        if (d) setDem(d);

        const [n, v, e] = await Promise.all([
          fetchNdvi(lat, lon).catch((ex) => {
            console.warn("[EoLiveStrip] NDVI", ex);
            return null;
          }),
          fetchVci(lat, lon, 60, 0).catch((ex) => {
            console.warn("[EoLiveStrip] VCI", ex);
            return null;
          }),
          fetchEoErosion(lat, lon).catch(() => null),
        ]);
        if (cancelled) return;
        if (n) setNdvi(n);
        if (v) setVci(v);
        if (e) setEros(e);
        if (!n && !v && !d && !e) {
          setErr("EO timeout — wait for Planetary or refresh");
        }
      } catch (ex) {
        if (!cancelled) setErr(ex instanceof Error ? ex.message : "EO offline");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
      window.clearTimeout(slowTimer);
    };
  }, [lat, lon]);

  if (loading && !dem && !ndvi) {
    return (
      <div className="flex flex-col gap-1 rounded-2xl border border-stone-200 bg-white px-4 py-3 text-sm text-stone-500">
        <div className="flex items-center gap-2">
          <Loader2 className="h-4 w-4 animate-spin text-indigo-600" />
          Live EO loading…
        </div>
        {slow && (
          <p className="text-[11px] text-amber-700">
            Sentinel NDVI may take 20–45s (Planetary Computer). API is still working.
          </p>
        )}
      </div>
    );
  }

  if (err && !ndvi && !dem) {
    return (
      <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
        {err} · <Link className="font-bold underline" to="/eo">EO Hub</Link>
      </div>
    );
  }

  const risk = eros?.erosion?.label ?? "—";
  const elev = dem?.elevation_m;

  return (
    <div className={`grid gap-3 ${compact ? "sm:grid-cols-2" : "sm:grid-cols-2 lg:grid-cols-4"}`}>
      <Card
        icon={<Leaf className="h-4 w-4" />}
        title="NDVI"
        value={ndvi?.mean_ndvi != null ? Number(ndvi.mean_ndvi).toFixed(3) : loading ? "…" : "—"}
        sub={String(ndvi?.provider ?? (loading ? "fetching…" : "Sentinel-2"))}
      />
      <Card
        icon={<Thermometer className="h-4 w-4" />}
        title="VCI"
        value={vci?.latest_vci?.vci != null ? String(vci.latest_vci.vci) : loading ? "…" : "—"}
        sub={vci?.mode ?? "metadata_fast"}
      />
      <Card
        icon={<Mountain className="h-4 w-4" />}
        title="Elevation"
        value={elev != null ? `${elev} m` : "—"}
        sub={dem?.elevation_source ?? "Open-Meteo"}
      />
      <Card
        icon={<AlertTriangle className="h-4 w-4" />}
        title="Erosion"
        value={risk}
        sub={eros?.erosion?.risk_score_0_100 != null ? `score ${eros.erosion.risk_score_0_100}` : "RUSLE-lite"}
      />
    </div>
  );
}

function Card({ icon, title, value, sub }: { icon: React.ReactNode; title: string; value: string; sub: string }) {
  return (
    <div className="rounded-2xl border border-stone-200/80 bg-white p-4 shadow-sm">
      <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wide text-stone-400">
        <span className="text-indigo-600">{icon}</span>
        {title}
      </div>
      <p className="mt-1 font-display text-2xl font-black text-stone-800">{value}</p>
      <p className="mt-1 truncate text-[11px] text-stone-500">{sub}</p>
    </div>
  );
}

export default EoLiveStrip;
