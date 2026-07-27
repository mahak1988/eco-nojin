import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { Play, Loader2 } from "lucide-react";

export default function AquaCropRunPage() {
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);

  async function run(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch("/api/v1/simulations/aquacrop", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ area_ha: 2, et0_mm_day: 4, kc: 1.15, days: 30, rain_mm_total: 15 }),
      });
      setResult(await res.json());
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-xl space-y-6 p-5 sm:p-8">
      <div className="flex items-center justify-between">
        <h1 className="font-display text-3xl">AquaCrop</h1>
        <Link to="/simulators" className="text-sm font-bold text-emerald-700">
          ← Simulators
        </Link>
      </div>
      <form onSubmit={(e) => void run(e)}>
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-5 py-2.5 text-sm font-bold text-white"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
          Run simulation
        </button>
      </form>
      {result && (
        <pre className="overflow-auto rounded-2xl border bg-white p-4 text-xs">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
