import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Satellite, Loader2, RefreshCw, LineChart, MapPinned, GitCompare, Radio } from "lucide-react";
import { LeafletPicker } from "../components/maps/LeafletPicker";
import { useLang } from "../components/eco/i18n";
import { tExtra } from "../components/eco/i18n_extras";
import { ndviHealth } from "../components/eco/i18n_phase_b5";
import { getSatelliteCatalog, type SatellitePlatform } from "../lib/apiServices";
import { apiFetch, v1 } from "../api/http";
import { EoLiveStrip } from "../components/eo/EoLiveStrip";
import { fetchEoSensors, type EoSensors } from "../lib/eoApi";

const HEALTH_STYLE = {
  good: "bg-emerald-100 text-emerald-800 ring-emerald-200",
  mid: "bg-amber-100 text-amber-900 ring-amber-200",
  poor: "bg-rose-100 text-rose-800 ring-rose-200",
} as const;

const BAR = {
  good: "from-emerald-400 to-teal-600",
  mid: "from-amber-400 to-orange-500",
  poor: "from-rose-400 to-red-600",
} as const;

function extractNdvi(row: Record<string, unknown>): number {
  const v = Number(row.mean_ndvi ?? row.ndvi ?? row.value);
  return Number.isFinite(v) ? v : NaN;
}

export default function SatelliteDashboardPage() {
  const { lang } = useLang();
  const tx = (k: string) => tExtra(lang, k);
  const [lat, setLat] = useState(32.65);
  const [lng, setLng] = useState(51.67);
  const [ndvi, setNdvi] = useState<Record<string, unknown> | null>(null);
  const [series, setSeries] = useState<Array<{ date: string; ndvi: number }>>([]);
  const [loading, setLoading] = useState(false);
  const [platforms, setPlatforms] = useState<SatellitePlatform[]>([]);
  const [recommended, setRecommended] = useState<string[]>([]);
  const [sensors, setSensors] = useState<EoSensors | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadCatalog() {
    try {
      const res = await getSatelliteCatalog();
      setPlatforms((res.data?.platforms as SatellitePlatform[]) || []);
      setRecommended((res.data?.mrv_stack_recommended as string[]) || []);
    } catch {
      setPlatforms([]);
    }
  }

  async function load(a = lat, b = lng) {
    setLoading(true);
    setError(null);
    try {
      const [n, t, s] = await Promise.all([
        apiFetch<Record<string, unknown>>(`${v1("/satellite/ndvi")}?lat=${a}&lon=${b}`),
        apiFetch<{ data?: Array<Record<string, unknown>>; points?: Array<Record<string, unknown>>; timeseries?: Array<Record<string, unknown>> }>(
          `${v1("/satellite/timeseries")}?lat=${a}&lon=${b}&days=90`,
        ),
        fetchEoSensors(a, b, 60).catch(() => null),
      ]);
      setNdvi(n);
      if (s) setSensors(s);
      const rows = (t.data || t.points || t.timeseries || []) as Array<Record<string, unknown>>;
      setSeries(
        rows
          .map((r) => ({
            date: String(r.date ?? r.acquisition_date ?? ""),
            ndvi: extractNdvi(r),
          }))
          .filter((p) => Number.isFinite(p.ndvi)),
      );
    } catch (e) {
      setNdvi(null);
      setSeries([]);
      setError(e instanceof Error ? e.message : "API error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
    void loadCatalog();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const ndviVal = ndvi != null ? extractNdvi(ndvi) : NaN;
  const health = Number.isFinite(ndviVal) ? ndviHealth(ndviVal) : "mid";

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-5 sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="grid h-12 w-12 place-items-center rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-700 text-white shadow-lg shadow-indigo-500/25">
            <Satellite className="h-6 w-6" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">{tx("sat_title")}</h1>
            <p className="text-sm text-stone-500">Live EO · Sentinel-2 + free multi-sensor stack</p>
          </div>
        </div>
        <button
          type="button"
          onClick={() => void load()}
          disabled={loading}
          className="inline-flex items-center gap-1.5 rounded-xl border border-stone-200 bg-white px-3 py-2 text-xs font-bold text-stone-600 shadow-sm hover:bg-stone-50 disabled:opacity-60"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          {tx("sat_refresh")}
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">{error}</div>
      )}

      <div className="flex flex-wrap gap-2">
        <Link to="/eo" className="inline-flex items-center gap-1 rounded-full bg-sky-50 px-3 py-1 text-xs font-bold text-sky-900 ring-1 ring-sky-100">
          EO Hub · full stack
        </Link>
        <Link to="/farms/map" className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-3 py-1 text-xs font-bold text-emerald-800 ring-1 ring-emerald-100">
          <MapPinned className="h-3.5 w-3.5" /> Register farm on map
        </Link>
        {(
          [
            ["/satellite/timeseries", "sat_link_ts", LineChart],
            ["/satellite/change", "sat_link_change", GitCompare],
            ["/satellite/fields", "sat_link_fields", MapPinned],
            ["/pilots/ndvi", "Pilots NDVI", Radio],
          ] as const
        ).map(([to, key, Icon]) => (
          <Link
            key={to}
            to={to}
            className="inline-flex items-center gap-1 rounded-full bg-indigo-50 px-3 py-1 text-xs font-bold text-indigo-800 ring-1 ring-indigo-100 hover:bg-indigo-100"
          >
            <Icon className="h-3.5 w-3.5" />
            {typeof key === "string" && key.startsWith("sat_") ? tx(key) : key}
          </Link>
        ))}
      </div>

      <EoLiveStrip lat={lat} lon={lng} />

      <section className="rounded-3xl border border-indigo-100 bg-gradient-to-br from-indigo-50/50 to-white p-5 shadow-sm">
        <div className="mb-3 flex items-center gap-2">
          <Radio className="h-4 w-4 text-indigo-600" />
          <h2 className="font-display text-lg text-stone-800">پلتفرم‌های ماهواره‌ای (رایگان)</h2>
        </div>
        <p className="mb-3 text-xs text-stone-500">
          Recommended: {recommended.length ? recommended.join(", ") : "Planetary Computer + Open-Meteo"}
        </p>
        {sensors?.sensors?.length ? (
          <div className="mb-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {sensors.sensors.map((s) => (
              <article key={s.collection} className="rounded-2xl border border-stone-200 bg-white p-3">
                <h3 className="text-sm font-bold text-stone-800">{s.collection}</h3>
                <p className="mt-1 text-[11px] text-stone-500">{s.family}</p>
                <p className="mt-2 font-display text-xl font-black text-indigo-700">{s.count} scenes</p>
              </article>
            ))}
          </div>
        ) : null}
        {platforms.length === 0 && !sensors?.sensors?.length ? (
          <p className="text-sm text-stone-400">Catalog optional — NDVI loads from /api/v1/satellite</p>
        ) : platforms.length > 0 ? (
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {platforms.map((p) => (
              <article key={p.id} className="rounded-2xl border border-stone-200 bg-white p-3">
                <h3 className="text-sm font-bold text-stone-800">{p.name}</h3>
                <p className="mt-1 text-[11px] text-stone-500">{(p.domains || []).join(" · ")}</p>
              </article>
            ))}
          </div>
        ) : null}
      </section>

      <div className="overflow-hidden rounded-3xl border border-stone-200/80 bg-white shadow-sm">
        <LeafletPicker
          lat={lat}
          lng={lng}
          height={360}
          showSatellite
          enableGeolocate
          onPick={(a, b) => {
            setLat(a);
            setLng(b);
            void load(a, b);
          }}
        />
      </div>

      {loading && (
        <div className="flex flex-col items-center gap-2 py-10">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
          <p className="text-sm text-stone-500">{tx("sat_loading")}</p>
        </div>
      )}

      {ndvi && !loading && (
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="rounded-3xl border border-stone-200/80 bg-white p-5 shadow-sm">
            <p className="text-xs font-bold uppercase text-stone-400">{tx("sat_ndvi")}</p>
            <p className="mt-1 font-display text-4xl font-black tabular-nums text-indigo-800">
              {Number.isFinite(ndviVal) ? ndviVal.toFixed(3) : "—"}
            </p>
            <div className="mt-3 h-2 overflow-hidden rounded-full bg-stone-100">
              <div
                className={`h-full rounded-full bg-gradient-to-r ${BAR[health]}`}
                style={{ width: `${Math.max(5, Math.min(100, (Number.isFinite(ndviVal) ? ndviVal : 0) * 100))}%` }}
              />
            </div>
          </div>
          <div className="rounded-3xl border border-stone-200/80 bg-white p-5 shadow-sm">
            <p className="text-xs font-bold uppercase text-stone-400">{tx("sat_health")}</p>
            <span className={`mt-2 inline-block rounded-full px-3 py-1 text-sm font-bold ring-1 ${HEALTH_STYLE[health]}`}>
              {tx(`sat_health_${health}`)}
            </span>
            <p className="mt-3 text-xs text-stone-500">
              {tx("sat_provider")}: {String(ndvi.provider ?? "—")}
            </p>
          </div>
          <div className="rounded-3xl border border-stone-200/80 bg-white p-5 shadow-sm">
            <p className="text-xs font-bold uppercase text-stone-400">{tx("sat_date")}</p>
            <p className="mt-2 font-bold text-stone-800">{String(ndvi.date ?? ndvi.acquisition_date ?? "—")}</p>
            <p className="mt-2 text-xs tabular-nums text-stone-500">
              {lat.toFixed(4)}, {lng.toFixed(4)}
            </p>
          </div>
        </div>
      )}

      <div className="rounded-3xl border border-stone-200/80 bg-white p-5 shadow-sm">
        <h2 className="mb-3 font-display text-lg text-stone-800">{tx("sat_timeseries")}</h2>
        {series.length === 0 && !loading ? (
          <div className="rounded-2xl border border-dashed border-stone-300 py-12 text-center text-sm text-stone-400">
            {tx("sat_empty_series")}
          </div>
        ) : (
          <div className="flex h-36 items-end gap-0.5">
            {series.map((p, i) => (
              <div
                key={`${p.date}-${i}`}
                title={`${p.date}: ${p.ndvi}`}
                className="flex-1 rounded-t bg-gradient-to-t from-indigo-600 to-violet-400/80 transition hover:opacity-90"
                style={{ height: `${Math.max(8, Math.min(100, p.ndvi * 100))}%` }}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
