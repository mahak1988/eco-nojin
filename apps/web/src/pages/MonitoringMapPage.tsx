import { useState } from "react";
import { Link } from "react-router-dom";
import { Map, MapPin, Crosshair, Navigation } from "lucide-react";
import { LeafletPicker } from "../components/maps/LeafletPicker";
import { useLang } from "../components/eco/i18n";
import { tExtra } from "../components/eco/i18n_extras";

const PRESETS = [
  { id: "isfahan", lat: 32.65, lng: 51.67, label: "Isfahan" },
  { id: "tehran", lat: 35.69, lng: 51.39, label: "Tehran" },
  { id: "shiraz", lat: 29.59, lng: 52.58, label: "Shiraz" },
  { id: "ahvaz", lat: 31.32, lng: 48.67, label: "Ahvaz" },
];

export default function MonitoringMapPage() {
  const { lang } = useLang();
  const tx = (k: string) => tExtra(lang, k);
  const [lat, setLat] = useState(32.65);
  const [lng, setLng] = useState(51.67);
  const [geoLoading, setGeoLoading] = useState(false);

  const useGps = () => {
    if (!navigator.geolocation) return;
    setGeoLoading(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLat(Number(pos.coords.latitude.toFixed(5)));
        setLng(Number(pos.coords.longitude.toFixed(5)));
        setGeoLoading(false);
      },
      () => setGeoLoading(false),
      { enableHighAccuracy: true, timeout: 10000 },
    );
  };

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-5 sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="grid h-12 w-12 place-items-center rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-700 text-white shadow-lg shadow-emerald-500/25">
            <Map className="h-6 w-6" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">{tx("mon_map_title")}</h1>
            <p className="text-sm text-stone-500">{tx("mon_map_sub")}</p>
          </div>
        </div>
        <Link
          to="/monitoring"
          className="rounded-xl border border-stone-200 bg-white px-3 py-2 text-sm font-bold text-cyan-800 shadow-sm"
        >
          {tx("mon_back_hub")}
        </Link>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-1">
          <div className="rounded-3xl border border-stone-200/80 bg-white p-5 shadow-sm">
            <p className="mb-3 flex items-center gap-1.5 text-xs font-bold uppercase tracking-wide text-stone-400">
              <MapPin className="h-3.5 w-3.5" />
              {tx("mon_map_coords")}
            </p>
            <div className="grid grid-cols-2 gap-2">
              <label className="text-xs font-medium text-stone-600">
                Lat
                <input
                  type="number"
                  step="any"
                  value={lat}
                  onChange={(e) => setLat(Number(e.target.value))}
                  className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm font-bold tabular-nums"
                />
              </label>
              <label className="text-xs font-medium text-stone-600">
                Lng
                <input
                  type="number"
                  step="any"
                  value={lng}
                  onChange={(e) => setLng(Number(e.target.value))}
                  className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2 text-sm font-bold tabular-nums"
                />
              </label>
            </div>
            <button
              type="button"
              onClick={useGps}
              disabled={geoLoading}
              className="mt-3 inline-flex w-full items-center justify-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50 py-2.5 text-xs font-bold text-emerald-800 hover:bg-emerald-100 disabled:opacity-60"
            >
              <Crosshair className={`h-3.5 w-3.5 ${geoLoading ? "animate-spin" : ""}`} />
              GPS
            </button>
            <p className="mt-3 text-xs leading-relaxed text-stone-500">{tx("mon_map_hint")}</p>
          </div>

          <div className="rounded-3xl border border-stone-200/80 bg-white p-5 shadow-sm">
            <p className="mb-3 flex items-center gap-1.5 text-xs font-bold uppercase text-stone-400">
              <Navigation className="h-3.5 w-3.5" />
              {tx("mon_map_presets")}
            </p>
            <div className="flex flex-wrap gap-2">
              {PRESETS.map((p) => (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => {
                    setLat(p.lat);
                    setLng(p.lng);
                  }}
                  className={`rounded-full px-3 py-1.5 text-xs font-bold transition ${
                    Math.abs(lat - p.lat) < 0.02 && Math.abs(lng - p.lng) < 0.02
                      ? "bg-emerald-600 text-white"
                      : "bg-stone-100 text-stone-700 hover:bg-stone-200"
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="overflow-hidden rounded-3xl border border-stone-200/80 bg-white shadow-sm lg:col-span-2">
          <LeafletPicker
            lat={lat}
            lng={lng}
            onPick={(a, b) => {
              setLat(a);
              setLng(b);
            }}
          />
        </div>
      </div>
    </div>
  );
}
