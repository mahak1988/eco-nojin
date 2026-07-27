import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Activity, Loader2, Radio } from "lucide-react";

export default function MonitoringHubPage() {
  const [overview, setOverview] = useState<Record<string, unknown> | null>(null);
  const [sensors, setSensors] = useState<Array<Record<string, unknown>>>([]);
  const [alerts, setAlerts] = useState<Array<Record<string, unknown>>>([]);

  useEffect(() => {
    void (async () => {
      await fetch("/api/v1/monitoring/seed-demo", { method: "POST", credentials: "include" });
      const [o, s, a] = await Promise.all([
        fetch("/api/v1/monitoring/overview", { credentials: "include" }).then((r) => r.json()),
        fetch("/api/v1/sensors", { credentials: "include" }).then((r) => r.json()),
        fetch("/api/v1/alerts", { credentials: "include" }).then((r) => r.json()),
      ]);
      setOverview(o);
      setSensors(s.data || []);
      setAlerts(a.data || []);
    })();
  }, []);

  if (!overview)
    return (
      <div className="flex justify-center py-24">
        <Loader2 className="h-8 w-8 animate-spin text-cyan-600" />
      </div>
    );

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-5 sm:p-8">
      <div className="flex items-center gap-3">
        <div className="grid h-11 w-11 place-items-center rounded-xl bg-cyan-50">
          <Activity className="h-5 w-5 text-cyan-700" />
        </div>
        <div>
          <h1 className="font-display text-3xl text-stone-800">Monitoring hub</h1>
          <p className="text-sm text-stone-500">Sensors · alerts · live readings</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        {[
          ["Sensors", overview.sensors_count],
          ["Open alerts", overview.open_alerts],
          ["Rules", overview.rules_count],
        ].map(([l, v]) => (
          <div key={String(l)} className="rounded-2xl border bg-white p-4">
            <p className="text-xs text-stone-400">{l}</p>
            <p className="font-display text-2xl font-black">{String(v)}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <section className="rounded-2xl border bg-white p-4">
          <h2 className="mb-3 flex items-center gap-1 font-bold">
            <Radio className="h-4 w-4" /> Sensors
          </h2>
          <ul className="space-y-2 text-sm">
            {sensors.map((s) => (
              <li key={String(s.id)} className="flex justify-between rounded-xl bg-stone-50 px-3 py-2">
                <span>{String(s.name)}</span>
                <span className="text-xs font-bold uppercase text-cyan-700">{String(s.sensor_type)}</span>
              </li>
            ))}
          </ul>
          <Link to="/monitoring/alerts" className="mt-3 inline-block text-xs font-bold text-cyan-700">
            View alerts →
          </Link>
        </section>
        <section className="rounded-2xl border bg-white p-4">
          <h2 className="mb-3 font-bold">Recent alerts</h2>
          {alerts.length === 0 ? (
            <p className="text-sm text-stone-400">No alerts</p>
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
