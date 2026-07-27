import { FormEvent, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  ArrowRight,
  Check,
  Loader2,
  MapPin,
  Crosshair,
  Wheat,
} from "lucide-react";
import { farmsApi } from "../lib/farmsApi";

const STEPS = ["Basics", "Map", "Confirm"] as const;

/** Simple clickable map preview (no external map SDK). */
function ClickMap({
  lat,
  lng,
  onPick,
}: {
  lat: number | null;
  lng: number | null;
  onPick: (lat: number, lng: number) => void;
}) {
  // Rough Iran-centered bounds for demo click mapping
  const bounds = { minLat: 25, maxLat: 40, minLng: 44, maxLng: 63 };

  const marker = useMemo(() => {
    if (lat == null || lng == null) return null;
    const x = ((lng - bounds.minLng) / (bounds.maxLng - bounds.minLng)) * 100;
    const y = (1 - (lat - bounds.minLat) / (bounds.maxLat - bounds.minLat)) * 100;
    return { left: `${Math.min(98, Math.max(2, x))}%`, top: `${Math.min(98, Math.max(2, y))}%` };
  }, [lat, lng]);

  return (
    <button
      type="button"
      onClick={(e) => {
        const rect = e.currentTarget.getBoundingClientRect();
        const px = (e.clientX - rect.left) / rect.width;
        const py = (e.clientY - rect.top) / rect.height;
        const pickLng = bounds.minLng + px * (bounds.maxLng - bounds.minLng);
        const pickLat = bounds.maxLat - py * (bounds.maxLat - bounds.minLat);
        onPick(Number(pickLat.toFixed(5)), Number(pickLng.toFixed(5)));
      }}
      className="relative h-64 w-full overflow-hidden rounded-2xl border border-emerald-200 bg-gradient-to-br from-emerald-100 via-sky-50 to-amber-50 shadow-inner"
      title="Click to set location"
    >
      <div
        className="pointer-events-none absolute inset-0 opacity-30"
        style={{
          backgroundImage:
            "linear-gradient(#059669 1px, transparent 1px), linear-gradient(90deg, #059669 1px, transparent 1px)",
          backgroundSize: "32px 32px",
        }}
      />
      <span className="absolute start-3 top-3 rounded-full bg-white/90 px-2 py-1 text-[10px] font-bold text-emerald-700">
        Click map · Iran demo bounds
      </span>
      {marker && (
        <span
          className="absolute z-10 -translate-x-1/2 -translate-y-full text-2xl drop-shadow"
          style={{ left: marker.left, top: marker.top }}
        >
          📍
        </span>
      )}
    </button>
  );
}

export default function FarmWizardPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [region, setRegion] = useState("");
  const [areaHa, setAreaHa] = useState("");
  const [lat, setLat] = useState<number | null>(null);
  const [lng, setLng] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [geoLoading, setGeoLoading] = useState(false);

  const useMyLocation = () => {
    if (!navigator.geolocation) {
      setError("Geolocation not supported in this browser");
      return;
    }
    setGeoLoading(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLat(Number(pos.coords.latitude.toFixed(5)));
        setLng(Number(pos.coords.longitude.toFixed(5)));
        setGeoLoading(false);
      },
      () => {
        setError("Could not read location — allow GPS or pick on map");
        setGeoLoading(false);
      },
      { enableHighAccuracy: true, timeout: 10000 },
    );
  };

  const canNext =
    step === 0
      ? name.trim().length > 0
      : step === 1
        ? lat != null && lng != null
        : true;

  async function onSubmit(e?: FormEvent) {
    e?.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const farm = await farmsApi.create({
        name: name.trim(),
        description: description.trim() || undefined,
        region: region.trim() || undefined,
        area_ha: areaHa ? Number(areaHa) : undefined,
        latitude: lat ?? undefined,
        longitude: lng ?? undefined,
      });
      navigate(`/farms/${farm.id}`, { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create farm");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6 p-5 sm:p-8">
      <Link to="/farms" className="inline-flex items-center gap-1 text-sm font-bold text-stone-500 hover:text-stone-800">
        <ArrowLeft className="h-4 w-4" />
        Farms
      </Link>

      <div className="flex items-center gap-3">
        <div className="grid h-11 w-11 place-items-center rounded-xl bg-emerald-50">
          <Wheat className="h-5 w-5 text-emerald-700" />
        </div>
        <div>
          <h1 className="font-display text-2xl text-stone-800">Farm wizard</h1>
          <p className="text-sm text-stone-500">Name → map pin → confirm</p>
        </div>
      </div>

      <div className="flex gap-2">
        {STEPS.map((s, i) => (
          <div
            key={s}
            className={`flex flex-1 items-center justify-center gap-1 rounded-full py-2 text-xs font-bold ${
              i === step
                ? "bg-emerald-600 text-white"
                : i < step
                  ? "bg-emerald-100 text-emerald-800"
                  : "bg-stone-100 text-stone-500"
            }`}
          >
            {i < step ? <Check className="h-3.5 w-3.5" /> : null}
            {s}
          </div>
        ))}
      </div>

      {error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</div>
      )}

      {step === 0 && (
        <div className="space-y-3 rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
          <label className="block text-sm">
            <span className="font-medium text-stone-600">Farm name *</span>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2.5 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
              placeholder="North Field"
            />
          </label>
          <label className="block text-sm">
            <span className="font-medium text-stone-600">Region</span>
            <input
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2.5 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
              placeholder="Isfahan"
            />
          </label>
          <label className="block text-sm">
            <span className="font-medium text-stone-600">Area (ha)</span>
            <input
              type="number"
              min={0}
              step="0.1"
              value={areaHa}
              onChange={(e) => setAreaHa(e.target.value)}
              className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2.5 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
            />
          </label>
          <label className="block text-sm">
            <span className="font-medium text-stone-600">Description</span>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2.5 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
            />
          </label>
        </div>
      )}

      {step === 1 && (
        <div className="space-y-3 rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
          <ClickMap
            lat={lat}
            lng={lng}
            onPick={(a, b) => {
              setLat(a);
              setLng(b);
            }}
          />
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={useMyLocation}
              disabled={geoLoading}
              className="inline-flex items-center gap-1.5 rounded-xl border border-stone-200 px-3 py-2 text-xs font-bold text-stone-700 hover:bg-stone-50"
            >
              {geoLoading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Crosshair className="h-3.5 w-3.5" />}
              Use my location
            </button>
            {lat != null && lng != null && (
              <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-bold text-emerald-800">
                <MapPin className="h-3.5 w-3.5" />
                {lat}, {lng}
              </span>
            )}
          </div>
          <div className="grid grid-cols-2 gap-2">
            <label className="text-sm">
              Lat
              <input
                type="number"
                step="any"
                value={lat ?? ""}
                onChange={(e) => setLat(e.target.value ? Number(e.target.value) : null)}
                className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm"
              />
            </label>
            <label className="text-sm">
              Lng
              <input
                type="number"
                step="any"
                value={lng ?? ""}
                onChange={(e) => setLng(e.target.value ? Number(e.target.value) : null)}
                className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm"
              />
            </label>
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="space-y-2 rounded-2xl border border-stone-200 bg-white p-5 shadow-sm text-sm">
          <p>
            <span className="text-stone-400">Name</span>{" "}
            <span className="font-bold text-stone-800">{name}</span>
          </p>
          <p>
            <span className="text-stone-400">Region</span> {region || "—"}
          </p>
          <p>
            <span className="text-stone-400">Area</span> {areaHa ? `${areaHa} ha` : "—"}
          </p>
          <p>
            <span className="text-stone-400">Coordinates</span>{" "}
            {lat != null && lng != null ? `${lat}, ${lng}` : "—"}
          </p>
          <p className="text-stone-500">{description || "No description"}</p>
        </div>
      )}

      <div className="flex justify-between gap-2">
        <button
          type="button"
          disabled={step === 0}
          onClick={() => setStep((s) => Math.max(0, s - 1))}
          className="inline-flex items-center gap-1 rounded-xl border border-stone-200 px-4 py-2.5 text-sm font-bold text-stone-600 disabled:opacity-40"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </button>
        {step < 2 ? (
          <button
            type="button"
            disabled={!canNext}
            onClick={() => setStep((s) => s + 1)}
            className="inline-flex items-center gap-1 rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-bold text-white disabled:opacity-40"
          >
            Next
            <ArrowRight className="h-4 w-4" />
          </button>
        ) : (
          <button
            type="button"
            disabled={loading}
            onClick={() => void onSubmit()}
            className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-5 py-2.5 text-sm font-bold text-white disabled:opacity-60"
          >
            {loading && <Loader2 className="h-4 w-4 animate-spin" />}
            Create farm
          </button>
        )}
      </div>
    </div>
  );
}
