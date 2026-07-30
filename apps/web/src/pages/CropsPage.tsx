import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Leaf, Loader2, AlertCircle, RefreshCw, Sprout, Search } from "lucide-react";
import { fetchCrops, type Crop } from "../api/resources";
import { apiFetch, v1 } from "../api/http";
import { t } from "../i18n";

export default function CropsPage() {
  const [crops, setCrops] = useState<Crop[]>([]);
  const [total, setTotal] = useState(0);
  const [q, setQ] = useState("");
  const [category, setCategory] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      let res = await fetchCrops(1, 200);
      if ((res.meta?.total ?? 0) === 0 && (res.data?.length ?? 0) === 0) {
        try {
          await apiFetch(v1("/crops/seed-demo?force=true"), { method: "POST" });
          res = await fetchCrops(1, 200);
        } catch {
          /* seed may fail offline; still show empty */
        }
      }
      let list = res.data || [];
      if (q.trim()) {
        const qq = q.trim().toLowerCase();
        list = list.filter(
          (c) =>
            c.name.toLowerCase().includes(qq) ||
            (c.name_fa || "").toLowerCase().includes(qq),
        );
      }
      if (category) {
        list = list.filter((c) => c.category === category);
      }
      setCrops(list);
      setTotal(res.meta?.total ?? list.length);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("common.error"));
    } finally {
      setLoading(false);
    }
  }, [q, category]);

  useEffect(() => {
    void load();
  }, [load]);

  const categories = useMemo(() => {
    const s = new Set(crops.map((c) => c.category));
    return Array.from(s).sort();
  }, [crops]);

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-5 sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-lime-50 ring-1 ring-lime-600/15">
            <Sprout className="h-5 w-5 text-lime-700" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">{t("common.nav.crops")}</h1>
            <p className="text-sm text-stone-500">
              {total} entries · water · season · growth
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={() => void load()}
          className="inline-flex items-center gap-1.5 rounded-xl border px-3 py-2 text-xs font-bold"
        >
          <RefreshCw className="h-3.5 w-3.5" /> {t("common.retry")}
        </button>
      </div>

      <div className="flex flex-wrap gap-2">
        <div className="relative min-w-[200px] flex-1">
          <Search className="pointer-events-none absolute start-3 top-1/2 h-4 w-4 -translate-y-1/2 text-stone-400" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder={t("common.search")}
            className="w-full rounded-xl border border-stone-200 py-2.5 ps-9 pe-3 text-sm"
          />
        </div>
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="rounded-xl border border-stone-200 px-3 py-2 text-sm"
        >
          <option value="">All categories</option>
          {categories.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>

      {loading && (
        <div className="flex justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-lime-600" />
        </div>
      )}
      {error && !loading && (
        <div className="rounded-2xl border border-rose-200 bg-rose-50 p-8 text-center">
          <AlertCircle className="mx-auto h-8 w-8 text-rose-500" />
          <p className="mt-2">{error}</p>
        </div>
      )}
      {!loading && !error && crops.length === 0 && (
        <p className="py-12 text-center text-stone-500">{t("common.empty")}</p>
      )}
      {!loading && !error && crops.length > 0 && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {crops.map((c) => (
            <Link
              key={c.id}
              to={`/crops/${c.id}`}
              className="rounded-2xl border border-stone-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-lime-200 hover:shadow-md"
            >
              <div className="mb-2 flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-lime-500 to-emerald-600 text-white">
                <Leaf className="h-4 w-4" />
              </div>
              <h3 className="font-display text-base text-stone-800">
                {c.name}
                {c.name_fa ? <span className="ms-1 text-xs text-stone-400">{c.name_fa}</span> : null}
              </h3>
              <p className="mt-1 text-xs font-bold uppercase tracking-wide text-lime-700">{c.category}</p>
              <div className="mt-2 flex flex-wrap gap-1.5 text-[10px] font-bold text-stone-500">
                {c.season && <span className="rounded-full bg-stone-100 px-2 py-0.5">{c.season}</span>}
                {c.water_need_mm != null && (
                  <span className="rounded-full bg-sky-50 px-2 py-0.5 text-sky-700">{c.water_need_mm} mm</span>
                )}
                {c.growth_days != null && (
                  <span className="rounded-full bg-amber-50 px-2 py-0.5 text-amber-800">{c.growth_days}d</span>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
