/** Full-screen farm map: geolocation, satellite basemap, register farm at pin. */
import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Loader2, MapPin, Satellite } from "lucide-react";
import { LeafletPicker, type MapMarker } from "../components/maps/LeafletPicker";
import { farmsApi, type FarmDto } from "../lib/farmsApi";
import { apiFetch, v1 } from "../api/http";

export default function FarmMapPage() {
  const navigate = useNavigate();
  const [lat, setLat] = useState<number | null>(32.65);
  const [lng, setLng] = useState<number | null>(51.67);
  const [name, setName] = useState("");
  const [areaHa, setAreaHa] = useState("");
  const [farms, setFarms] = useState<FarmDto[]>([]);
  const [ndvi, setNdvi] = useState<number | null>(null);
  const [provider, setProvider] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);

  const markers: MapMarker[] = farms
    .filter((f) => f.latitude != null && f.longitude != null)
    .map((f) => ({
      lat: Number(f.latitude),
      lng: Number(f.longitude),
      label: f.name,
    }));

  async function refreshFarms() {
    try {
      const res = await farmsApi.list(1, 100);
      setFarms(res.data || []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Cannot load farms");
    }
  }

  async function loadNdvi(a: number, b: number) {
    try {
      const j = await apiFetch<Record<string, unknown>>(`${v1("/satellite/ndvi")}?lat=${a}&lon=${b}`);
      const v = Number(j.mean_ndvi ?? j.ndvi);
      setNdvi(Number.isFinite(v) ? v : null);
      setProvider(String(j.provider ?? ""));
    } catch {
      setNdvi(null);
      setProvider("");
    }
  }

  useEffect(() => {
    void refreshFarms();
  }, []);

  useEffect(() => {
    if (lat != null && lng != null) void loadNdvi(lat, lng);
  }, [lat, lng]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (lat == null || lng == null || !name.trim()) {
      setError("Name and map location required");
      return;
    }
    setLoading(true);
    setError(null);
    setMsg(null);
    try {
      const farm = await farmsApi.create({
        name: name.trim(),
        area_ha: areaHa ? Number(areaHa) : undefined,
        latitude: lat,
        longitude: lng,
      });
      setMsg(`Farm #${farm.id} saved`);
      setName("");
      await refreshFarms();
      navigate(`/farms/${farm.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-4 sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="font-display text-3xl font-bold text-stone-900">نقشه مزارع · Farm map</h1>
          <p className="text-sm text-stone-600">
            تصویر ماهواره‌ای رایگان (Esri) + موقعیت شما + ثبت مزرعه روی نقشه — داده از API
          </p>
        </div>
        <Link to="/satellite" className="inline-flex items-center gap-1 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-bold text-white">
          <Satellite className="h-4 w-4" /> NDVI lab
        </Link>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.4fr_0.9fr]">
        <div className="space-y-3">
          <LeafletPicker
            lat={lat}
            lng={lng}
            height={420}
            showSatellite
            enableGeolocate
            extraMarkers={markers}
            onPick={(a, b) => {
              setLat(a);
              setLng(b);
            }}
          />
          <p className="text-xs text-stone-500">
            Pin: {lat?.toFixed(5)}, {lng?.toFixed(5)} · farms on map: {markers.length}
          </p>
        </div>

        <div className="space-y-4">
          <div className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
            <p className="text-xs font-bold uppercase text-stone-400">Satellite NDVI at pin</p>
            <p className="mt-1 font-display text-3xl font-black tabular-nums text-indigo-800">
              {ndvi != null ? ndvi.toFixed(3) : "—"}
            </p>
            <p className="text-xs text-stone-500">{provider || "Select a point on the map"}</p>
          </div>

          <form onSubmit={onSubmit} className="space-y-3 rounded-2xl border border-emerald-100 bg-emerald-50/40 p-5">
            <h2 className="flex items-center gap-2 font-bold text-stone-800">
              <MapPin className="h-4 w-4 text-emerald-700" /> Register farm here
            </h2>
            {error && <p className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p>}
            {msg && <p className="rounded-lg bg-emerald-100 px-3 py-2 text-sm text-emerald-800">{msg}</p>}
            <input
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Farm name"
              className="w-full rounded-xl border border-stone-200 px-3 py-2.5 text-sm"
            />
            <input
              type="number"
              min={0}
              step="0.1"
              value={areaHa}
              onChange={(e) => setAreaHa(e.target.value)}
              placeholder="Area (ha)"
              className="w-full rounded-xl border border-stone-200 px-3 py-2.5 text-sm"
            />
            <button
              type="submit"
              disabled={loading}
              className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-600 py-3 text-sm font-bold text-white disabled:opacity-60"
            >
              {loading && <Loader2 className="h-4 w-4 animate-spin" />}
              Save farm at this location
            </button>
          </form>

          <div className="rounded-2xl border border-stone-200 bg-white p-4">
            <p className="mb-2 text-xs font-bold text-stone-500">Your farms (API)</p>
            <ul className="max-h-48 space-y-1 overflow-auto text-sm">
              {farms.length === 0 && <li className="text-stone-400">No farms yet</li>}
              {farms.map((f) => (
                <li key={f.id}>
                  <Link className="text-emerald-700 underline" to={`/farms/${f.id}`}>
                    {f.name}
                    {f.latitude != null ? ` (${Number(f.latitude).toFixed(3)}, ${Number(f.longitude).toFixed(3)})` : ""}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
