import { useState } from "react";
import { Link } from "react-router-dom";
import { Map } from "lucide-react";
import { LeafletPicker } from "../components/maps/LeafletPicker";

export default function MonitoringMapPage() {
  const [lat, setLat] = useState(32.65);
  const [lng, setLng] = useState(51.67);

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-5 sm:p-8">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-emerald-50">
            <Map className="h-5 w-5 text-emerald-700" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">Monitoring map</h1>
            <p className="text-sm text-stone-500">نقشه پایش — {lat.toFixed(4)}, {lng.toFixed(4)}</p>
          </div>
        </div>
        <Link to="/monitoring" className="text-sm font-bold text-cyan-700">
          ← Hub
        </Link>
      </div>
      <LeafletPicker lat={lat} lng={lng} onPick={(a, b) => { setLat(a); setLng(b); }} />
    </div>
  );
}
