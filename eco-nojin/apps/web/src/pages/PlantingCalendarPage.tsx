import { FormEvent, useCallback, useEffect, useState } from "react";
import { CalendarDays, Loader2, Plus, RefreshCw } from "lucide-react";

interface Plan {
  id: number;
  title: string;
  crop_name: string;
  season?: string | null;
  planned_start?: string | null;
  planned_end?: string | null;
  area_ha?: number | null;
  seed_rate_kg_ha?: number | null;
  expected_yield_t_ha?: number | null;
  irrigation_method?: string | null;
  status: string;
  notes?: string | null;
}

export default function PlantingCalendarPage() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    title: "",
    crop_name: "",
    season: "spring",
    planned_start: "",
    planned_end: "",
    area_ha: "",
    seed_rate_kg_ha: "",
    expected_yield_t_ha: "",
    irrigation_method: "drip",
    notes: "",
  });
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/v1/planting-plans?page=1&size=50", {
        credentials: "include",
        headers: { Accept: "application/json" },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const j = await res.json();
      setPlans(j.data || []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function onCreate(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const res = await fetch("/api/v1/planting-plans", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({
          title: form.title,
          crop_name: form.crop_name,
          season: form.season,
          planned_start: form.planned_start || null,
          planned_end: form.planned_end || null,
          area_ha: form.area_ha ? Number(form.area_ha) : null,
          seed_rate_kg_ha: form.seed_rate_kg_ha ? Number(form.seed_rate_kg_ha) : null,
          expected_yield_t_ha: form.expected_yield_t_ha ? Number(form.expected_yield_t_ha) : null,
          irrigation_method: form.irrigation_method,
          notes: form.notes || null,
          status: "planned",
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setShowForm(false);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-5 sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-amber-50">
            <CalendarDays className="h-5 w-5 text-amber-700" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">Planting calendar</h1>
            <p className="text-sm text-stone-500">Plans · seed rate · yield · irrigation</p>
          </div>
        </div>
        <div className="flex gap-2">
          <button type="button" onClick={() => void load()} className="rounded-xl border px-3 py-2 text-xs font-bold">
            <RefreshCw className="inline h-3.5 w-3.5" /> Refresh
          </button>
          <button
            type="button"
            onClick={() => setShowForm((v) => !v)}
            className="inline-flex items-center gap-1 rounded-xl bg-amber-600 px-3 py-2 text-sm font-bold text-white"
          >
            <Plus className="h-4 w-4" /> New plan
          </button>
        </div>
      </div>

      {error && <div className="rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</div>}

      {showForm && (
        <form onSubmit={onCreate} className="grid gap-3 rounded-2xl border bg-white p-5 shadow-sm sm:grid-cols-2">
          {(
            [
              ["title", "Plan title *", "text"],
              ["crop_name", "Crop name *", "text"],
              ["season", "Season", "text"],
              ["planned_start", "Start date", "date"],
              ["planned_end", "End date", "date"],
              ["area_ha", "Area (ha)", "number"],
              ["seed_rate_kg_ha", "Seed rate (kg/ha)", "number"],
              ["expected_yield_t_ha", "Expected yield (t/ha)", "number"],
              ["irrigation_method", "Irrigation", "text"],
            ] as const
          ).map(([key, label, type]) => (
            <label key={key} className="block text-sm">
              <span className="font-medium text-stone-600">{label}</span>
              <input
                required={key === "title" || key === "crop_name"}
                type={type}
                value={form[key]}
                onChange={(e) => setForm((f) => ({ ...f, [key]: e.target.value }))}
                className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2"
              />
            </label>
          ))}
          <label className="block text-sm sm:col-span-2">
            <span className="font-medium text-stone-600">Notes</span>
            <textarea
              value={form.notes}
              onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))}
              rows={2}
              className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2"
            />
          </label>
          <button
            type="submit"
            disabled={saving}
            className="sm:col-span-2 rounded-xl bg-amber-600 py-2.5 text-sm font-bold text-white disabled:opacity-60"
          >
            {saving ? "Saving…" : "Save plan"}
          </button>
        </form>
      )}

      {loading ? (
        <div className="flex justify-center py-16">
          <Loader2 className="h-8 w-8 animate-spin text-amber-600" />
        </div>
      ) : plans.length === 0 ? (
        <p className="py-12 text-center text-stone-500">No planting plans yet</p>
      ) : (
        <div className="space-y-3">
          {plans.map((p) => (
            <article key={p.id} className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div>
                  <h3 className="font-display text-lg text-stone-800">{p.title}</h3>
                  <p className="text-sm text-amber-800 font-bold">{p.crop_name}</p>
                </div>
                <span className="rounded-full bg-stone-100 px-2 py-0.5 text-[11px] font-bold uppercase">{p.status}</span>
              </div>
              <dl className="mt-3 grid grid-cols-2 gap-2 text-xs text-stone-600 sm:grid-cols-4">
                <div>
                  <dt className="text-stone-400">Season</dt>
                  <dd className="font-bold">{p.season || "—"}</dd>
                </div>
                <div>
                  <dt className="text-stone-400">Window</dt>
                  <dd className="font-bold">
                    {p.planned_start || "?"} → {p.planned_end || "?"}
                  </dd>
                </div>
                <div>
                  <dt className="text-stone-400">Area / seed</dt>
                  <dd className="font-bold">
                    {p.area_ha ?? "—"} ha · {p.seed_rate_kg_ha ?? "—"} kg/ha
                  </dd>
                </div>
                <div>
                  <dt className="text-stone-400">Yield / irrig.</dt>
                  <dd className="font-bold">
                    {p.expected_yield_t_ha ?? "—"} t/ha · {p.irrigation_method || "—"}
                  </dd>
                </div>
              </dl>
              {p.notes && <p className="mt-2 text-sm text-stone-500">{p.notes}</p>}
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
