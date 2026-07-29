import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { MapPinned, Loader2 } from "lucide-react";

export default function SatelliteFieldMapPage() {
  const [geo, setGeo] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    void fetch("/api/v1/satellite/fields", { credentials: "include" })
      .then((r) => r.json())
      .then(setGeo);
  }, []);

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-5 sm:p-8">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <MapPinned className="h-5 w-5 text-indigo-700" />
          <h1 className="font-display text-3xl">Field map · نقشه مزرعه</h1>
        </div>
        <Link to="/satellite" className="text-sm font-bold text-indigo-700">
          ← Dashboard
        </Link>
      </div>
      {!geo ? (
        <Loader2 className="mx-auto h-8 w-8 animate-spin" />
      ) : (
        <pre className="overflow-auto rounded-2xl border bg-white p-4 text-xs">
          {JSON.stringify(geo, null, 2)}
        </pre>
      )}
    </div>
  );
}
