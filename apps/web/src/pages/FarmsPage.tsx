import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  MapPin,
  Plus,
  Search,
  Loader2,
  AlertCircle,
  RefreshCw,
  Wheat,
  Map,
} from "lucide-react";
import { farmsApi, type FarmDto } from "../lib/farmsApi";
import { apiFetch, v1 } from "../api/http";
import { useLang, CONTENT } from "../components/eco/i18n";
import { tr, tExtra } from "../components/eco/i18n_extras";

export default function FarmsPage() {
  const { lang } = useLang();
  const c = CONTENT[lang] as unknown as Record<string, unknown>;
  const tx = (key: string) => {
    const a = tr(c, lang, key);
    return a !== key ? a : tExtra(lang, key);
  };

  const [farms, setFarms] = useState<FarmDto[]>([]);
  const [total, setTotal] = useState(0);
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      let res = await farmsApi.list(1, 50, q.trim());
      if ((res.meta?.total ?? 0) === 0) {
        try {
          await apiFetch(v1("/farms/seed-demo"), { method: "POST" });
          res = await farmsApi.list(1, 50, q.trim());
        } catch {
          /* ignore seed errors */
        }
      }
      setFarms(res.data || []);
      setTotal(res.meta?.total ?? res.data?.length ?? 0);
    } catch (e) {
      setError(e instanceof Error ? e.message : tx("state_error"));
      setFarms([]);
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q, lang]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-5 sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-emerald-50 ring-1 ring-emerald-600/15">
            <Wheat className="h-5 w-5 text-emerald-700" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">{tx("nav_farms")}</h1>
            <p className="text-sm text-stone-500">
              {total} {tx("farms_subtitle")}
            </p>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => void load()}
            className="inline-flex items-center gap-1.5 rounded-xl border border-stone-200 bg-white px-3 py-2 text-xs font-bold text-stone-600 hover:bg-stone-50"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            {tx("state_retry")}
          </button>
          <Link
            to="/farms/wizard"
            className="inline-flex items-center gap-1.5 rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm font-bold text-emerald-800 hover:bg-emerald-100"
          >
            <Map className="h-4 w-4" />
            {tx("farms_map_wizard")}
          </Link>
          <Link
            to="/farms/new"
            className="inline-flex items-center gap-1.5 rounded-xl bg-emerald-600 px-4 py-2 text-sm font-bold text-white shadow-sm hover:bg-emerald-700"
          >
            <Plus className="h-4 w-4" />
            {tx("farms_quick_add")}
          </Link>
        </div>
      </div>

      <div className="relative max-w-md">
        <Search className="pointer-events-none absolute start-3 top-1/2 h-4 w-4 -translate-y-1/2 text-stone-400" />
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder={tx("search_placeholder")}
          className="w-full rounded-xl border border-stone-200 bg-white py-2.5 ps-9 pe-3 text-sm outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
        />
      </div>

      {loading && (
        <div className="flex justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-emerald-600" />
        </div>
      )}

      {error && !loading && (
        <div className="flex flex-col items-center gap-3 rounded-2xl border border-rose-200 bg-rose-50/50 py-12 text-center">
          <AlertCircle className="h-10 w-10 text-rose-500" />
          <p className="font-medium text-rose-800">{error}</p>
          <button
            type="button"
            onClick={() => void load()}
            className="rounded-xl bg-rose-600 px-4 py-2 text-sm font-bold text-white"
          >
            {tx("state_retry")}
          </button>
        </div>
      )}

      {!loading && !error && farms.length === 0 && (
        <div className="flex flex-col items-center gap-3 rounded-2xl border border-dashed border-stone-300 bg-white py-16 text-center">
          <MapPin className="h-10 w-10 text-stone-300" />
          <p className="text-stone-500">{tx("state_empty")}</p>
          <Link
            to="/farms/wizard"
            className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-bold text-white"
          >
            {tx("farms_empty_cta")}
          </Link>
        </div>
      )}

      {!loading && farms.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {farms.map((f) => (
            <Link
              key={f.id}
              to={`/farms/${f.id}`}
              className="group rounded-2xl border border-stone-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-emerald-200 hover:shadow-md"
            >
              <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 text-xl text-white shadow-md shadow-emerald-500/20">
                🌾
              </div>
              <h3 className="font-display text-lg text-stone-800 group-hover:text-emerald-700">{f.name}</h3>
              <p className="mt-1 line-clamp-2 text-sm text-stone-500">{f.description || f.region || "—"}</p>
              <div className="mt-3 flex flex-wrap gap-2 text-[11px] font-bold text-stone-500">
                {f.area_ha != null && (
                  <span className="rounded-full bg-stone-100 px-2 py-0.5">{f.area_ha} ha</span>
                )}
                {f.region && (
                  <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-emerald-700">{f.region}</span>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
