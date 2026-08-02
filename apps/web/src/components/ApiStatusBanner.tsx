import { useEffect, useState } from "react";
import { apiFetch } from "../api/http";

/** Non-blocking banner: shows whether Vite proxy → FastAPI works. */
export function ApiStatusBanner() {
  const [ok, setOk] = useState<boolean | null>(null);
  const [detail, setDetail] = useState("");

  useEffect(() => {
    let cancelled = false;
    apiFetch<Record<string, unknown>>("/health", {}, 4000)
      .then((h) => {
        if (cancelled) return;
        setOk(true);
        setDetail(String(h.status ?? "ok"));
      })
      .catch((e) => {
        if (cancelled) return;
        setOk(false);
        setDetail(e instanceof Error ? e.message : "offline");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (ok === null) return null;
  if (ok) {
    return (
      <div className="border-b border-emerald-200 bg-emerald-50 px-3 py-1 text-center text-[11px] font-medium text-emerald-800">
        API connected · /health = {detail}
      </div>
    );
  }
  return (
    <div className="border-b border-amber-300 bg-amber-50 px-3 py-2 text-center text-xs text-amber-900">
      <strong>Backend offline.</strong> Start API then refresh:{" "}
      <code className="rounded bg-amber-100 px-1">uvicorn apps.main:app --reload --port 8000</code>
      <span className="mt-1 block text-[11px] opacity-80">{detail}</span>
    </div>
  );
}
