import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { CloudSun, ArrowUpRight, Loader2 } from "lucide-react";
import { useLang, CONTENT } from "./i18n";
import { tr } from "./i18n_extras";

/** Live weather via Open-Meteo (free, no key) — same stack as backend. */
export function WeatherPanel({ lat = 32.65, lon = 51.67 }: { lat?: number; lon?: number }) {
  const { lang } = useLang();
  const pack = (CONTENT[lang] ?? CONTENT.fa) as unknown as Record<string, unknown>;
  const t = (key: string) => tr(pack, lang, key);
  const [temp, setTemp] = useState<number | null>(null);
  const [wind, setWind] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const url =
      `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}` +
      `&current=temperature_2m,wind_speed_10m&timezone=auto`;
    fetch(url)
      .then((r) => r.json())
      .then((j) => {
        if (cancelled) return;
        const c = j.current || {};
        setTemp(typeof c.temperature_2m === "number" ? c.temperature_2m : null);
        setWind(typeof c.wind_speed_10m === "number" ? c.wind_speed_10m : null);
        setError(null);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "weather error");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [lat, lon]);

  return (
    <Link
      to="/weather"
      className="group block h-full rounded-[var(--r-lg)] border border-[var(--border-subtle)] bg-[var(--surface-raised)] p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:border-sky-300 hover:shadow-md"
    >
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <CloudSun className="h-4 w-4 text-sky-700" />
          <span className="text-xs font-bold text-[var(--text-3)]">{t("panel_weather_title") || "Weather"}</span>
        </div>
        <ArrowUpRight className="h-3.5 w-3.5 opacity-0 transition-opacity group-hover:opacity-100" />
      </div>
      {loading ? (
        <Loader2 className="h-8 w-8 animate-spin text-sky-600" />
      ) : error ? (
        <p className="text-sm text-rose-600">{error}</p>
      ) : (
        <>
          <p className="font-display text-3xl font-black tabular-nums text-sky-800">
            {temp != null ? `${temp.toFixed(1)}°` : "—"}
          </p>
          <p className="mt-1 text-xs text-[var(--text-3)]">
            Open-Meteo · wind {wind != null ? `${wind.toFixed(1)} km/h` : "—"}
          </p>
        </>
      )}
    </Link>
  );
}
