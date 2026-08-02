import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Satellite,
  Loader2,
  RefreshCw,
  Mountain,
  Leaf,
  CloudRain,
  AlertTriangle,
  Radio,
} from "lucide-react";
import { LeafletPicker } from "../components/maps/LeafletPicker";
import {
  fetchEoCatalog,
  fetchEoSensors,
  fetchEoSummary,
  fetchNdvi,
  fetchVci,
  type EoCatalog,
  type EoSensors,
  type EoSummary,
  type NdviPoint,
  type VciPack,
} from "../lib/eoApi";

export default function EoHubPage() {
  const [lat, setLat] = useState(32.65);
  const [lon, setLon] = useState(51.67);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [catalog, setCatalog] = useState<EoCatalog | null>(null);
  const [sensors, setSensors] = useState<EoSensors | null>(null);
  const [summary, setSummary] = useState<EoSummary | null>(null);
  const [ndvi, setNdvi] = useState<NdviPoint | null>(null);
  const [vci, setVci] = useState<VciPack | null>(null);

  const load = useCallback(
    async (a = lat, b = lon) => {
      setLoading(true);
      setError(null);
      try {
        const [c, s, sum, n, v] = await Promise.all([
          fetchEoCatalog(),
          fetchEoSensors(a, b, 60),
          fetchEoSummary(a, b),
          fetchNdvi(a, b),
          fetchVci(a, b, 60, 0),
        ]);
        setCatalog(c);
        setSensors(s);
        setSummary(sum);
        setNdvi(n);
        setVci(v);
      } catch (e) {
        setError(e instanceof Error ? e.message : "EO API error");
      } finally {
        setLoading(false);
      }
    },
    [lat, lon],
  );

  useEffect(() => {
    void load();
  }, [load]);

  const eros = summary?.erosion;
  const elev = summary?.topography?.elevation_m;

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-5 sm:p-8">
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="grid h-12 w-12 place-items-center rounded-2xl bg-gradient-to-br from-sky-500 to-indigo-700 text-white shadow-lg">
            <Satellite className="h-6 w-6" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-900">EO Hub · استک ماهواره‌ای رایگان</h1>
            <p className="text-sm text-stone-500">
              Sentinel-2 · Landsat · MODIS · DEM · RUSLE-lite · Open-Meteo — بدون API پولی
            </p>
          </div>
        </div>
        <button
          type="button"
          disabled={loading}
          onClick={() => void load()}
          className="inline-flex items-center gap-2 rounded-xl border border-stone-200 bg-white px-4 py-2 text-sm font-bold shadow-sm disabled:opacity-60"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} /> بروزرسانی
        </button>
      </header>

      <div className="flex flex-wrap gap-2 text-xs font-bold">
        <Link to="/satellite" className="rounded-full bg-indigo-50 px-3 py-1 text-indigo-800 ring-1 ring-indigo-100">Satellite dashboard</Link>
        <Link to="/pilots/ndvi" className="rounded-full bg-emerald-50 px-3 py-1 text-emerald-800 ring-1 ring-emerald-100">Pilots NDVI</Link>
        <Link to="/free-stack" className="rounded-full bg-stone-100 px-3 py-1 text-stone-700 ring-1 ring-stone-200">Free stack</Link>
        <Link to="/science" className="rounded-full bg-violet-50 px-3 py-1 text-violet-800 ring-1 ring-violet-100">Science</Link>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">{error}</div>
      )}

      <section className="overflow-hidden rounded-3xl border border-stone-200 bg-white shadow-sm">
        <LeafletPicker
          lat={lat}
          lng={lon}
          height={340}
          showSatellite
          enableGeolocate
          onPick={(a, b) => {
            setLat(a);
            setLon(b);
            void load(a, b);
          }}
        />
        <p className="border-t border-stone-100 px-4 py-2 text-xs tabular-nums text-stone-500">
          {lat.toFixed(5)}, {lon.toFixed(5)} · کلیک روی نقشه یا GPS
        </p>
      </section>

      {loading && (
        <div className="flex justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Metric icon={<Leaf className="h-5 w-5" />} label="NDVI (Sentinel-2)" value={ndvi?.mean_ndvi != null ? Number(ndvi.mean_ndvi).toFixed(3) : "—"} hint={String(ndvi?.provider ?? "")} />
        <Metric icon={<Radio className="h-5 w-5" />} label="VCI / drought" value={vci?.latest_vci?.vci != null ? String(vci.latest_vci.vci) : "—"} hint={vci?.mode ?? ""} />
        <Metric icon={<Mountain className="h-5 w-5" />} label="Elevation" value={elev != null ? `${elev} m` : "—"} hint={summary?.topography?.elevation_source ?? ""} />
        <Metric icon={<AlertTriangle className="h-5 w-5" />} label="Erosion risk" value={eros?.label ?? "—"} hint={eros?.risk_score_0_100 != null ? `score ${eros.risk_score_0_100}` : "RUSLE-lite"} />
      </div>

      <section className="rounded-3xl border border-sky-100 bg-gradient-to-br from-sky-50/80 to-white p-5 shadow-sm">
        <h2 className="mb-3 flex items-center gap-2 font-display text-lg text-stone-800">
          <CloudRain className="h-5 w-5 text-sky-600" /> سنسورهای رایگان (STAC counts)
        </h2>
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {(sensors?.sensors || []).map((s) => (
            <article key={s.collection} className="rounded-2xl border border-stone-200 bg-white p-3">
              <p className="text-xs font-bold text-stone-800">{s.collection}</p>
              <p className="text-[11px] text-stone-500">{s.family}</p>
              <p className="mt-2 font-display text-2xl font-black text-indigo-700">{s.count}</p>
              {s.error && <p className="mt-1 text-[10px] text-rose-600">{s.error}</p>}
            </article>
          ))}
          {!sensors?.sensors?.length && !loading && (
            <p className="text-sm text-stone-400">No sensor counts yet — start API on :8000</p>
          )}
        </div>
      </section>

      {catalog?.collections && (
        <section className="rounded-3xl border border-stone-200 bg-white p-5 shadow-sm">
          <h2 className="mb-3 font-display text-lg text-stone-800">کاتالوگ مجموعه داده‌ها</h2>
          <p className="mb-3 text-xs text-stone-500">{catalog.policy} · {catalog.primary_hub}</p>
          <ul className="grid gap-2 sm:grid-cols-2">
            {catalog.collections.map((c) => (
              <li key={c.id} className="rounded-xl border border-stone-100 bg-stone-50/80 px-3 py-2 text-sm">
                <span className="font-bold text-stone-800">{c.id}</span>
                <span className="mt-0.5 block text-[11px] text-stone-500">{c.family} — {c.use}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {Array.isArray(vci?.timeseries) && vci!.timeseries!.length > 0 && (
        <section className="rounded-3xl border border-stone-200 bg-white p-5 shadow-sm">
          <h2 className="mb-3 font-display text-lg text-stone-800">سری زمانی NDVI / VCI</h2>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[480px] text-left text-xs">
              <thead>
                <tr className="border-b border-stone-200 text-stone-400">
                  <th className="py-2 font-bold">Date</th>
                  <th className="py-2 font-bold">NDVI</th>
                  <th className="py-2 font-bold">VCI</th>
                  <th className="py-2 font-bold">Anomaly</th>
                  <th className="py-2 font-bold">Label</th>
                </tr>
              </thead>
              <tbody>
                {vci!.timeseries!.slice(-12).map((row, i) => (
                  <tr key={i} className="border-b border-stone-100">
                    <td className="py-1.5 tabular-nums">{String(row.date ?? "—")}</td>
                    <td className="py-1.5 tabular-nums">{row.mean_ndvi != null ? Number(row.mean_ndvi).toFixed(3) : "—"}</td>
                    <td className="py-1.5 tabular-nums">{row.vci != null ? String(row.vci) : "—"}</td>
                    <td className="py-1.5 tabular-nums">{row.anomaly != null ? Number(row.anomaly).toFixed(3) : "—"}</td>
                    <td className="py-1.5">{String(row.drought_label ?? row.signal ?? "—")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}

function Metric({
  icon,
  label,
  value,
  hint,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  hint: string;
}) {
  return (
    <div className="rounded-3xl border border-stone-200/80 bg-white p-5 shadow-sm">
      <div className="flex items-center gap-2 text-indigo-600">{icon}<span className="text-xs font-bold uppercase text-stone-400">{label}</span></div>
      <p className="mt-2 font-display text-3xl font-black text-stone-900">{value}</p>
      <p className="mt-1 truncate text-[11px] text-stone-500">{hint}</p>
    </div>
  );
}
