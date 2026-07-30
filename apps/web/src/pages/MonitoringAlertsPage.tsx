import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Bell, Loader2, ShieldAlert, Filter } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { tExtra } from "../components/eco/i18n_extras";

type Filter = "all" | "critical" | "warning" | "info";

function severityOf(a: Record<string, unknown>): Filter {
  const s = String(a.severity || a.level || "info").toLowerCase();
  if (s.includes("crit") || s === "high") return "critical";
  if (s.includes("warn") || s === "medium") return "warning";
  return "info";
}

const SEV_STYLE: Record<string, string> = {
  critical: "bg-rose-100 text-rose-800 ring-rose-200",
  warning: "bg-amber-100 text-amber-900 ring-amber-200",
  info: "bg-sky-100 text-sky-800 ring-sky-200",
};

export default function MonitoringAlertsPage() {
  const { lang } = useLang();
  const tx = (k: string) => tExtra(lang, k);
  const [items, setItems] = useState<Array<Record<string, unknown>>>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<Filter>("all");

  useEffect(() => {
    void fetch("/api/v1/alerts", { credentials: "include" })
      .then((r) => r.json())
      .then((j) => setItems(j.data || []))
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    if (filter === "all") return items;
    return items.filter((a) => severityOf(a) === filter);
  }, [items, filter]);

  const counts = useMemo(() => {
    const c = { all: items.length, critical: 0, warning: 0, info: 0 };
    for (const a of items) c[severityOf(a)]++;
    return c;
  }, [items]);

  const filters: Filter[] = ["all", "critical", "warning", "info"];

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-5 sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="grid h-12 w-12 place-items-center rounded-2xl bg-gradient-to-br from-amber-400 to-orange-600 text-white shadow-lg shadow-amber-500/25">
            <Bell className="h-6 w-6" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">{tx("mon_alerts_title")}</h1>
            <p className="text-sm text-stone-500">{tx("mon_alerts_sub")}</p>
          </div>
        </div>
        <Link
          to="/monitoring"
          className="rounded-xl border border-stone-200 bg-white px-3 py-2 text-sm font-bold text-cyan-800 shadow-sm"
        >
          {tx("mon_back_hub")}
        </Link>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Filter className="h-4 w-4 text-stone-400" />
        {filters.map((f) => (
          <button
            key={f}
            type="button"
            onClick={() => setFilter(f)}
            className={`rounded-full px-3 py-1.5 text-xs font-bold transition ${
              filter === f
                ? "bg-stone-800 text-white"
                : "bg-white text-stone-600 ring-1 ring-stone-200 hover:bg-stone-50"
            }`}
          >
            {tx(`mon_alerts_${f}`)} ({counts[f]})
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex justify-center py-16">
          <Loader2 className="h-8 w-8 animate-spin text-amber-600" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center gap-3 rounded-3xl border border-dashed border-stone-300 bg-white py-16 text-center">
          <ShieldAlert className="h-10 w-10 text-stone-300" />
          <p className="text-stone-500">{tx("mon_alerts_empty")}</p>
        </div>
      ) : (
        <ul className="space-y-3">
          {filtered.map((a) => {
            const sev = severityOf(a);
            return (
              <li
                key={String(a.id)}
                className="card-hover rounded-2xl border border-stone-200/80 bg-white p-4 shadow-sm"
              >
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <span className={`rounded-full px-2.5 py-0.5 text-[11px] font-bold uppercase ring-1 ${SEV_STYLE[sev]}`}>
                    {tx(`mon_alerts_${sev}`)}
                  </span>
                  {a.created_at != null && (
                    <span className="text-[11px] text-stone-400">{String(a.created_at)}</span>
                  )}
                </div>
                <p className="mt-2 text-sm leading-relaxed text-stone-800">{String(a.message)}</p>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
