/** EcoCoin transparency + trust monitor — /ecocoin/transparency */
import { useEffect, useState, useMemo } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, PieChart, Loader2, Shield, CheckCircle2, XCircle, Coins, Flame, Lock, RefreshCw } from "lucide-react";
import { getTreasury, type TreasuryOut } from "../lib/ecocoinLedgerApi";
import { readSupply, trustSignals, trustScore, type EcoSupplySnapshot } from "../lib/ecocoinTrustStore";
import { useLang } from "../components/eco/i18n";

function fmt(n: string | number | undefined) {
  if (n === undefined || n === null) return "—";
  const x = Number(n);
  if (Number.isNaN(x)) return String(n);
  return x.toLocaleString(undefined, { maximumFractionDigits: 0 });
}

const BUCKET_COLORS: Record<string, string> = {
  COMMUNITY: "bg-emerald-500", ORG: "bg-sky-500", TREASURY: "bg-amber-500", SCIENCE: "bg-violet-500", FOUNDERS: "bg-stone-400",
};

export default function EcoCoinTransparencyPage() {
  const { lang } = useLang();
  const [data, setData] = useState<TreasuryOut | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [local, setLocal] = useState<EcoSupplySnapshot>(() => readSupply());

  const load = () => {
    setLoading(true); setError(null);
    void getTreasury()
      .then((t) => {
        setData(t);
        const minted = Number((t as any).total_minted ?? t.max_supply);
        if (!Number.isNaN(minted) && minted > 0) {
          setLocal((prev) => ({
            ...prev, totalMinted: Math.min(prev.maxSupply, minted),
            mode: (t.mode as EcoSupplySnapshot["mode"]) || "local_ledger",
            lastUpdated: new Date().toISOString(),
          }));
        }
      })
      .catch((e) => { setError(e instanceof Error ? e.message : String(e)); setLocal(readSupply()); })
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);
  const signals = useMemo(() => trustSignals(local), [local]);
  const score = useMemo(() => trustScore(local), [local]);

  return (
    <div className="min-h-screen bg-stone-50 text-stone-900">
      <div className="mx-auto max-w-3xl px-4 py-8">
        <Link to="/ecocoin" className="mb-6 inline-flex items-center gap-2 text-sm text-emerald-700 hover:underline">
          <ArrowLeft className="h-4 w-4" /> Back to EcoCoin
        </Link>

        <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-emerald-100 p-3"><PieChart className="h-6 w-6 text-emerald-700" /></div>
            <div>
              <h1 className="text-2xl font-bold">{lang === "fa" ? "شفافیت خزانه" : "Treasury transparency"}</h1>
              <p className="text-sm text-stone-600">Hard cap 1B ECO · Community 55% · impact-only mint</p>
            </div>
          </div>
          <button type="button" onClick={load} className="inline-flex items-center gap-1.5 rounded-xl border border-stone-200 bg-white px-3 py-2 text-xs font-bold">
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} /> Refresh
          </button>
        </div>

        <div className="mb-6 rounded-2xl border border-emerald-200 bg-gradient-to-br from-emerald-50 to-white p-5 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <Shield className="h-8 w-8 text-emerald-700" />
              <div>
                <p className="text-xs font-bold uppercase text-emerald-800/70">{lang === "fa" ? "امتیاز اعتماد" : "Trust score"}</p>
                <p className="font-display text-3xl font-black text-emerald-800">{score}%</p>
              </div>
            </div>
            <p className="text-xs text-stone-600">mode: <span className="font-mono">{data?.mode ?? local.mode}</span></p>
          </div>
          <ul className="mt-4 space-y-2">
            {signals.map((sig) => {
              const label = lang === "fa" ? sig.label_fa : lang === "ar" ? sig.label_ar : sig.label_en;
              const detail = lang === "fa" ? sig.detail_fa : lang === "ar" ? sig.detail_ar : sig.detail_en;
              return (
                <li key={sig.id} className="flex items-start gap-2 rounded-xl bg-white/80 px-3 py-2 text-sm ring-1 ring-stone-100">
                  {sig.ok ? <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" /> : <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-red-500" />}
                  <div><p className="font-semibold">{label}</p><p className="text-xs text-stone-500">{detail}</p></div>
                </li>
              );
            })}
          </ul>
        </div>

        <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
          {[
            { icon: Coins, label: "Minted", value: local.totalMinted, color: "text-emerald-700" },
            { icon: Coins, label: "Circ.", value: local.circulating, color: "text-sky-700" },
            { icon: Flame, label: "Burned", value: local.burned, color: "text-orange-700" },
            { icon: Lock, label: "Staked", value: local.staked, color: "text-violet-700" },
          ].map((c) => (
            <div key={c.label} className="rounded-2xl border border-stone-200 bg-white p-4 shadow-sm">
              <div className="flex items-center gap-1.5 text-xs text-stone-500"><c.icon className={`h-3.5 w-3.5 ${c.color}`} />{c.label}</div>
              <p className={`mt-1 font-display text-xl font-black tabular-nums ${c.color}`}>{fmt(c.value)}</p>
            </div>
          ))}
        </div>

        <div className="mb-4 flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          <Shield className="mt-0.5 h-4 w-4 shrink-0" />
          <p>EcoCoin is an educational–scientific incentive token. It is <strong>not</strong> a carbon credit registry product.</p>
        </div>

        {loading && <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-emerald-600" /></div>}
        {error && !data && (
          <div className="mb-4 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
            <p className="font-medium">API unavailable — local trust monitor</p>
            <p className="mt-1 font-mono text-xs opacity-80">{error}</p>
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
                <p className="text-2xl font-bold text-emerald-700">{fmt((data as any).total_remaining)}</p>
              </div>
            </div>
            <ul className="space-y-3">
              {(data.buckets || []).map((b: any) => {
                const alloc = Number(b.allocation ?? b.total_allocated) || 1;
                const rem = Number(b.remaining) || 0;
                const pct = Math.min(100, Math.round((rem / alloc) * 100));
                return (
                  <li key={b.code} className="rounded-2xl border border-stone-200 bg-white p-4 shadow-sm">
                    <p className="font-semibold">{b.name || b.code} <span className="font-mono text-xs text-stone-500">{b.code}</span></p>
                    <div className="mb-1 mt-2 h-2 overflow-hidden rounded-full bg-stone-100">
                      <div className={`h-full ${BUCKET_COLORS[b.code] || "bg-emerald-500"}`} style={{ width: `${pct}%` }} />
                    </div>
                    <div className="flex justify-between text-xs text-stone-600">
                      <span>Remaining {fmt(b.remaining)}</span><span>of {fmt(b.allocation ?? b.total_allocated)}</span>
                    </div>
                  </li>
                );
              })}
            </ul>
          </>
        )}

        {!data && !loading && (
          <ul className="space-y-3">
            {[
              { code: "COMMUNITY", name: "Community", allocation: local.communityPool },
              { code: "TREASURY", name: "Treasury", allocation: local.treasuryPool },
              { code: "SCIENCE", name: "Science", allocation: local.sciencePool },
            ].map((b) => (
              <li key={b.code} className="rounded-2xl border border-stone-200 bg-white p-4 shadow-sm">
                <p className="font-semibold">{b.name} <span className="font-mono text-xs text-stone-500">{b.code}</span></p>
                <div className="mt-2 h-2 overflow-hidden rounded-full bg-stone-100">
                  <div className={`h-full ${BUCKET_COLORS[b.code]}`} style={{ width: `${Math.round((b.allocation / local.maxSupply) * 100)}%` }} />
                </div>
                <p className="mt-1 text-xs text-stone-600">{fmt(b.allocation)} / {fmt(local.maxSupply)}</p>
              </li>
            ))}
          </ul>
        )}

        <div className="mt-8 flex flex-wrap gap-3 text-sm">
          <Link to="/ecocoin/claims/new" className="rounded-lg bg-emerald-600 px-4 py-2 text-white hover:bg-emerald-700">Submit a claim</Link>
          <Link to="/ecocoin" className="rounded-lg border px-4 py-2 hover:bg-stone-100">Wallet hub</Link>
          <Link to="/payments" className="rounded-lg border px-4 py-2 hover:bg-stone-100">Payments</Link>
        </div>
      </div>
    </div>
  );
}
