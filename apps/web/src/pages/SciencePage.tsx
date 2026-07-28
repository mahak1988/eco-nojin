import { useCallback, useEffect, useState } from "react";
import {
  getScienceNdviCanopy,
  getScienceRuns,
  getScienceStatus,
  postAquaCropAdvanced,
  postSwat,
} from "../lib/apiServices";

type LoadState = "idle" | "loading" | "ok" | "error";

type Analysis = {
  summary_fa?: string;
  summary_en?: string;
  formulas?: string[];
  advice_fa?: string;
  advice_en?: string;
};

const FORMULA_GUIDE = [
  {
    id: "scs",
    title: "SCS-CN / حوضه",
    formulas: ["S = 25.4×(1000/CN−10)", "Q = (P−0.2S)²/(P+0.8S) اگر P>0.2S"],
    text: "شماره منحنی (CN) نفوذپذیری و پوشش را خلاصه می‌کند. S ظرفیت نگهداشت است. اگر هر واقعه بارش از ۰.۲S کمتر باشد، رواناب سطحی صفر می‌شود (مثل خروجی شما با بارش کم).",
  },
  {
    id: "aqua",
    title: "AquaCrop مفهومی + Ky",
    formulas: ["ETc = Kc×ET0", "Y/Yx = 1 − Ky(1 − Ta/Tc)"],
    text: "تعرق واقعی (Ta) نسبت به بالقوه (Tc) با تنش رطوبت ریشه (Ks) کم می‌شود. Ky حساسیت عملکرد محصول به کمبود آب است (گندم≈۱.۱۵).",
  },
  {
    id: "ndvi",
    title: "NDVI → پوشش تاج",
    formulas: ["NDVI = (NIR−Red)/(NIR+Red)", "CC = clamp((NDVI−0.15)/0.70)"],
    text: "پوشش تاج برای مقیاس‌کردن Kc در بیلان آب استفاده می‌شود. بدون GEE ممکن است سری ساختگی باشد.",
  },
  {
    id: "rothc",
    title: "RothC-26.3",
    formulas: ["استخرهای DPM/RPM/BIO/HUM/IOM", "نرخ × a(T)×b(رطوبت)×c(پوشش)"],
    text: "تحول کربن آلی خاک در چند سال؛ ورودی بقایا و کود آلی SOC را بالا می‌برد.",
  },
];

function AnalysisBlock({ a }: { a?: Analysis }) {
  if (!a) return null;
  return (
    <div className="mt-3 space-y-2 rounded-xl border border-emerald-200 bg-white/80 p-4 text-sm text-stone-700">
      {a.summary_fa && (
        <p>
          <span className="font-bold text-emerald-800">تحلیل: </span>
          {a.summary_fa}
        </p>
      )}
      {a.summary_en && <p className="text-stone-500">{a.summary_en}</p>}
      {a.formulas && a.formulas.length > 0 && (
        <ul className="list-inside list-disc font-mono text-xs text-stone-600">
          {a.formulas.map((f) => (
            <li key={f}>{f}</li>
          ))}
        </ul>
      )}
      {a.advice_fa && (
        <p className="rounded-lg bg-amber-50 px-3 py-2 text-amber-900">
          <span className="font-semibold">توصیه: </span>
          {a.advice_fa}
        </p>
      )}
    </div>
  );
}

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
    setErr(null);
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
    setErr(null);
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
    setErr(null);
    const res = await getScienceNdviCanopy(lat, lon, 60);
    if (res.source === "error") {
      setErr(res.errorMessage || "ndvi failed");
      setState("error");
      return;
    }
    setNdvi(res.data as Record<string, unknown>);
    setState("ok");
  }

  const analysis = (result?.analysis || ndvi?.analysis) as Analysis | undefined;

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-6">
      <header>
        <h1 className="font-display text-3xl text-stone-900">Science / فاز علمی</h1>
        <p className="mt-1 text-sm text-stone-600">
          مدل‌های فرایندی با فرمول‌های منتشرشده (FAO Ky، RothC، SCS-CN، NDVI) — نه باینری رسمی FAO/SWAT+.
          هر اجرا «تحلیل + توصیه» برمی‌گرداند.
        </p>
      </header>

      <section className="grid gap-3 md:grid-cols-2">
        {FORMULA_GUIDE.map((g) => (
          <article key={g.id} className="rounded-2xl border border-stone-200 bg-stone-50 p-4">
            <h3 className="font-semibold text-stone-900">{g.title}</h3>
            <ul className="mt-2 list-inside list-disc font-mono text-xs text-emerald-800">
              {g.formulas.map((f) => (
                <li key={f}>{f}</li>
              ))}
            </ul>
            <p className="mt-2 text-sm leading-relaxed text-stone-600">{g.text}</p>
          </article>
        ))}
      </section>

      {state === "loading" && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm">در حال اجرا…</div>
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
              Run SCS-CN
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
          <h2 className="font-semibold text-stone-800">نتیجه مدل</h2>
          <AnalysisBlock a={(result.analysis as Analysis) || analysis} />
          {result.persist_error ? (
            <p className="mt-2 text-xs text-amber-700">persist: {String(result.persist_error)}</p>
          ) : result.run_id ? (
            <p className="mt-2 text-xs text-emerald-700">ذخیره شد · run_id={String(result.run_id)}</p>
          ) : null}
          <details className="mt-3">
            <summary className="cursor-pointer text-xs font-semibold text-stone-500">JSON خام</summary>
            <pre className="mt-2 max-h-64 overflow-auto text-xs">{JSON.stringify(result, null, 2)}</pre>
          </details>
        </section>
      )}

      {ndvi && (
        <section className="rounded-2xl border border-violet-200 bg-violet-50/40 p-4">
          <h2 className="font-semibold text-stone-800">NDVI / canopy</h2>
          <p className="text-sm text-stone-600">
            provider: {String(ndvi.provider)} · count: {String(ndvi.count)}
          </p>
          <AnalysisBlock a={ndvi.analysis as Analysis} />
          <details className="mt-3">
            <summary className="cursor-pointer text-xs font-semibold text-stone-500">JSON خام</summary>
            <pre className="mt-2 max-h-40 overflow-auto text-xs">{JSON.stringify(ndvi, null, 2)}</pre>
          </details>
        </section>
      )}

      <section className="rounded-2xl border border-stone-200 bg-white p-4">
        <h2 className="font-semibold text-stone-800">اجراهای ذخیره‌شده</h2>
        {runs.length === 0 ? (
          <p className="mt-2 text-sm text-stone-500">خالی — یک مدل با persist اجرا کنید</p>
        ) : (
          <ul className="mt-2 divide-y divide-stone-100 text-sm">
            {runs.map((r, i) => {
              const row = r as { id?: number; model?: string; created_at?: string };
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
