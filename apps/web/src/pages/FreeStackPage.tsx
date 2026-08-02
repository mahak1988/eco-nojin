import { Link } from "react-router-dom";
import { EoLiveStrip } from "../components/eo/EoLiveStrip";

const LINKS = [
  { to: "/eo", title: "EO Hub", desc: "Sentinel · Landsat · MODIS · DEM · erosion · climate" },
  { to: "/satellite", title: "Satellite dashboard", desc: "NDVI map + timeseries" },
  { to: "/pilots/ndvi", title: "Pilots NDVI", desc: "Batch VCI for international pilots" },
  { to: "/science", title: "Science", desc: "AquaCrop · RothC · free models" },
  { to: "/simulators/aquacrop", title: "AquaCrop-OSPy", desc: "Crop water productivity" },
  { to: "/simulators/rothc", title: "pyRothC", desc: "Soil carbon" },
];

export default function FreeStackPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-6 p-5 sm:p-8">
      <h1 className="font-display text-3xl text-stone-900">Free science stack</h1>
      <p className="text-sm text-stone-600">
        همه مسیرها بدون API پولی: Planetary Computer، Open-Meteo، AquaCrop-OSPy، pyRothC.
      </p>
      <EoLiveStrip lat={32.65} lon={51.67} />
      <div className="grid gap-3 sm:grid-cols-2">
        {LINKS.map((l) => (
          <Link
            key={l.to}
            to={l.to}
            className="rounded-2xl border border-stone-200 bg-white p-4 shadow-sm transition hover:border-emerald-300 hover:shadow-md"
          >
            <p className="font-bold text-stone-800">{l.title}</p>
            <p className="mt-1 text-xs text-stone-500">{l.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
