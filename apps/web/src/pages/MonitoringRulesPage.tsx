import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { Settings2, Plus, Shield, Loader2 } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { tExtra } from "../components/eco/i18n_extras";

type LocalRule = {
  id: string;
  name: string;
  sensor_type: string;
  operator: string;
  threshold: string;
  severity: string;
};

const SAMPLE: LocalRule[] = [
  { id: "1", name: "Low soil moisture", sensor_type: "soil", operator: "lt", threshold: "25", severity: "warning" },
  { id: "2", name: "High temperature", sensor_type: "air_temp", operator: "gt", threshold: "38", severity: "critical" },
];

const SEV: Record<string, string> = {
  critical: "bg-rose-100 text-rose-800 ring-rose-200",
  warning: "bg-amber-100 text-amber-900 ring-amber-200",
  info: "bg-sky-100 text-sky-800 ring-sky-200",
};

export default function MonitoringRulesPage() {
  const { lang } = useLang();
  const tx = (k: string) => tExtra(lang, k);
  const [msg, setMsg] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [rules, setRules] = useState<LocalRule[]>(SAMPLE);
  const [form, setForm] = useState({
    name: "",
    sensor_type: "soil",
    operator: "lt",
    threshold: "25",
    severity: "warning",
  });

  async function submit(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setMsg(null);
    try {
      const res = await fetch("/api/v1/alert-rules", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...form, threshold: Number(form.threshold) }),
      });
      if (res.ok) {
        setMsg(tx("mon_rules_ok"));
        setRules((r) => [
          { id: String(Date.now()), ...form },
          ...r,
        ]);
        setForm((f) => ({ ...f, name: "" }));
      } else {
        setMsg(`${tx("mon_rules_err")} (${res.status})`);
        setRules((r) => [{ id: String(Date.now()), ...form }, ...r]);
      }
    } catch {
      setMsg(tx("mon_rules_err"));
      setRules((r) => [{ id: String(Date.now()), ...form }, ...r]);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-5 sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="grid h-12 w-12 place-items-center rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-700 text-white shadow-lg shadow-cyan-500/25">
            <Settings2 className="h-6 w-6" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">{tx("mon_rules_title")}</h1>
            <p className="text-sm text-stone-500">{tx("mon_rules_sub")}</p>
          </div>
        </div>
        <Link
          to="/monitoring"
          className="rounded-xl border border-stone-200 bg-white px-3 py-2 text-sm font-bold text-cyan-800 shadow-sm"
        >
          {tx("mon_back_hub")}
        </Link>
      </div>

      <form
        onSubmit={(e) => void submit(e)}
        className="grid gap-3 rounded-3xl border border-stone-200/80 bg-white p-5 shadow-sm sm:grid-cols-2"
      >
        <label className="block text-sm sm:col-span-2">
          <span className="font-medium text-stone-600">{tx("mon_rules_name")}</span>
          <input
            required
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2.5 outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/15"
          />
        </label>
        <label className="block text-sm">
          <span className="font-medium text-stone-600">{tx("mon_rules_sensor")}</span>
          <select
            value={form.sensor_type}
            onChange={(e) => setForm((f) => ({ ...f, sensor_type: e.target.value }))}
            className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2.5"
          >
            {["soil", "air_temp", "humidity", "rain"].map((o) => (
              <option key={o} value={o}>
                {o}
              </option>
            ))}
          </select>
        </label>
        <label className="block text-sm">
          <span className="font-medium text-stone-600">{tx("mon_rules_op")}</span>
          <select
            value={form.operator}
            onChange={(e) => setForm((f) => ({ ...f, operator: e.target.value }))}
            className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2.5"
          >
            <option value="lt">&lt;</option>
            <option value="gt">&gt;</option>
            <option value="eq">=</option>
          </select>
        </label>
        <label className="block text-sm">
          <span className="font-medium text-stone-600">{tx("mon_rules_threshold")}</span>
          <input
            type="number"
            value={form.threshold}
            onChange={(e) => setForm((f) => ({ ...f, threshold: e.target.value }))}
            className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2.5"
          />
        </label>
        <label className="block text-sm">
          <span className="font-medium text-stone-600">{tx("mon_rules_severity")}</span>
          <select
            value={form.severity}
            onChange={(e) => setForm((f) => ({ ...f, severity: e.target.value }))}
            className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2.5"
          >
            {["info", "warning", "critical"].map((o) => (
              <option key={o} value={o}>
                {o}
              </option>
            ))}
          </select>
        </label>
        <button
          type="submit"
          disabled={saving}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-cyan-700 py-2.5 text-sm font-bold text-white hover:bg-cyan-800 disabled:opacity-60 sm:col-span-2"
        >
          {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
          {tx("mon_rules_save")}
        </button>
        {msg && <p className="text-center text-sm font-medium text-emerald-700 sm:col-span-2">{msg}</p>}
      </form>

      <div>
        <h2 className="mb-3 flex items-center gap-2 font-display text-lg text-stone-800">
          <Shield className="h-5 w-5 text-cyan-700" />
          {tx("mon_rules_list")}
        </h2>
        {rules.length === 0 ? (
          <div className="rounded-3xl border border-dashed border-stone-300 bg-white py-12 text-center text-stone-400">
            {tx("mon_rules_empty")}
          </div>
        ) : (
          <ul className="space-y-2">
            {rules.map((r) => (
              <li
                key={r.id}
                className="card-hover flex flex-wrap items-center justify-between gap-2 rounded-2xl border border-stone-200/80 bg-white px-4 py-3 shadow-sm"
              >
                <div>
                  <p className="font-bold text-stone-800">{r.name}</p>
                  <p className="text-xs text-stone-500">
                    {r.sensor_type} {r.operator} {r.threshold}
                  </p>
                </div>
                <span className={`rounded-full px-2.5 py-0.5 text-[11px] font-bold uppercase ring-1 ${SEV[r.severity] || SEV.info}`}>
                  {r.severity}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
