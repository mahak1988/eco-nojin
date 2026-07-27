import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Leaf, Loader2, AlertCircle, RefreshCw, Sprout } from "lucide-react";

interface Crop {
  id: number;
  name: string;
  name_fa?: string | null;
  category: string;
  season?: string | null;
  water_need_mm?: number | null;
  growth_days?: number | null;
  description?: string | null;
}

async function fetchCrops(): Promise<{ data: Crop[]; total: number }> {
  const res = await fetch("/api/v1/crops?page=1&size=50", {
    credentials: "include",
    headers: { Accept: "application/json" },
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const j = await res.json();
  return { data: j.data || [], total: j.meta?.total ?? 0 };
}

async function seedCrops() {
  await fetch("/api/v1/crops/seed-demo", {
    method: "POST",
    credentials: "include",
    headers: { Accept: "application/json" },
  });
}

export default function CropsPage() {
  const [crops, setCrops] = useState<Crop[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      let { data } = await fetchCrops();
      if (data.length === 0) {
        await seedCrops();
        ({ data } = await fetchCrops());
      }
      setCrops(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-5 sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-lime-50 ring-1 ring-lime-600/15">
            <Sprout className="h-5 w-5 text-lime-700" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">Crops</h1>
            <p className="text-sm text-stone-500">Catalog · water need · growth cycle</p>
          </div>
        </div>
        <button
          type="button"
          onClick={() => void load()}
          className="inline-flex items-center gap-1.5 rounded-xl border border-stone-200 px-3 py-2 text-xs font-bold"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Refresh
        </button>
      </div>

      {loading && (
        <div className="flex justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-lime-600" />
        </div>
      )}
      {error && !loading && (
        <div className="rounded-2xl border border-rose-200 bg-rose-50 p-8 text-center">
          <AlertCircle className="mx-auto h-8 w-8 text-rose-500" />
          <p className="mt-2 text-rose-800">{error}</p>
        </div>
      )}
      {!loading && !error && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {crops.map((c) => (
            <Link
              key={c.id}
              to={`/crops/${c.id}`}
              className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-lime-200 hover:shadow-md"
            >
              <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-lime-500 to-emerald-600 text-white">
                <Leaf className="h-5 w-5" />
              </div>
              <h3 className="font-display text-lg text-stone-800">
                {c.name}
                {c.name_fa ? <span className="ms-2 text-sm text-stone-400">{c.name_fa}</span> : null}
              </h3>
              <p className="mt-1 text-xs font-bold uppercase tracking-wide text-lime-700">{c.category}</p>
              <div className="mt-3 flex flex-wrap gap-2 text-[11px] font-bold text-stone-500">
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
