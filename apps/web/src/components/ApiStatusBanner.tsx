import { useEffect, useState } from "react";

/**
 * Probe API via Vite proxy first, then direct 127.0.0.1:8000 (CORS must allow).
 * Avoids false "offline" when proxy is misconfigured but uvicorn is up.
 */
async function probeHealth(): Promise<{ ok: boolean; detail: string }> {
  const paths = ["/health", "http://127.0.0.1:8000/health"];
  let lastErr = "";
  for (const url of paths) {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), 12_000);
    try {
      const res = await fetch(url, {
        signal: ctrl.signal,
        credentials: url.startsWith("http") ? "omit" : "include",
        headers: { Accept: "application/json" },
      });
      clearTimeout(t);
      if (!res.ok) {
        lastErr = `HTTP ${res.status} @ ${url}`;
        continue;
      }
      const j = (await res.json()) as { status?: string };
      return { ok: true, detail: `${j.status ?? "ok"} via ${url}` };
    } catch (e) {
      clearTimeout(t);
      lastErr = e instanceof Error ? e.message : String(e);
    }
  }
  return {
    ok: false,
    detail: lastErr || "unreachable",
  };
}

export function ApiStatusBanner() {
  const [ok, setOk] = useState<boolean | null>(null);
  const [detail, setDetail] = useState("");

  useEffect(() => {
    let cancelled = false;
    probeHealth().then((r) => {
      if (cancelled) return;
      setOk(r.ok);
      setDetail(r.detail);
    });
    const id = window.setInterval(() => {
      probeHealth().then((r) => {
        if (cancelled) return;
        setOk(r.ok);
        setDetail(r.detail);
      });
    }, 30_000);
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
        API connected · {detail}
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
