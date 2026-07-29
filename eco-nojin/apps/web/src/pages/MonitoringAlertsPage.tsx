import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bell, Loader2 } from "lucide-react";

export default function MonitoringAlertsPage() {
  const [items, setItems] = useState<Array<Record<string, unknown>>>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void fetch("/api/v1/alerts", { credentials: "include" })
      .then((r) => r.json())
      .then((j) => setItems(j.data || []))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-5 sm:p-8">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Bell className="h-6 w-6 text-amber-600" />
          <h1 className="font-display text-3xl text-stone-800">Alerts · هشدارها</h1>
        </div>
        <Link to="/monitoring" className="text-sm font-bold text-cyan-700">
          ← Hub
        </Link>
      </div>
      {loading ? (
        <Loader2 className="mx-auto h-8 w-8 animate-spin" />
      ) : items.length === 0 ? (
        <p className="rounded-2xl border border-dashed p-8 text-center text-stone-400">No open alerts</p>
      ) : (
        <ul className="space-y-2">
          {items.map((a) => (
            <li key={String(a.id)} className="rounded-xl border bg-amber-50 px-4 py-3 text-sm">
              <span className="font-bold uppercase text-amber-800">{String(a.severity)}</span>
              <p>{String(a.message)}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
