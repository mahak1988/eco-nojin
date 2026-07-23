// apps/web/src/pages/MySimulationsPage.tsx
// User dashboard: saved simulation runs + their recommendations & scenarios.
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bookmark, Trash2, FlaskConical, Lightbulb, GitBranch, Inbox } from "lucide-react";
import { API_BASE, API_V1 } from "../lib/simulationApi";

interface SavedRun {
  id: string; simulator_id: string; simulator_name: string;
  metrics: Record<string, number>; advisory: any;
  scenario_name?: string; note?: string; created_at?: string;
}

export default function MySimulationsPage() {
  const [runs, setRuns] = useState<SavedRun[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const r = await fetch(`${API_BASE}${API_V1}/simulation/runs?limit=100`);
      if (r.ok) {
        const d = await r.json();
        setRuns(d.runs || []);
      }
    } catch { /* offline */ }
    setLoading(false);
  };
  useEffect(() => { load(); }, []);

  const remove = async (id: string) => {
    try {
      await fetch(`${API_BASE}${API_V1}/simulation/runs/${id}`, { method: "DELETE" });
      setRuns((prev) => prev.filter((r) => r.id !== id));
    } catch { /* ignore */ }
  };

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-5 sm:p-8">
      <div className="flex items-center gap-3">
        <div className="grid h-11 w-11 place-items-center rounded-xl bg-green-50 ring-1 ring-green-600/15">
          <Bookmark className="h-5 w-5 text-green-700" />
        </div>
        <div>
          <h1 className="font-display text-3xl text-stone-800">داشبورد شبیه‌سازی‌های من</h1>
          <p className="mt-0.5 text-stone-600">تاریخچهٔ اجراها، توصیه‌ها و سناریوهای ذخیره‌شده</p>
        </div>
      </div>

      {loading ? (
        <p className="text-stone-400">در حال بارگذاری…</p>
      ) : runs.length === 0 ? (
        <div className="flex flex-col items-center gap-3 rounded-2xl border border-dashed border-stone-300 bg-white py-16 text-center">
          <Inbox className="h-10 w-10 text-stone-300" />
          <p className="text-stone-500">هنوز شبیه‌سازی ذخیره‌شده‌ای ندارید.</p>
          <Link to="/simulators" className="rounded-xl bg-green-600 px-4 py-2 text-sm font-bold text-white hover:bg-green-700">
            رفتن به شبیه‌سازها
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {runs.map((run) => (
            <div key={run.id} className="rounded-2xl border border-stone-200 bg-white p-5">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-3">
                  <span className="grid h-10 w-10 place-items-center rounded-xl bg-green-50 text-green-700 ring-1 ring-green-600/15">
                    <FlaskConical className="h-4 w-4" />
                  </span>
                  <div>
                    <Link to={`/simulators/${run.simulator_id}`} className="font-display text-lg text-stone-800 hover:text-green-700">
                      {run.simulator_name || run.simulator_id}
                    </Link>
                    <div className="mt-0.5 flex flex-wrap items-center gap-2 text-xs text-stone-500">
                      {run.scenario_name && (
                        <span className="inline-flex items-center gap-1 rounded-full bg-purple-50 px-2 py-0.5 font-bold text-purple-700">
                          <GitBranch className="h-3 w-3" /> {run.scenario_name}
                        </span>
                      )}
                      {run.created_at && <span>{new Date(run.created_at).toLocaleString("fa-IR")}</span>}
                    </div>
                  </div>
                </div>
                <button onClick={() => remove(run.id)} className="grid h-9 w-9 place-items-center rounded-xl border border-stone-200 text-stone-500 hover:bg-red-50 hover:text-red-600">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>

              {/* metrics */}
              {run.metrics && Object.keys(run.metrics).length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {Object.entries(run.metrics).slice(0, 6).map(([k, v]) => (
                    <span key={k} className="rounded-lg bg-stone-100 px-2.5 py-1 text-xs font-bold text-stone-700">
                      {k}: <span className="tabular-nums text-green-700">{typeof v === "number" ? v.toLocaleString("fa-IR", { maximumFractionDigits: 2 }) : v}</span>
                    </span>
                  ))}
                </div>
              )}

              {/* recommendations */}
              {run.advisory?.recommendations?.length > 0 && (
                <div className="mt-3 space-y-1.5">
                  <p className="flex items-center gap-1.5 text-xs font-bold text-stone-500"><Lightbulb className="h-3.5 w-3.5 text-amber-500" /> توصیه‌ها</p>
                  {run.advisory.recommendations.slice(0, 3).map((rec: any, i: number) => (
                    <p key={i} className="rounded-lg bg-amber-50 px-3 py-2 text-xs leading-relaxed text-amber-800">{rec.text}</p>
                  ))}
                </div>
              )}

              {run.note && <p className="mt-3 rounded-lg bg-stone-50 px-3 py-2 text-sm text-stone-600">📝 {run.note}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
