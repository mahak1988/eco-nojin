import { useState } from "react";
import { apiFetch, v1 } from "../api/http";

export default function ScienceE2EPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<Record<string, unknown> | null>(null);

  async function run() {
    setLoading(true);
    setError(null);
    try {
      const out = await apiFetch<Record<string, unknown>>(v1("/science/e2e-mrv/isfahan-wheat"));
      setData(out);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  const kpis = (data?.kpis || {}) as Record<string, unknown>;

  return (
    <div className="space-y-6">
      <header>
        <h1 className="font-display text-3xl font-bold">Science E2E · MRV</h1>
        <p className="mt-2 text-stone-600">
          زنجیره رایگان: NDVI → AquaCrop → RothC → MRV (گندم اصفهان)
        </p>
      </header>
      <button
        type="button"
        onClick={run}
        disabled={loading}
        className="rounded-xl bg-emerald-600 px-6 py-2.5 text-sm font-bold text-white disabled:opacity-60"
      >
        {loading ? "Running…" : "Run Isfahan wheat pipeline"}
      </button>
      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-800">
          <p className="font-semibold">Request failed</p>
          <p className="text-sm">{error}</p>
          <p className="mt-2 text-xs">Ensure API is on :8000 and Vite proxy is active.</p>
        </div>
      )}
      {data && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {["mean_ndvi", "yield_t_ha", "delta_soc_t_ha", "assurance_level", "issuable"].map((k) => (
            <div key={k} className="rounded-xl border border-stone-200 bg-white p-4 shadow-sm">
              <p className="text-xs uppercase text-stone-500">{k}</p>
              <p className="mt-1 text-xl font-bold text-stone-900">{String(kpis[k] ?? "—")}</p>
            </div>
          ))}
        </div>
      )}
      {data && (
        <pre className="max-h-96 overflow-auto rounded-xl bg-stone-900 p-4 text-xs text-emerald-100">
          {JSON.stringify(data, null, 2)}
        </pre>
      )}
    </div>
  );
}
