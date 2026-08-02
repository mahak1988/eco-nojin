import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Activity, Loader2, Radio, AlertCircle, RefreshCw } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { tExtra } from "../components/eco/i18n_extras";
import { EoLiveStrip } from "../components/eo/EoLiveStrip";

const DEFAULT_LAT = 32.65;
const DEFAULT_LON = 51.67;

export default function MonitoringHubPage() {
  const { lang } = useLang();
  const tx = (k: string) => tExtra(lang, k);
  const [overview, setOverview] = useState<Record<string, unknown> | null>(null);
  const [sensors, setSensors] = useState<Array<Record<string, unknown>>>([]);
  const [alerts, setAlerts] = useState<Array<Record<string, unknown>>>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      try {
        await fetch("/api/v1/monitoring/seed-demo", { method: "POST", credentials: "include" });
      } catch {
        /* seed optional */
      }
      const [oRes, sRes, aRes] = await Promise.all([
        fetch("/api/v1/monitoring/overview", { credentials: "include" }),
        fetch("/api/v1/sensors", { credentials: "include" }),
        fetch("/api/v1/alerts", { credentials: "include" }),
      ]);
      if (!oRes.ok) throw new Error(`overview HTTP ${oRes.status}`);
      const o = await oRes.json();
      const s = sRes.ok ? await sRes.json() : { data: [] };
      const a = aRes.ok ? await aRes.json() : { data: [] };
      setOverview(o);
      setSensors(s.data || []);
      setAlerts(a.data || []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "load_failed");
      setOverview(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  if (loading)
    return (
      <div className="flex flex-col items-center justify-center gap-2 py-24">
        <Loader2 className="h-8 w-8 animate-spin text-cyan-600" />
        <p className="text-sm text-stone-500">{tx("mon_sub")}</p>
      </div>
    );

  if (error || !overview)
    return (
      <div className="mx-auto max-w-lg space-y-4 p-8 text-center">
        <AlertCircle className="mx-auto h-10 w-10 text-rose-500" />
        <p className="font-medium text-rose-800">{error || "No data"}</p>
        <button
          type="button"
          onClick={() => void load()}
          className="inline-flex items-center gap-2 rounded-xl bg-cyan-700 px-4 py-2 text-sm font-bold text-white"
        >
          <RefreshCw className="h-4 w-4" />
          {tx("state_retry") !== "state_retry" ? tx("state_retry") : "Retry"}
        </button>
        <div className="pt-6 text-start">
          <p className="mb-2 text-xs font-bold text-stone-500">Live EO (independent of monitoring API)</p>
          <EoLiveStrip lat={DEFAULT_LAT} lon={DEFAULT_LON} compact />
          <Link to="/eo" className="mt-2 inline-block text-xs font-bold text-indigo-700 underline">EO Hub →</Link>
        </div>
      </div>
    );

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-5 sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-cyan-50">
            <Activity className="h-5 w-5 text-cyan-700" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">{tx("mon_title")}</h1>
            <p className="text-sm text-stone-500">{tx("mon_sub")}</p>
          </div>
        </div>
        <button
          type="button"
          onClick={() => void load()}
          className="inline-flex items-center gap-1.5 rounded-xl border border-stone-200 bg-white px-3 py-2 text-xs font-bold text-stone-600 hover:bg-stone-50"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Refresh
        </button>
      </div>

      <section className="space-y-2 rounded-3xl border border-sky-100 bg-sky-50/40 p-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-sm font-bold text-stone-800">
            {lang === "fa" ? "پایش ماهواره‌ای رایگان (Sentinel / DEM / فرسایش)" : "Free satellite monitoring"}
          </h2>
          <div className="flex gap-3 text-xs font-bold">
            <Link to="/eo" className="text-indigo-700 underline">EO Hub</Link>
            <Link to="/satellite" className="text-indigo-700 underline">Satellite</Link>
          </div>
        </div>
        <EoLiveStrip lat={DEFAULT_LAT} lon={DEFAULT_LON} />
      </section>

      <div className="grid grid-cols-3 gap-3">
        {[
          [tx("mon_sensors"), overview.sensors_count],
          [tx("mon_open_alerts"), overview.open_alerts],
          [tx("mon_rules"), overview.rules_count],
        ].map(([l, v]) => (
          <div key={String(l)} className="rounded-2xl border bg-white p-4">
            <p className="text-xs text-stone-400">{l}</p>
            <p className="font-display text-2xl font-black">{String(v ?? "—")}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <section className="rounded-2xl border bg-white p-4">
          <h2 className="mb-3 flex items-center gap-1 font-bold">
            <Radio className="h-4 w-4" /> {tx("mon_sensors")}
          </h2>
          {sensors.length === 0 ? (
            <p className="text-sm text-stone-400">{tx("state_empty") !== "state_empty" ? tx("state_empty") : "Empty"}</p>
          ) : (
            <ul className="space-y-2 text-sm">
              {sensors.map((s) => (
                <li key={String(s.id)} className="flex justify-between rounded-xl bg-stone-50 px-3 py-2">
                  <span>{String(s.name)}</span>
                  <span className="text-xs font-bold uppercase text-cyan-700">{String(s.sensor_type)}</span>
                </li>
              ))}
            </ul>
          )}
          <div className="mt-3 flex flex-wrap gap-3 text-xs font-bold text-cyan-700">
            <Link to="/monitoring/alerts">{tx("mon_view_alerts")}</Link>
            <Link to="/monitoring/rules">Rules</Link>
            <Link to="/monitoring/soil">Soil</Link>
            <Link to="/monitoring/map">Map</Link>
            <Link to="/eo">EO Hub</Link>
          </div>
        </section>
        <section className="rounded-2xl border bg-white p-4">
          <h2 className="mb-3 font-bold">{tx("mon_recent_alerts")}</h2>
          {alerts.length === 0 ? (
            <p className="text-sm text-stone-400">{tx("mon_no_alerts")}</p>
          ) : (
            <ul className="space-y-2 text-sm">
              {alerts.slice(0, 8).map((a) => (
                <li key={String(a.id)} className="rounded-xl border border-amber-100 bg-amber-50 px-3 py-2">
                  {String(a.message)}
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}
