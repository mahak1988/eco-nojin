import { useEffect, useState } from "react";
import { CloudSun, Loader2 } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { tExtra } from "../components/eco/i18n_extras";

export default function WeatherPage() {
  const { lang } = useLang();
  const tx = (k: string) => tExtra(lang, k);
  const [data, setData] = useState<{
    provider: string;
    daily?: Array<Record<string, unknown>>;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/v1/weather/forecast?lat=32.6&lon=51.7&days=7", {
      credentials: "include",
      headers: { Accept: "application/json" },
    })
      .then((r) => r.json())
      .then(setData)
      .catch((e) => setError(String(e)));
  }, []);

  if (error) return <div className="p-8 text-rose-700">{error}</div>;
  if (!data)
    return (
      <div className="flex justify-center py-24">
        <Loader2 className="h-8 w-8 animate-spin text-sky-600" />
      </div>
    );

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-5 sm:p-8">
      <div className="flex items-center gap-3">
        <div className="grid h-11 w-11 place-items-center rounded-xl bg-sky-50">
          <CloudSun className="h-5 w-5 text-sky-700" />
        </div>
        <div>
          <h1 className="font-display text-3xl text-stone-800">{tx("weather_title")}</h1>
          <p className="text-sm text-stone-500">
            {tx("weather_sub")}: {data.provider} · {tx("weather_days")}
          </p>
        </div>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {(data.daily || []).map((d) => (
          <div key={String(d.date)} className="rounded-2xl border bg-white p-4 shadow-sm">
            <p className="font-bold text-stone-800">{String(d.date)}</p>
            <p className="text-sm text-stone-500">{String(d.condition)}</p>
            <p className="mt-2 text-lg font-black text-sky-800">
              {String(d.temp_max_c)}° / {String(d.temp_min_c)}°
            </p>
            <p className="text-xs text-stone-500">
              rain {String(d.precip_mm)} mm · ET0 {String(d.et0_mm)} · RH {String(d.humidity_pct)}%
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
