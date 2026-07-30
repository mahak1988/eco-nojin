import { FormEvent, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Lock, Loader2, Calculator, ArrowLeft } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { ECO_STR, type EcoLang } from "../components/ecocoin/ecocoinI18n";

type Tier = { id: number; duration: string; apy: number; multiplier: number; min_amount: number };

/** Smart stake estimator: reward ≈ amount * (apy/100) * (days/365) * multiplier */
function estimateReward(amount: number, apy: number, days: number, multiplier: number) {
  const base = amount * (apy / 100) * (days / 365);
  return base * multiplier;
}

function parseDays(duration: string): number {
  const m = duration.match(/(\d+)/);
  if (!m) return 30;
  const n = Number(m[1]);
  if (/year|yr|سال/i.test(duration)) return n * 365;
  if (/month|mo|ماه/i.test(duration)) return n * 30;
  return n;
}

export default function EcoCoinStakingPage() {
  const { lang } = useLang();
  const s = ECO_STR[lang as EcoLang];
  const [tiers, setTiers] = useState<Tier[]>([]);
  const [loading, setLoading] = useState(true);
  const [amount, setAmount] = useState("100");
  const [tierId, setTierId] = useState(1);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    void fetch("/api/v1/ecocoin/staking/tiers", { credentials: "include" })
      .then((r) => r.json())
      .then((j) => {
        const list = Array.isArray(j) ? j : [];
        setTiers(list);
        if (list[0]) setTierId(list[0].id);
      })
      .catch(() =>
        setTiers([
          { id: 1, duration: "30 days", apy: 8, multiplier: 1, min_amount: 50 },
          { id: 2, duration: "90 days", apy: 12, multiplier: 1.2, min_amount: 100 },
          { id: 3, duration: "365 days", apy: 18, multiplier: 1.5, min_amount: 250 },
        ]),
      )
      .finally(() => setLoading(false));
  }, []);

  const tier = tiers.find((t) => t.id === tierId) || tiers[0];
  const amt = Number(amount) || 0;
  const preview = useMemo(() => {
    if (!tier || amt <= 0) return null;
    const days = parseDays(tier.duration);
    const reward = estimateReward(amt, tier.apy, days, tier.multiplier);
    return { days, reward, total: amt + reward };
  }, [tier, amt]);

  async function onStake(e: FormEvent) {
    e.preventDefault();
    if (!tier || amt < tier.min_amount) return;
    setBusy(true);
    setResult(null);
    try {
      const res = await fetch("/api/v1/ecocoin/staking/stake", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          address: "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18",
          amount: amt,
          tier_id: tier.id,
        }),
      });
      const j = await res.json();
      setResult(j);
    } catch (err) {
      setResult({ error: String(err), local_estimate: preview });
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-5 sm:p-8">
      <Link to="/ecocoin" className="inline-flex items-center gap-1 text-sm font-bold text-emerald-700">
        <ArrowLeft className="h-4 w-4" /> EcoCoin
      </Link>
      <div className="flex items-center gap-3">
        <div className="grid h-12 w-12 place-items-center rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-700 text-white shadow-lg">
          <Lock className="h-6 w-6" />
        </div>
        <div>
          <h1 className="font-display text-3xl text-stone-800">{s.stakeTitle}</h1>
          <p className="text-sm text-stone-500">{s.stakeSub}</p>
        </div>
      </div>

      {loading ? (
        <Loader2 className="mx-auto h-8 w-8 animate-spin text-emerald-600" />
      ) : (
        <>
          <div className="grid gap-3 sm:grid-cols-3">
            {tiers.map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => setTierId(t.id)}
                className={`rounded-2xl border p-4 text-start transition ${
                  tierId === t.id
                    ? "border-emerald-400 bg-emerald-50 ring-2 ring-emerald-500/30"
                    : "border-stone-200 bg-white hover:border-emerald-200"
                }`}
              >
                <p className="text-xs font-bold text-emerald-700">Tier {t.id}</p>
                <p className="font-display text-lg font-black">{t.duration}</p>
                <p className="text-emerald-700 font-black">{t.apy}% APY</p>
                <p className="text-[11px] text-stone-500">×{t.multiplier} · min {t.min_amount}</p>
              </button>
            ))}
          </div>

          <form onSubmit={(e) => void onStake(e)} className="space-y-4 rounded-3xl border bg-white p-5 shadow-sm">
            <label className="block text-sm">
              <span className="font-medium text-stone-600">{s.ecoUnit}</span>
              <input
                type="number"
                min={tier?.min_amount || 0}
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="mt-1 w-full rounded-xl border px-3 py-2.5 text-sm font-bold"
              />
            </label>

            {preview && (
              <div className="flex items-start gap-2 rounded-2xl bg-emerald-50 p-4 text-sm text-emerald-900">
                <Calculator className="mt-0.5 h-4 w-4 shrink-0" />
                <div>
                  <p>
                    ~{preview.days}d · reward{" "}
                    <strong>{preview.reward.toFixed(2)}</strong> ECO · total{" "}
                    <strong>{preview.total.toFixed(2)}</strong>
                  </p>
                  <p className="mt-1 text-xs opacity-80">
                    R = A × (APY/100) × (d/365) × multiplier
                  </p>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={busy || !tier || amt < (tier?.min_amount || 0)}
              className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-600 py-3 text-sm font-bold text-white disabled:opacity-50"
            >
              {busy && <Loader2 className="h-4 w-4 animate-spin" />}
              {s.stake}
            </button>
            {result && (
              <pre className="max-h-40 overflow-auto rounded-xl bg-stone-50 p-3 text-[11px] text-stone-600">
                {JSON.stringify(result, null, 2)}
              </pre>
            )}
          </form>
        </>
      )}
    </div>
  );
}
