import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, Loader2 } from "lucide-react";

export default function CropDetailPage() {
  const { id } = useParams();
  const [crop, setCrop] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let c = false;
    (async () => {
      try {
        const res = await fetch(`/api/v1/crops/${id}`, {
          credentials: "include",
          headers: { Accept: "application/json" },
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const j = await res.json();
        if (!c) setCrop(j);
      } catch (e) {
        if (!c) setError(e instanceof Error ? e.message : "Error");
      }
    })();
    return () => {
      c = true;
    };
  }, [id]);

  if (error) {
    return (
      <div className="p-8 text-center text-rose-700">
        {error}
        <div>
          <Link to="/crops" className="font-bold text-emerald-700">
            ← Catalog
          </Link>
        </div>
      </div>
    );
  }
  if (!crop) {
    return (
      <div className="flex justify-center py-24">
        <Loader2 className="h-8 w-8 animate-spin text-lime-600" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4 p-5 sm:p-8">
      <Link to="/crops" className="inline-flex items-center gap-1 text-sm font-bold text-stone-500">
        <ArrowLeft className="h-4 w-4" />
        Catalog
      </Link>
      <div className="rounded-3xl border border-stone-200 bg-white p-6 shadow-sm">
        <h1 className="font-display text-3xl text-stone-800">{String(crop.name)}</h1>
        {crop.name_fa ? <p className="text-stone-500">{String(crop.name_fa)}</p> : null}
        <p className="mt-2 text-sm text-stone-600">{String(crop.description || crop.scientific_name || "")}</p>
        <dl className="mt-6 grid grid-cols-2 gap-4 text-sm">
          <div>
            <dt className="text-stone-400">Category</dt>
            <dd className="font-bold">{String(crop.category)}</dd>
          </div>
          <div>
            <dt className="text-stone-400">Season</dt>
            <dd className="font-bold">{String(crop.season || "—")}</dd>
          </div>
          <div>
            <dt className="text-stone-400">Water need</dt>
            <dd className="font-bold">{crop.water_need_mm != null ? `${crop.water_need_mm} mm` : "—"}</dd>
          </div>
          <div>
            <dt className="text-stone-400">Growth</dt>
            <dd className="font-bold">{crop.growth_days != null ? `${crop.growth_days} days` : "—"}</dd>
          </div>
        </dl>
      </div>
    </div>
  );
}
