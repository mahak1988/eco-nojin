import { FormEvent, useState } from "react";
import { AlertTriangle, Loader2, Shield } from "lucide-react";

interface RiskItem {
  code: string;
  name: string;
  score: number;
  level: string;
  drivers: string[];
  actions: string[];
}

interface Report {
  overall_score: number;
  overall_level: string;
  items: RiskItem[];
  notes: string;
}

const levelColor: Record<string, string> = {
  low: "bg-emerald-50 text-emerald-800 border-emerald-200",
  moderate: "bg-amber-50 text-amber-900 border-amber-200",
  high: "bg-orange-50 text-orange-900 border-orange-200",
  critical: "bg-rose-50 text-rose-900 border-rose-200",
};

export default function RisksPage() {
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    soil_moisture_pct: "30",
    precip_7d_mm: "5",
    et0_7d_mm: "32",
    temp_max_c: "36",
    humidity_pct: "40",
    days_since_rain: "10",
    slope_pct: "8",
    vegetation_cover_pct: "40",
    crop_category: "cereal",
  });

  async function run(e?: FormEvent) {
    e?.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const body = {
        soil_moisture_pct: Number(form.soil_moisture_pct),
        precip_7d_mm: Number(form.precip_7d_mm),
        et0_7d_mm: Number(form.et0_7d_mm),
        temp_max_c: Number(form.temp_max_c),
        humidity_pct: Number(form.humidity_pct),
        days_since_rain: Number(form.days_since_rain),
        slope_pct: Number(form.slope_pct),
        vegetation_cover_pct: Number(form.vegetation_cover_pct),
        crop_category: form.crop_category,
      };
      const res = await fetch("/api/v1/risks/predict", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setReport(await res.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-5 sm:p-8">
      <div className="flex items-center gap-3">
        <div className="grid h-11 w-11 place-items-center rounded-xl bg-rose-50">
          <Shield className="h-5 w-5 text-rose-700" />
        </div>
        <div>
          <h1 className="font-display text-3xl text-stone-800">Agri risk prediction</h1>
          <p className="text-sm text-stone-500">Drought · flood · erosion · pest · disease · heat · frost</p>
        </div>
      </div>

      <form onSubmit={(e) => void run(e)} className="grid gap-2 rounded-2xl border bg-white p-4 sm:grid-cols-3">
        {Object.entries(form).map(([k, v]) => (
          <label key={k} className="text-xs">
            {k}
            <input
              value={v}
              onChange={(e) => setForm((f) => ({ ...f, [k]: e.target.value }))}
              className="mt-1 w-full rounded-lg border px-2 py-1.5 text-sm"
            />
          </label>
        ))}
        <button
          type="submit"
          disabled={loading}
          className="sm:col-span-3 inline-flex items-center justify-center gap-2 rounded-xl bg-rose-600 py-2.5 text-sm font-bold text-white"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <AlertTriangle className="h-4 w-4" />}
          Run prediction
        </button>
      </form>

      {error && <div className="rounded-xl bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</div>}

      {report && (
        <div className="space-y-4">
          <div className={`rounded-2xl border p-4 ${levelColor[report.overall_level] || ""}`}>
            <p className="text-xs font-bold uppercase">Overall</p>
            <p className="font-display text-3xl font-black">
              {report.overall_score} · {report.overall_level}
            </p>
            <p className="mt-1 text-xs opacity-80">{report.notes}</p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {report.items.map((it) => (
              <article key={it.code} className={`rounded-2xl border p-4 ${levelColor[it.level] || "bg-white"}`}>
                <div className="flex justify-between gap-2">
                  <h3 className="font-bold">{it.name}</h3>
                  <span className="text-sm font-black">{it.score}</span>
                </div>
                <p className="text-xs uppercase opacity-70">{it.level}</p>
                <p className="mt-2 text-xs">
                  <span className="font-bold">Drivers:</span> {it.drivers.join("; ")}
                </p>
                <ul className="mt-2 list-inside list-disc text-xs">
                  {it.actions.map((a) => (
                    <li key={a}>{a}</li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
