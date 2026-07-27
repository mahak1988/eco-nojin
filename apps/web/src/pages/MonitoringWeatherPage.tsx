import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Cloud, Loader2 } from "lucide-react";

export default function MonitoringWeatherPage() {
  const [data, setData] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    void fetch("/api/v1/weather/forecast?lat=32.65&lon=51.67", { credentials: "include" })
      .then((r) => r.json())
      .then(setData)
      .catch(() => setData({ error: "unavailable" }));
  }, []);

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-5 sm:p-8">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-amber-50">
            <Cloud className="h-5 w-5 text-amber-700" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">Weather monitoring</h1>
            <p className="text-sm text-stone-500">پایش هواشناسی</p>
          </div>
        </div>
        <Link to="/monitoring" className="text-sm font-bold text-cyan-700">
          ← Hub
        </Link>
      </div>
      {!data ? (
        <Loader2 className="mx-auto h-8 w-8 animate-spin" />
      ) : (
        <pre className="overflow-auto rounded-2xl border bg-white p-4 text-xs">
          {JSON.stringify(data, null, 2)}
        </pre>
      )}
    </div>
  );
}
