import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { LineChart, Loader2 } from "lucide-react";

export default function SatelliteTimeseriesPage() {
  const [points, setPoints] = useState<Array<{ date: string; ndvi: number }>>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void fetch("/api/v1/satellite/timeseries?lat=32.65&lon=51.67", { credentials: "include" })
      .then((r) => r.json())
      .then((j) => setPoints(j.points || []))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-5 sm:p-8">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <LineChart className="h-5 w-5 text-indigo-700" />
          <h1 className="font-display text-3xl">NDVI timeseries · سری زمانی</h1>
        </div>
        <Link to="/satellite" className="text-sm font-bold text-indigo-700">
          ← Dashboard
        </Link>
      </div>
      {loading ? (
        <Loader2 className="mx-auto h-8 w-8 animate-spin" />
      ) : (
        <div className="flex h-40 items-end gap-0.5 rounded-2xl border bg-white p-4">
          {points.map((p) => (
            <div
              key={p.date}
              title={`${p.date}: ${p.ndvi}`}
              className="flex-1 rounded-t bg-indigo-500/80"
              style={{ height: `${Math.max(6, p.ndvi * 100)}%` }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
