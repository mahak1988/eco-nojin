import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Loader2, MapPin, Trash2 } from "lucide-react";
import { farmsApi, type FarmDto } from "../lib/farmsApi";

export default function FarmDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const farmId = Number(id);
  const [farm, setFarm] = useState<FarmDto | null>(null);
  const [geo, setGeo] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (!Number.isFinite(farmId)) {
      setError("Invalid farm id");
      setLoading(false);
      return;
    }
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const [f, g] = await Promise.all([farmsApi.get(farmId), farmsApi.geojson(farmId).catch(() => null)]);
        if (!cancelled) {
          setFarm(f);
          setGeo(g);
        }
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "Not found");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [farmId]);

  const onDelete = async () => {
    if (!confirm("Delete this farm?")) return;
    setDeleting(true);
    try {
      await farmsApi.remove(farmId);
      navigate("/farms", { replace: true });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Delete failed");
    } finally {
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-24">
        <Loader2 className="h-8 w-8 animate-spin text-emerald-600" />
      </div>
    );
  }

  if (error || !farm) {
    return (
      <div className="mx-auto max-w-lg p-8 text-center">
        <p className="text-rose-700">{error || "Farm not found"}</p>
        <Link to="/farms" className="mt-4 inline-block font-bold text-emerald-700">
          ← Back
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-5 sm:p-8">
      <Link to="/farms" className="inline-flex items-center gap-1 text-sm font-bold text-stone-500 hover:text-stone-800">
        <ArrowLeft className="h-4 w-4" />
        All farms
      </Link>

      <div className="overflow-hidden rounded-3xl border border-stone-200 bg-white shadow-sm">
        <div className="bg-gradient-to-br from-emerald-600 to-teal-600 px-6 py-10 text-white">
          <p className="text-sm font-bold opacity-80">Farm #{farm.id}</p>
          <h1 className="font-display text-3xl">{farm.name}</h1>
          {farm.region && (
            <p className="mt-2 inline-flex items-center gap-1 text-sm opacity-90">
              <MapPin className="h-4 w-4" />
              {farm.region}
            </p>
          )}
        </div>
        <div className="space-y-4 p-6">
          <p className="text-stone-600">{farm.description || "No description"}</p>
          <dl className="grid grid-cols-2 gap-4 text-sm sm:grid-cols-3">
            <div>
              <dt className="text-stone-400">Area</dt>
              <dd className="font-bold text-stone-800">{farm.area_ha != null ? `${farm.area_ha} ha` : "—"}</dd>
            </div>
            <div>
              <dt className="text-stone-400">Latitude</dt>
              <dd className="font-bold text-stone-800">{farm.latitude ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-stone-400">Longitude</dt>
              <dd className="font-bold text-stone-800">{farm.longitude ?? "—"}</dd>
            </div>
          </dl>
          {geo && (
            <pre className="max-h-48 overflow-auto rounded-xl bg-stone-50 p-3 text-xs text-stone-600">
              {JSON.stringify(geo, null, 2)}
            </pre>
          )}
          <button
            type="button"
            disabled={deleting}
            onClick={() => void onDelete()}
            className="inline-flex items-center gap-2 rounded-xl border border-rose-200 px-4 py-2 text-sm font-bold text-rose-700 hover:bg-rose-50 disabled:opacity-60"
          >
            {deleting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
            Delete farm
          </button>
        </div>
      </div>
    </div>
  );
}
