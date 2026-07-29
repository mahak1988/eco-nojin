import { useEffect, useState } from "react";
import { Satellite, Loader2 } from "lucide-react";
import { LeafletPicker } from "../components/maps/LeafletPicker";

export default function SatelliteDashboardPage() {
  const [lat, setLat] = useState(32.65);
  const [lng, setLng] = useState(51.67);
  const [ndvi, setNdvi] = useState<Record<string, unknown> | null>(null);
  const [series, setSeries] = useState<Array<{ date: string; ndvi: number }>>([]);
  const [loading, setLoading] = useState(false);

  async function load(a = lat, b = lng) {
    setLoading(true);
    try {
      const [n, t] = await Promise.all([
        fetch(`/api/v1/satellite/ndvi?lat=${a}&lon=${b}`, { credentials: "include" }).then((r) => r.json()),
        fetch(`/api/v1/satellite/timeseries?lat=${a}&lon=${b}`, { credentials: "include" }).then((r) => r.json()),
      ]);
      setNdvi(n);
      setSeries(t.points || []);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-5 sm:p-8">
      <div className="flex items-center gap-3">
        <div className="grid h-11 w-11 place-items-center rounded-xl bg-indigo-50">
          <Satellite className="h-5 w-5 text-indigo-700" />
        </div>
        <div>
          <h1 className="font-display text-3xl text-stone-800">Satellite</h1>
          <p className="text-sm text-stone-500">NDVI · timeseries · provider fallback</p>
        </div>
      </div>

      <LeafletPicker
        lat={lat}
        lng={lng}
        onPick={(a, b) => {
          setLat(a);
          setLng(b);
          void load(a, b);
        }}
      />

      {loading && (
        <div className="flex justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-indigo-600" />
        </div>
      )}

      {ndvi && !loading && (
        <div className="rounded-2xl border bg-white p-5 shadow-sm">
          <p className="text-sm text-stone-500">Provider: {String(ndvi.provider)}</p>
          <p className="font-display text-4xl font-black text-indigo-800">{String(ndvi.ndvi)}</p>
          <p className="text-xs text-stone-400">NDVI @ {String(ndvi.date)}</p>
        </div>
      )}

      <div className="rounded-2xl border bg-white p-4">
        <h2 className="mb-2 font-bold">Timeseries</h2>
        <div className="flex h-32 items-end gap-0.5">
          {series.map((p) => (
            <div
              key={p.date}
              title={`${p.date}: ${p.ndvi}`}
              className="flex-1 rounded-t bg-indigo-500/80"
              style={{ height: `${Math.max(8, p.ndvi * 100)}%` }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
