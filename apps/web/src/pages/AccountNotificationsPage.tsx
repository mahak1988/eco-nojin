import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bell, Loader2, Settings2 } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { tExtra } from "../components/eco/i18n_extras";

export default function AccountNotificationsPage() {
  const { lang } = useLang();
  const tx = (k: string) => tExtra(lang, k);
  const [items, setItems] = useState<Array<Record<string, unknown>>>([]);
  const [loading, setLoading] = useState(true);
  const [prefs, setPrefs] = useState({ email: true, push: false, farm: true, sim: true });

  useEffect(() => {
    fetch("/api/v1/notifications", { credentials: "include" })
      .then((r) => r.json())
      .then((j) => setItems(j.data || []))
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  }, []);

  function toggle(key: keyof typeof prefs) {
    setPrefs((p) => ({ ...p, [key]: !p[key] }));
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6 p-5 sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="grid h-12 w-12 place-items-center rounded-2xl bg-gradient-to-br from-violet-500 to-indigo-600 text-white shadow-lg shadow-violet-500/25">
            <Bell className="h-6 w-6" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">{tx("notif_title")}</h1>
            <p className="text-sm text-stone-500">{tx("notif_sub")}</p>
          </div>
        </div>
        <Link to="/account" className="text-sm font-bold text-emerald-700">
          {tx("sec_back")}
        </Link>
      </div>

      <section className="rounded-3xl border border-stone-200/80 bg-white p-5 shadow-sm">
        <h2 className="mb-3 flex items-center gap-2 font-display text-lg">
          <Settings2 className="h-5 w-5 text-stone-500" />
          {tx("notif_prefs")}
        </h2>
        <div className="grid gap-2 sm:grid-cols-2">
          {(
            [
              ["email", "notif_email"],
              ["push", "notif_push"],
              ["farm", "notif_farm"],
              ["sim", "notif_sim"],
            ] as const
          ).map(([key, label]) => (
            <button
              key={key}
              type="button"
              onClick={() => toggle(key)}
              className={`flex items-center justify-between rounded-2xl border px-4 py-3 text-sm font-bold transition ${
                prefs[key]
                  ? "border-emerald-200 bg-emerald-50 text-emerald-900"
                  : "border-stone-200 bg-stone-50 text-stone-500"
              }`}
            >
              {tx(label)}
              <span className={`h-2.5 w-2.5 rounded-full ${prefs[key] ? "bg-emerald-500" : "bg-stone-300"}`} />
            </button>
          ))}
        </div>
      </section>

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-violet-600" />
        </div>
      ) : items.length === 0 ? (
        <div className="rounded-3xl border border-dashed border-stone-300 bg-white py-14 text-center text-stone-400">
          {tx("notif_empty")}
        </div>
      ) : (
        <ul className="space-y-3">
          {items.map((n) => (
            <li
              key={String(n.id)}
              className="card-hover rounded-2xl border border-stone-200/80 bg-white p-4 shadow-sm"
            >
              <div className="flex items-start justify-between gap-2">
                <p className="font-bold text-stone-800">{String(n.title)}</p>
                <button type="button" className="text-[11px] font-bold text-violet-700">
                  {tx("notif_mark_read")}
                </button>
              </div>
              <p className="mt-1 text-sm text-stone-500">{String(n.body)}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
