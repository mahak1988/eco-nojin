import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Satellite, ArrowUpRight, Loader2 } from "lucide-react";
import { useLang, CONTENT } from "./i18n";
import { tr } from "./i18n_extras";
import { apiFetch, v1 } from "../../api/http";

/** Live NDVI — long timeout for Planetary Computer first hit. */
export function SatellitePanel({ lat = 32.65, lon = 51.67 }: { lat?: number; lon?: number }) {
  const { lang } = useLang();
  const pack = (CONTENT[lang] ?? CONTENT.fa) as unknown as Record<string, unknown>;
  const t = (key: string) => tr(pack, lang, key);
  const [ndvi, setNdvi] = useState<number | null>(null);
  const [provider, setProvider] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    apiFetch<Record<string, unknown>>(`${v1("/satellite/ndvi")}?lat=${lat}&lon=${lon}`, {}, 45_000)
      .then((j) => {
        if (cancelled) return;
        const v = Number(j.mean_ndvi ?? j.ndvi ?? j.value);
        setNdvi(Number.isFinite(v) ? v : null);
        setProvider(String(j.provider ?? j.source ?? ""));
        setError(null);
      })
      .catch((e) => {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "API error");
          setNdvi(null);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [lat, lon]);

  const pct = ndvi != null ? Math.max(0, Math.min(100, ndvi * 100)) : 0;

  return (
    <Link
      to="/satellite"
      aria-label={t("panel_ndvi_title")}
      className="group block h-full rounded-[var(--r-lg)] border border-[var(--border-subtle)] bg-[var(--surface-raised)] p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:border-green-300 hover:shadow-md"
    >
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Satellite className="h-4 w-4 text-green-700" />
          <span className="text-xs font-bold text-[var(--text-3)]">{t("panel_ndvi_title")}</span>
        </div>
        <ArrowUpRight className="h-3.5 w-3.5 text-[var(--text-3)] opacity-0 transition-opacity group-hover:opacity-100" />
      </div>
      {loading ? (
        <div className="space-y-2">
          <Loader2 className="h-8 w-8 animate-spin text-emerald-600" />
          <p className="text-[11px] text-stone-400">Planetary Computer…</p>
        </div>
      ) : error ? (
        <>
          <p className="text-sm font-bold text-amber-700">Slow / retry</p>
          <p className="mt-1 line-clamp-2 text-xs text-stone-500">{error}</p>
        </>
      ) : (
        <>
          <p className="font-display text-3xl font-black tabular-nums text-green-700">
            {ndvi != null ? ndvi.toFixed(3) : "—"}
          </p>
          <p className="mt-1 text-xs text-[var(--text-3)]">
            {provider ? `${provider} · ` : ""}
            {t("panel_ndvi_sub")}
          </p>
          <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-stone-100">
            <div
              className="h-full rounded-full bg-green-600 transition-all duration-700"
              style={{ width: `${pct}%` }}
            />
          </div>
        </>
      )}
    </Link>
  );
}
