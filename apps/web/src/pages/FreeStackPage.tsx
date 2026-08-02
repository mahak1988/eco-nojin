import { useEffect, useState } from "react";
import { apiFetch } from "../api/http";

export default function FreeStackPage() {
  const [health, setHealth] = useState<Record<string, unknown> | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<Record<string, unknown>>("/health")
      .then(setHealth)
      .catch((e) => setErr(e instanceof Error ? e.message : String(e)));
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="font-display text-3xl font-bold">Free stack status</h1>
      <p className="text-stone-600">Phase 6–7 · zero paid APIs required for core path.</p>
      {err && <p className="text-red-600">{err}</p>}
      {health && (
        <pre className="overflow-auto rounded-xl bg-stone-900 p-4 text-xs text-emerald-100">
          {JSON.stringify(health, null, 2)}
        </pre>
      )}
      <ul className="list-disc space-y-1 pl-6 text-stone-700">
        <li>Planetary Computer EO (free)</li>
        <li>Open-Meteo weather (free)</li>
        <li>AquaCrop conceptual / optional OSPy</li>
        <li>RothC in-repo / optional pyRothC</li>
        <li>Neon/Supabase Postgres free tier for production DB</li>
      </ul>
    </div>
  );
}
