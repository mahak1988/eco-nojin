import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { Settings2 } from "lucide-react";

export default function MonitoringRulesPage() {
  const [msg, setMsg] = useState<string | null>(null);
  const [form, setForm] = useState({
    name: "Low soil moisture",
    sensor_type: "soil",
    operator: "lt",
    threshold: "25",
    severity: "warning",
  });

  async function submit(e: FormEvent) {
    e.preventDefault();
    const res = await fetch("/api/v1/alert-rules", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...form,
        threshold: Number(form.threshold),
      }),
    });
    setMsg(res.ok ? "Rule created" : `Error ${res.status}`);
  }

  return (
    <div className="mx-auto max-w-lg space-y-6 p-5 sm:p-8">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Settings2 className="h-5 w-5" />
          <h1 className="font-display text-2xl">Alert rules · قوانین هشدار</h1>
        </div>
        <Link to="/monitoring" className="text-sm font-bold text-cyan-700">
          ← Hub
        </Link>
      </div>
      <form onSubmit={(e) => void submit(e)} className="space-y-3 rounded-2xl border bg-white p-4">
        {Object.entries(form).map(([k, v]) => (
          <label key={k} className="block text-xs">
            {k}
            <input
              className="mt-1 w-full rounded-lg border px-2 py-1.5 text-sm"
              value={v}
              onChange={(e) => setForm((f) => ({ ...f, [k]: e.target.value }))}
            />
          </label>
        ))}
        <button type="submit" className="w-full rounded-xl bg-cyan-700 py-2.5 text-sm font-bold text-white">
          Save rule
        </button>
        {msg && <p className="text-center text-sm text-emerald-700">{msg}</p>}
      </form>
    </div>
  );
}
