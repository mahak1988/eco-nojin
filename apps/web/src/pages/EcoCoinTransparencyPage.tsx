/**
 * Phase 4 — Public transparency: treasury buckets + mode.
 * Route: /ecocoin/transparency
 */
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, PieChart, Loader2, Shield } from "lucide-react";
import { getTreasury, type TreasuryOut } from "../lib/ecocoinLedgerApi";

function fmt(n: string | number | undefined) {
  if (n === undefined || n === null) return "—";
  const x = Number(n);
  if (Number.isNaN(x)) return String(n);
  return x.toLocaleString(undefined, { maximumFractionDigits: 0 });
}

const BUCKET_COLORS: Record<string, string> = {
  COMMUNITY: "bg-emerald-500",
  ORG: "bg-sky-500",
  TREASURY: "bg-amber-500",
  SCIENCE: "bg-violet-500",
  FOUNDERS: "bg-stone-400",
};

export default function EcoCoinTransparencyPage() {
  const [data, setData] = useState<TreasuryOut | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void getTreasury()
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : String(e)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-stone-50 text-stone-900">
      <div className="mx-auto max-w-3xl px-4 py-8">
        <Link
          to="/ecocoin"
          className="mb-6 inline-flex items-center gap-2 text-sm text-emerald-700 hover:underline"
        >
          <ArrowLeft className="h-4 w-4" /> Back to EcoCoin
        </Link>

        <div className="mb-6 flex items-center gap-3">
          <div className="rounded-xl bg-emerald-100 p-3">
            <PieChart className="h-6 w-6 text-emerald-700" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Treasury transparency</h1>
            <p className="text-sm text-stone-600">
              Hard cap 1B ECO · Community 55% · impact-only mint
            </p>
          </div>
        </div>

        <div className="mb-4 flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          <Shield className="mt-0.5 h-4 w-4 shrink-0" />
          <p>
            EcoCoin is an educational–scientific incentive token. It is{" "}
            <strong>not</strong> a carbon credit registry product. Mode shown is
            the backend settlement path ({data?.mode ?? "…"}).
          </p>
        </div>

        {loading && (
          <div className="flex justify-center py-16">
            <Loader2 className="h-8 w-8 animate-spin text-emerald-600" />
          </div>
        )}

        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">
            <p className="font-medium">Could not load treasury</p>
            <p className="mt-1 font-mono text-xs">{error}</p>
            <p className="mt-2 text-stone-600">
              Ensure ledger routes are mounted and migration seed ran. Until
              then, buckets may be empty.
            </p>
          </div>
        )}

        {data && (
          <>
            <div className="mb-6 grid grid-cols-2 gap-4">
              <div className="rounded-2xl border border-stone-200 bg-white p-4">
                <p className="text-xs uppercase text-stone-500">Total allocated</p>
                <p className="text-2xl font-bold">{fmt((data as any).total_allocated ?? data.max_supply)}</p>
              </div>
              <div className="rounded-2xl border border-stone-200 bg-white p-4">
                <p className="text-xs uppercase text-stone-500">Total remaining</p>
                <p className="text-2xl font-bold text-emerald-700">
                  {fmt((data as any).total_remaining)}
                </p>
              </div>
            </div>

            <ul className="space-y-3">
              {(data.buckets || []).map((b: any) => {
                const alloc = Number(b.allocation ?? b.total_allocated) || 1;
                const rem = Number(b.remaining) || 0;
                const pct = Math.min(100, Math.round((rem / alloc) * 100));
                return (
                  <li
                    key={b.code}
                    className="rounded-2xl border border-stone-200 bg-white p-4 shadow-sm"
                  >
                    <div className="mb-2 flex items-center justify-between">
                      <div>
                        <p className="font-semibold">
                          {b.name || b.code}{" "}
                          <span className="font-mono text-xs text-stone-500">
                            {b.code}
                          </span>
                        </p>
                        {b.description && (
                          <p className="text-xs text-stone-500">{b.description}</p>
                        )}
                      </div>
                      <span className="text-sm text-stone-600">{b.status || "active"}</span>
                    </div>
                    <div className="mb-1 h-2 overflow-hidden rounded-full bg-stone-100">
                      <div
                        className={`h-full ${BUCKET_COLORS[b.code] || "bg-emerald-500"}`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <div className="flex justify-between text-xs text-stone-600">
                      <span>Remaining {fmt(b.remaining)}</span>
                      <span>of {fmt(b.allocation ?? b.total_allocated)}</span>
                    </div>
                  </li>
                );
              })}
            </ul>

            {(data.buckets || []).length === 0 && (
              <p className="text-center text-sm text-stone-500">
                No buckets yet — run Alembic seed for eco_treasury_buckets.
              </p>
            )}
          </>
        )}

        <div className="mt-8 flex flex-wrap gap-3 text-sm">
          <Link
            to="/ecocoin/claims/new"
            className="rounded-lg bg-emerald-600 px-4 py-2 text-white hover:bg-emerald-700"
          >
            Submit a claim
          </Link>
          <Link to="/ecocoin" className="rounded-lg border px-4 py-2 hover:bg-stone-100">
            Wallet hub
          </Link>
        </div>
      </div>
    </div>
  );
}
