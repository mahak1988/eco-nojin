import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Droplets, Loader2 } from "lucide-react";

export default function MonitoringSoilPage() {
  const [sm, setSm] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void (async () => {
      try {
        const res = await fetch("/api/v1/satellite/soil-moisture?lat=32.65&lon=51.67", {
          credentials: "include",
        });
        setSm(await res.json());
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-5 sm:p-8">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-sky-50">
            <Droplets className="h-5 w-5 text-sky-700" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">Soil moisture</h1>
            <p className="text-sm text-stone-500">رطوبت خاک — surface & root zone</p>
          </div>
        </div>
        <Link to="/monitoring" className="text-sm font-bold text-cyan-700">
          ← Hub
        </Link>
      </div>
      {loading ? (
        <Loader2 className="mx-auto h-8 w-8 animate-spin text-sky-600" />
      ) : sm ? (
        <div className="grid gap-3 sm:grid-cols-3">
          {[
            ["0–7 cm", sm.sm_pct_0_7cm ?? sm.soil_moisture_0_7cm],
            ["7–28 cm", sm.soil_moisture_7_28cm],
            ["28–100 cm", sm.soil_moisture_28_100cm],
          ].map(([l, v]) => (
            <div key={String(l)} className="rounded-2xl border bg-white p-4">
              <p className="text-xs text-stone-400">{l}</p>
              <p className="font-display text-2xl font-black text-sky-800">{String(v ?? "—")}</p>
            </div>
          ))}
          <p className="sm:col-span-3 text-xs text-stone-500">
            Source: {String(sm.source || sm.provider)} · role: soil_moisture
          </p>
        </div>
      ) : (
        <p className="text-stone-500">No data</p>
      )}
    </div>
  );
}
