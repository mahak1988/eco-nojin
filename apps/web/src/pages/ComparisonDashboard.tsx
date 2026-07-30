/** Side-by-side simulation comparison (English UI strings for Phase 4 i18n later). */
import { useEffect, useState } from "react";
import { Scale, TrendingUp, Droplets } from "lucide-react";
import { API_BASE, API_V1 } from "../api/http";

interface Run {
  id: string;
  simulator_name: string;
  metrics: Record<string, number>;
  created_at: string;
}

function runsUrl(): string {
  const path = `${API_V1}/simulation/runs?limit=2`;
  return API_BASE ? `${API_BASE.replace(/\/$/, "")}${path}` : path;
}

export default function ComparisonDashboard() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(runsUrl(), { credentials: "include" })
      .then((r) => r.json())
      .then((d) => {
        setRuns(d.runs || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8 text-center">Loading…</div>;
  if (runs.length < 2) {
    return (
      <div className="p-8 text-center text-stone-500">
        Need at least 2 saved simulations to compare.
      </div>
    );
  }

  const [run1, run2] = runs;

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-8">
      <h1 className="text-3xl font-bold text-stone-800">Scenario comparison</h1>
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {[run1, run2].map((run, idx) => (
          <div
            key={run.id}
            className={`rounded-2xl border p-6 ${
              idx === 0 ? "border-blue-200 bg-blue-50/30" : "border-purple-200 bg-purple-50/30"
            }`}
          >
            <h2 className="mb-4 text-xl font-bold">
              {run.simulator_name}{" "}
              <span className="text-sm font-normal text-stone-500">
                ({new Date(run.created_at).toLocaleDateString()})
              </span>
            </h2>
            <div className="space-y-3">
              <div className="flex items-center gap-2 rounded-xl bg-white p-3 shadow-sm">
                <Scale className="h-5 w-5 text-blue-600" />
                <div>
                  <p className="text-xs text-stone-500">Yield (t/ha)</p>
                  <p className="text-lg font-bold">{run.metrics?.yield_t_ha ?? "N/A"}</p>
                </div>
              </div>
              <div className="flex items-center gap-2 rounded-xl bg-white p-3 shadow-sm">
                <Droplets className="h-5 w-5 text-cyan-600" />
                <div>
                  <p className="text-xs text-stone-500">Water productivity (kg/m³)</p>
                  <p className="text-lg font-bold">{run.metrics?.water_use_efficiency_kg_m3 ?? "N/A"}</p>
                </div>
              </div>
              <div className="flex items-center gap-2 rounded-xl bg-white p-3 shadow-sm">
                <TrendingUp className="h-5 w-5 text-green-600" />
                <div>
                  <p className="text-xs text-stone-500">NPV</p>
                  <p className="text-lg font-bold">{run.metrics?.npv_m_usd ?? "N/A"}</p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
