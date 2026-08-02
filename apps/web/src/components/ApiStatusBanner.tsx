import { useEffect, useState } from "react";

/**
 * Single shared health probe — avoids N parallel /health spam from StrictMode remounts.
 * Prefer Vite proxy /health only (same-origin). Direct :8000 is fallback.
 */
let lastOk: boolean | null = null;
let lastDetail = "";
let lastAt = 0;
let inflight: Promise<{ ok: boolean; detail: string }> | null = null;
const CACHE_MS = 8_000;
const POLL_MS = 60_000;

async function probeHealth(): Promise<{ ok: boolean; detail: string }> {
  const now = Date.now();
  if (inflight) return inflight;
  if (lastOk !== null && now - lastAt < CACHE_MS) {
    return { ok: lastOk, detail: lastDetail };
  }

  inflight = (async () => {
    const paths = ["/health", "http://127.0.0.1:8000/health"];
    let lastErr = "";
    for (const url of paths) {
      const ctrl = new AbortController();
      const t = setTimeout(() => ctrl.abort(), 8_000);
      try {
        const res = await fetch(url, {
          signal: ctrl.signal,
          credentials: url.startsWith("http") ? "omit" : "include",
          headers: { Accept: "application/json" },
        });
        clearTimeout(t);
        if (!res.ok) {
          lastErr = `HTTP ${res.status}`;
          continue;
        }
        const j = (await res.json()) as { status?: string };
        const detail = `${j.status ?? "ok"}`;
        lastOk = true;
        lastDetail = detail;
        lastAt = Date.now();
        return { ok: true, detail };
      } catch (e) {
        clearTimeout(t);
        lastErr = e instanceof Error ? e.message : String(e);
      }
    }
    lastOk = false;
    lastDetail = lastErr || "unreachable";
    lastAt = Date.now();
    return { ok: false, detail: lastDetail };
  })();

  try {
    return await inflight;
  } finally {
    inflight = null;
  }
}

export function ApiStatusBanner() {
  const [ok, setOk] = useState<boolean | null>(lastOk);
  const [detail, setDetail] = useState(lastDetail);

  useEffect(() => {
    let cancelled = false;
    const run = () => {
      probeHealth().then((r) => {
        if (cancelled) return;
        setOk(r.ok);
        setDetail(r.detail);
      });
    };
    run();
    const id = window.setInterval(run, POLL_MS);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, []);

  if (ok === null) {
    return (
      <div className="border-b border-stone-200 bg-stone-50 px-3 py-1 text-center text-[11px] text-stone-500">
        Checking API…
      </div>
    );
  }
  if (ok) {
    return (
      <div className="border-b border-emerald-200 bg-emerald-50 px-3 py-1 text-center text-[11px] font-medium text-emerald-800">
        Live · API connected · {detail}
      </div>
    );
  }
  return (
    <div className="border-b border-amber-300 bg-amber-50 px-3 py-2 text-center text-xs text-amber-900">
      <strong>Backend offline from browser.</strong> Keep uvicorn on :8000 and open{" "}
      <code className="rounded bg-amber-100 px-1">http://127.0.0.1:5173</code> (not LAN IP).
      <span className="mt-1 block text-[11px] opacity-80">{detail}</span>
    </div>
  );
}
