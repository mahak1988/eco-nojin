import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { LineChart, Loader2 } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { tExtra } from "../components/eco/i18n_extras";

export default function SatelliteTimeseriesPage() {
  const { lang } = useLang();
  const tx = (k: string) => tExtra(lang, k);
  const [points, setPoints] = useState<Array<{ date: string; ndvi: number }>>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void fetch("/api/v1/satellite/timeseries?lat=32.65&lon=51.67", { credentials: "include" })
      .then((r) => r.json())
      .then((j) => setPoints(j.points || []))
      .catch(() => setPoints([]))
      .finally(() => setLoading(false));
  }, []);

  const avg =
    points.length > 0 ? points.reduce((s, p) => s + p.ndvi, 0) / points.length : null;

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-5 sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="grid h-12 w-12 place-items-center rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-700 text-white shadow-lg shadow-indigo-500/25">
            <LineChart className="h-6 w-6" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">{tx("sat_ts_title")}</h1>
            <p className="text-sm text-stone-500">{tx("sat_ts_sub")}</p>
          </div>
        </div>
        <Link
          to="/satellite"
          className="rounded-xl border border-stone-200 bg-white px-3 py-2 text-sm font-bold text-indigo-800 shadow-sm"
        >
          {tx("sat_back")}
        </Link>
      </div>

      {avg != null && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          <div className="rounded-2xl border bg-white p-4 shadow-sm">
            <p className="text-xs text-stone-400">{tx("sat_ndvi")}</p>
            <p className="font-display text-2xl font-black text-indigo-800">{avg.toFixed(3)}</p>
          </div>
          <div className="rounded-2xl border bg-white p-4 shadow-sm">
            <p className="text-xs text-stone-400">n</p>
            <p className="font-display text-2xl font-black text-stone-800">{points.length}</p>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex flex-col items-center gap-2 py-16">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
          <p className="text-sm text-stone-500">{tx("sat_loading")}</p>
        </div>
      ) : points.length === 0 ? (
        <div className="rounded-3xl border border-dashed border-stone-300 bg-white py-16 text-center text-stone-400">
          {tx("sat_empty_series")}
        </div>
      ) : (
        <div className="rounded-3xl border border-stone-200/80 bg-white p-5 shadow-sm">
          <div className="flex h-44 items-end gap-0.5">
            {points.map((p) => (
              <div
                key={p.date}
                title={`${p.date}: ${p.ndvi}`}
                className="flex-1 rounded-t bg-gradient-to-t from-indigo-600 to-violet-400/80"
                style={{ height: `${Math.max(6, p.ndvi * 100)}%` }}
              />
            ))}
          </div>
          <div className="mt-3 flex justify-between text-[10px] text-stone-400">
            <span>{points[0]?.date}</span>
            <span>{points[points.length - 1]?.date}</span>
          </div>
        </div>
      )}
    </div>
  );
}
