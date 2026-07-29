import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Loader2,
  Radar,
  RotateCcw,
  Save,
  Settings2,
  XCircle,
} from "lucide-react";
import {
  getScienceMonitors,
  getScienceThresholds,
  postScienceWatch,
  putScienceThresholds,
  resetScienceThresholds,
  setScienceThresholdPreset,
} from "../../lib/apiServices";
import { MetricCard } from "./ScienceVisuals";

type Event = {
  monitor_id: string;
  title_fa: string;
  severity: string;
  value: number;
  unit: string;
  message_fa: string;
  model: string;
  thresholds?: { warning: number; critical: number; operator: string };
};

type CatItem = {
  id: string;
  title_fa: string;
  model: string;
  unit: string;
  operator: string;
  warning: number;
  critical: number;
  overridden?: boolean;
  defaults?: { warning: number; critical: number };
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
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [events, setEvents] = useState<Event[]>([]);
  const [counts, setCounts] = useState<{ ok: number; warning: number; critical: number } | null>(
    null,
  );
  const [sensors, setSensors] = useState<Record<string, number> | null>(null);
  const [showCfg, setShowCfg] = useState(false);
  const [catalog, setCatalog] = useState<CatItem[]>([]);
  const [preset, setPreset] = useState("default");
  const [presets, setPresets] = useState<Record<string, { label_fa?: string }>>({});
  const [draft, setDraft] = useState<Record<string, { warning: string; critical: string }>>({});

  const loadThresholds = useCallback(async () => {
    const [th, mon] = await Promise.all([getScienceThresholds(), getScienceMonitors()]);
    if (th.source === "api") {
      const data = th.data as {
        effective?: CatItem[];
        preset?: string;
      };
      const eff = data.effective || [];
      setCatalog(eff);
      setPreset(data.preset || "default");
      const d: Record<string, { warning: string; critical: string }> = {};
      for (const m of eff) {
        d[m.id] = { warning: String(m.warning), critical: String(m.critical) };
      }
      setDraft(d);
    }
    if (mon.source === "api") {
      const mdata = mon.data as {
        presets?: Record<string, { label_fa?: string }>;
        store?: { preset?: string };
      };
      if (mdata.presets) setPresets(mdata.presets);
      if (mdata.store?.preset) setPreset(mdata.store.preset);
    }
  }, []);

  useEffect(() => {
    void loadThresholds();
  }, [loadThresholds]);

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
      thresholds?: { preset?: string; catalog?: CatItem[] };
    };
    setEvents(data.events || []);
    setCounts(data.counts || null);
    setSensors(data.sensors || null);
    if (data.thresholds?.catalog) {
      setCatalog(data.thresholds.catalog);
      setPreset(data.thresholds.preset || "default");
    }
  }

  async function saveDraft() {
    setSaving(true);
    setErr(null);
    const overrides: Record<string, { warning: number; critical: number }> = {};
    for (const [id, v] of Object.entries(draft)) {
      const w = Number(v.warning);
      const c = Number(v.critical);
      if (Number.isFinite(w) && Number.isFinite(c)) {
        overrides[id] = { warning: w, critical: c };
      }
    }
    const res = await putScienceThresholds({ overrides, merge: true, preset });
    setSaving(false);
    if (res.source === "error") {
      setErr(res.errorMessage || "save failed");
      return;
    }
    await loadThresholds();
  }

  async function applyPreset(name: string) {
    setSaving(true);
    const res = await setScienceThresholdPreset(name);
    setSaving(false);
    if (res.source === "error") {
      setErr(res.errorMessage || "preset failed");
      return;
    }
    setPreset(name);
    await loadThresholds();
  }

  async function doReset() {
    setSaving(true);
    await resetScienceThresholds();
    setSaving(false);
    await loadThresholds();
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
          پایشگرهای مدل (آستانه پویا)
        </h2>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => setShowCfg((v) => !v)}
            className="sci-btn inline-flex items-center gap-1.5 rounded-xl border border-indigo-300 bg-white px-3 py-2 text-sm font-semibold text-indigo-800"
          >
            <Settings2 className="h-4 w-4" /> آستانه‌ها
          </button>
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
      </div>

      <p className="text-sm text-stone-600">
        آستانه‌ها قابل تنظیم‌اند (دستی یا preset اقلیمی). فایل ذخیره:{" "}
        <code className="rounded bg-stone-100 px-1 text-xs">data/monitor_thresholds.json</code>
        {" · "}
        preset فعلی: <strong>{preset}</strong>
      </p>

      {showCfg && (
        <div className="sci-panel-enter space-y-3 rounded-2xl border border-indigo-100 bg-white p-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-semibold text-stone-600">Preset اقلیمی:</span>
            {Object.keys(presets).length
              ? Object.entries(presets).map(([k, v]) => (
                  <button
                    key={k}
                    type="button"
                    onClick={() => void applyPreset(k)}
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${
                      preset === k
                        ? "bg-indigo-600 text-white"
                        : "bg-stone-100 text-stone-700 hover:bg-stone-200"
                    }`}
                  >
                    {v.label_fa || k}
                  </button>
                ))
              : ["default", "arid", "humid", "high_risk"].map((k) => (
                  <button
                    key={k}
                    type="button"
                    onClick={() => void applyPreset(k)}
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${
                      preset === k ? "bg-indigo-600 text-white" : "bg-stone-100 text-stone-700"
                    }`}
                  >
                    {k}
                  </button>
                ))}
            <button
              type="button"
              onClick={() => void doReset()}
              className="ml-auto inline-flex items-center gap-1 rounded-xl border border-stone-300 px-3 py-1.5 text-xs font-semibold"
            >
              <RotateCcw className="h-3.5 w-3.5" /> Reset
            </button>
            <button
              type="button"
              onClick={() => void saveDraft()}
              disabled={saving}
              className="inline-flex items-center gap-1 rounded-xl bg-emerald-600 px-3 py-1.5 text-xs font-bold text-white"
            >
              {saving ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Save className="h-3.5 w-3.5" />}
              ذخیره
            </button>
          </div>

          <div className="max-h-80 overflow-y-auto rounded-xl border border-stone-100">
            <table className="min-w-full text-left text-xs">
              <thead className="sticky top-0 bg-stone-100 text-stone-600">
                <tr>
                  <th className="px-2 py-2">پایشگر</th>
                  <th className="px-2 py-2">مدل</th>
                  <th className="px-2 py-2">op</th>
                  <th className="px-2 py-2">Warning</th>
                  <th className="px-2 py-2">Critical</th>
                  <th className="px-2 py-2">واحد</th>
                </tr>
              </thead>
              <tbody>
                {catalog.map((m) => (
                  <tr key={m.id} className="border-t border-stone-50 odd:bg-white even:bg-stone-50/50">
                    <td className="px-2 py-1.5 font-medium">
                      {m.title_fa}
                      {m.overridden ? (
                        <span className="ml-1 text-[10px] text-indigo-600">override</span>
                      ) : null}
                    </td>
                    <td className="px-2 py-1.5 font-mono text-stone-500">{m.model}</td>
                    <td className="px-2 py-1.5 font-mono">{m.operator}</td>
                    <td className="px-2 py-1.5">
                      <input
                        type="number"
                        step="any"
                        value={draft[m.id]?.warning ?? ""}
                        onChange={(e) =>
                          setDraft((d) => ({
                            ...d,
                            [m.id]: {
                              warning: e.target.value,
                              critical: d[m.id]?.critical ?? String(m.critical),
                            },
                          }))
                        }
                        className="w-24 rounded-lg border border-stone-200 px-2 py-1"
                      />
                    </td>
                    <td className="px-2 py-1.5">
                      <input
                        type="number"
                        step="any"
                        value={draft[m.id]?.critical ?? ""}
                        onChange={(e) =>
                          setDraft((d) => ({
                            ...d,
                            [m.id]: {
                              warning: d[m.id]?.warning ?? String(m.warning),
                              critical: e.target.value,
                            },
                          }))
                        }
                        className="w-24 rounded-lg border border-stone-200 px-2 py-1"
                      />
                    </td>
                    <td className="px-2 py-1.5 text-stone-500">{m.unit}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

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
                  {e.thresholds
                    ? ` · W=${e.thresholds.warning} C=${e.thresholds.critical}`
                    : ""}
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
