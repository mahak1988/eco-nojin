import { useState } from "react";
import { Activity, AlertTriangle, CheckCircle2, Loader2, Radar, XCircle } from "lucide-react";
import { postScienceWatch } from "../../lib/apiServices";
import { MetricCard } from "./ScienceVisuals";

type Event = {
  monitor_id: string;
  title_fa: string;
  severity: string;
  value: number;
  unit: string;
  message_fa: string;
  model: string;
};

export function ScienceMonitorPanel({
  lat,
  lon,
  days,
}: {
  lat: number;
  lon: number;
  days: number;
}) {
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [events, setEvents] = useState<Event[]>([]);
  const [counts, setCounts] = useState<{ ok: number; warning: number; critical: number } | null>(
    null,
  );
  const [sensors, setSensors] = useState<Record<string, number> | null>(null);

  async function runWatch() {
    setLoading(true);
    setErr(null);
    const res = await postScienceWatch({ lat, lon, days, include_sensors: true });
    setLoading(false);
    if (res.source === "error") {
      setErr(res.errorMessage || "watch failed");
      return;
    }
    const data = res.data as {
      events?: Event[];
      counts?: { ok: number; warning: number; critical: number };
      sensors?: Record<string, number>;
    };
    setEvents(data.events || []);
    setCounts(data.counts || null);
    setSensors(data.sensors || null);
  }

  const sevStyle = (s: string) =>
    s === "critical"
      ? "border-rose-300 bg-rose-50 text-rose-900"
      : s === "warning"
        ? "border-amber-300 bg-amber-50 text-amber-950"
        : "border-emerald-200 bg-emerald-50/80 text-emerald-900";

  const SevIcon = ({ s }: { s: string }) =>
    s === "critical" ? (
      <XCircle className="h-4 w-4 text-rose-600" />
    ) : s === "warning" ? (
      <AlertTriangle className="h-4 w-4 text-amber-600" />
    ) : (
      <CheckCircle2 className="h-4 w-4 text-emerald-600" />
    );

  return (
    <section className="sci-panel-enter space-y-4 rounded-3xl border border-indigo-200 bg-gradient-to-br from-indigo-50/40 to-white p-5 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="flex items-center gap-2 font-display text-xl text-stone-900">
          <Radar className="sci-icon-bob h-5 w-5 text-indigo-600" />
          پایشگرهای مدل (Monitors)
        </h2>
        <button
          type="button"
          onClick={() => void runWatch()}
          disabled={loading}
          className="sci-btn inline-flex items-center gap-1.5 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-bold text-white shadow"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Activity className="h-4 w-4" />}
          اجرای پایش یکپارچه
        </button>
      </div>
      <p className="text-sm text-stone-600">
        همه مدل‌ها (AquaCrop، SCS-CN، RothC، NDVI) به‌همراه پروکسی سنسور اجرا و با آستانه‌های هشدار/بحرانی
        مقایسه می‌شوند.
      </p>

      {err && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">{err}</div>
      )}

      {counts && (
        <div className="sci-stagger grid gap-3 sm:grid-cols-3">
          <MetricCard icon={<CheckCircle2 className="h-4 w-4" />} label="OK" value={String(counts.ok)} tone="emerald" />
          <MetricCard
            icon={<AlertTriangle className="h-4 w-4" />}
            label="Warning"
            value={String(counts.warning)}
            tone="amber"
          />
          <MetricCard
            icon={<XCircle className="h-4 w-4" />}
            label="Critical"
            value={String(counts.critical)}
            tone="rose"
          />
        </div>
      )}

      {sensors && (
        <div className="rounded-2xl border border-stone-100 bg-stone-50/60 p-3 text-xs text-stone-600">
          <span className="font-semibold">سنسورها: </span>
          {Object.entries(sensors)
            .map(([k, v]) => `${k}=${typeof v === "number" ? v.toFixed(1) : v}`)
            .join(" · ")}
        </div>
      )}

      <ul className="space-y-2">
        {events.map((e) => (
          <li
            key={e.monitor_id}
            className={`sci-card flex gap-3 rounded-2xl border p-3 text-sm ${sevStyle(e.severity)}`}
          >
            <SevIcon s={e.severity} />
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                <span className="font-semibold">{e.title_fa}</span>
                <span className="font-mono text-xs">
                  {e.value} {e.unit} · {e.model}
                </span>
              </div>
              <p className="mt-1 text-xs opacity-90">{e.message_fa}</p>
            </div>
          </li>
        ))}
      </ul>

      {!events.length && !loading && (
        <p className="text-sm text-stone-500">برای شروع «اجرای پایش یکپارچه» را بزنید.</p>
      )}
    </section>
  );
}
