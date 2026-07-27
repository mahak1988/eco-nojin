import { useState } from "react";
import { Link } from "react-router-dom";
import { GitCompare, Loader2 } from "lucide-react";

export default function SatelliteChangePage() {
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    try {
      const res = await fetch("/api/v1/satellite/change-detection", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lat: 32.65, lon: 51.67 }),
      });
      setResult(await res.json());
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-5 sm:p-8">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <GitCompare className="h-5 w-5" />
          <h1 className="font-display text-3xl">Change detection · تشخیص تغییر</h1>
        </div>
        <Link to="/satellite" className="text-sm font-bold text-indigo-700">
          ← Dashboard
        </Link>
      </div>
      <button
        type="button"
        onClick={() => void run()}
        className="rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-bold text-white"
      >
        {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Compare NDVI (90d)"}
      </button>
      {result && (
        <div className="rounded-2xl border bg-white p-5">
          <p className="font-display text-3xl font-black">Δ {String(result.delta)}</p>
          <p className="text-sm uppercase">{String(result.interpretation)}</p>
          <p className="mt-2 text-xs text-stone-500">
            {String(result.ndvi_a)} → {String(result.ndvi_b)}
          </p>
        </div>
      )}
    </div>
  );
}
