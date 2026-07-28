import { useCallback, useEffect, useState } from "react";
import {
  getScienceNdviCanopy,
  getScienceRuns,
  getScienceStatus,
  postAquaCropAdvanced,
  postSwat,
} from "../lib/apiServices";

type LoadState = "idle" | "loading" | "ok" | "error";

export default function SciencePage() {
  const [status, setStatus] = useState<Record<string, unknown> | null>(null);
  const [runs, setRuns] = useState<unknown[]>([]);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [ndvi, setNdvi] = useState<Record<string, unknown> | null>(null);
  const [state, setState] = useState<LoadState>("idle");
  const [err, setErr] = useState<string | null>(null);
  const [lat, setLat] = useState(32.65);
  const [lon, setLon] = useState(51.67);
  const [days, setDays] = useState(40);

  const refresh = useCallback(async () => {
    setState("loading");
    setErr(null);
    const [st, rn] = await Promise.all([getScienceStatus(), getScienceRuns()]);
    if (st.source === "error") {
      setState("error");
      setErr(st.errorMessage || "science status failed");
      return;
    }
    setStatus(st.data as Record<string, unknown>);
    setRuns(((rn.data as { data?: unknown[] })?.data as unknown[]) || []);
    setState("ok");
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  async function runAqua() {
    setState("loading");
    const res = await postAquaCropAdvanced({
      days,
      rain_mm_day: 0.4,
      crop: "wheat",
      lat,
      lon,
      use_ndvi_canopy: true,
      persist: true,
    });
    if (res.source === "error") {
      setErr(res.errorMessage || "aquacrop failed");
      setState("error");
      return;
    }
    setResult(res.data as Record<string, unknown>);
    setState("ok");
    void refresh();
  }

  async function runSwat() {
    setState("loading");
    const res = await postSwat({ days: 365, precip_mm_year: 320, curve_number: 75, persist: true });
    if (res.source === "error") {
      setErr(res.errorMessage || "swat failed");
      setState("error");
      return;
    }
    setResult(res.data as Record<string, unknown>);
    setState("ok");
    void refresh();
  }

  async function loadNdvi() {
    setState("loading");
    const res = await getScienceNdviCanopy(lat, lon, 60);
    if (res.source === "error") {
      setErr(res.errorMessage || "ndvi failed");
      setState("error");
      return;
    }
    setNdvi(res.data as Record<string, unknown>);
    setState("ok");
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-6">
      <header>
        <h1 className="font-display text-3xl text-stone-900">Science / فاز علمی</h1>
        <p className="mt-1 text-sm text-stone-600">
          AquaCrop conceptual (FAO Ky), RothC-26.3, SCS-CN basin, NDVI→canopy — process models, not
          official FAO/SWAT binaries.
        </p>
      </header>

      {state === "loading" && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm">Loading…</div>
      )}
      {err && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{err}</div>
      )}

      <section className="grid gap-4 rounded-2xl border border-stone-200 bg-white p-4 shadow-sm md:grid-cols-2">
        <div>
          <h2 className="text-sm font-bold uppercase tracking-wide text-stone-500">Status</h2>
          <pre className="mt-2 max-h-40 overflow-auto rounded-lg bg-stone-50 p-3 text-xs">
            {status ? JSON.stringify(status, null, 2) : "—"}
          </pre>
        </div>
        <div className="space-y-2">
          <label className="block text-xs font-medium text-stone-600">
            Lat
            <input
              type="number"
              step="0.01"
              value={lat}
              onChange={(e) => setLat(Number(e.target.value))}
              className="mt-1 w-full rounded-lg border border-stone-200 px-3 py-2 text-sm"
            />
          </label>
          <label className="block text-xs font-medium text-stone-600">
            Lon
            <input
              type="number"
              step="0.01"
              value={lon}
              onChange={(e) => setLon(Number(e.target.value))}
              className="mt-1 w-full rounded-lg border border-stone-200 px-3 py-2 text-sm"
            />
          </label>
          <label className="block text-xs font-medium text-stone-600">
            Days (AquaCrop)
            <input
              type="number"
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="mt-1 w-full rounded-lg border border-stone-200 px-3 py-2 text-sm"
            />
          </label>
          <div className="flex flex-wrap gap-2 pt-2">
            <button
              type="button"
              onClick={() => void runAqua()}
              className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-bold text-white"
            >
              Run AquaCrop
            </button>
            <button
              type="button"
              onClick={() => void runSwat()}
              className="rounded-xl bg-sky-600 px-4 py-2 text-sm font-bold text-white"
            >
              Run SCS-CN / SWAT proxy
            </button>
            <button
              type="button"
              onClick={() => void loadNdvi()}
              className="rounded-xl bg-violet-600 px-4 py-2 text-sm font-bold text-white"
            >
              NDVI → canopy
            </button>
            <button
              type="button"
              onClick={() => void refresh()}
              className="rounded-xl border border-stone-300 px-4 py-2 text-sm font-semibold"
            >
              Refresh
            </button>
          </div>
        </div>
      </section>

      {result && (
        <section className="rounded-2xl border border-emerald-200 bg-emerald-50/40 p-4">
          <h2 className="font-semibold text-stone-800">Last model result</h2>
          <pre className="mt-2 max-h-64 overflow-auto text-xs">{JSON.stringify(result, null, 2)}</pre>
        </section>
      )}

      {ndvi && (
        <section className="rounded-2xl border border-violet-200 bg-violet-50/40 p-4">
          <h2 className="font-semibold text-stone-800">NDVI / canopy</h2>
          <p className="text-sm text-stone-600">provider: {String(ndvi.provider)} · count: {String(ndvi.count)}</p>
          <pre className="mt-2 max-h-40 overflow-auto text-xs">{JSON.stringify(ndvi, null, 2)}</pre>
        </section>
      )}

      <section className="rounded-2xl border border-stone-200 bg-white p-4">
        <h2 className="font-semibold text-stone-800">Persisted runs</h2>
        {runs.length === 0 ? (
          <p className="mt-2 text-sm text-stone-500">Empty — run a model with persist=true</p>
        ) : (
          <ul className="mt-2 divide-y divide-stone-100 text-sm">
            {runs.map((r, i) => {
              const row = r as { id?: number; model?: string; status?: string; created_at?: string };
              return (
                <li key={row.id ?? i} className="flex justify-between py-2">
                  <span>
                    #{row.id} {row.model}
                  </span>
                  <span className="text-stone-500">{row.created_at}</span>
                </li>
              );
            })}
          </ul>
        )}
      </section>
    </div>
  );
}
