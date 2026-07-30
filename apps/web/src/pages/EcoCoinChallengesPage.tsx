import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, Trophy, Loader2, Gift, Link2 } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { ECO_STR, type EcoLang } from "../components/ecocoin/ecocoinI18n";
import {
  DEFAULT_ECO_ADDRESS,
  claimChallenge,
  claimRewards,
  fetchChallenges,
  fetchRewards,
  joinChallenge,
  type ApiChallenge,
} from "../lib/ecocoinApi";

type Row = ApiChallenge & { joined?: boolean; claimed?: boolean };

export default function EcoCoinChallengesPage() {
  const { lang } = useLang();
  const s = ECO_STR[lang as EcoLang];
  const locale = lang === "fa" ? "fa-IR" : lang === "ar" ? "ar-EG" : "en-US";
  const [items, setItems] = useState<Row[]>([]);
  const [pending, setPending] = useState(0);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [lastTx, setLastTx] = useState<string | null>(null);

  const reload = useCallback(async () => {
    setLoading(true);
    try {
      const [ch, rw] = await Promise.all([
        fetchChallenges("active"),
        fetchRewards(DEFAULT_ECO_ADDRESS),
      ]);
      // re-fetch with address enrichment
      const res = await fetch(
        `/api/v1/ecocoin/challenges?status=active&address=${DEFAULT_ECO_ADDRESS}`,
        { credentials: "include" },
      );
      const body = await res.json();
      setItems(body.challenges || ch.challenges || []);
      setPending(rw.pending_rewards || 0);
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "load failed");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void reload();
  }, [reload]);

  const onJoin = async (id: string) => {
    setBusyId(id);
    setMsg(null);
    try {
      await joinChallenge(id, DEFAULT_ECO_ADDRESS);
      await reload();
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "join failed");
    } finally {
      setBusyId(null);
    }
  };

  const onClaimChallenge = async (id: string, target: number) => {
    setBusyId(id);
    setMsg(null);
    try {
      // Demo: submit full target score so user can receive pool share
      const r = await claimChallenge(id, Math.max(target * 0.25, 1), DEFAULT_ECO_ADDRESS);
      setLastTx(r.chain?.tx_hash || null);
      setMsg(`+${r.reward_eco.toFixed(2)} ECO → pending`);
      await reload();
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "claim failed");
    } finally {
      setBusyId(null);
    }
  };

  const onClaimPending = async () => {
    setBusyId("rewards");
    setMsg(null);
    try {
      const r = await claimRewards(DEFAULT_ECO_ADDRESS);
      setLastTx(r.tx_hash);
      setMsg(`Claimed ${r.amount} ECO to wallet`);
      await reload();
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "reward claim failed");
    } finally {
      setBusyId(null);
    }
  };

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-5 sm:p-8">
      <Link to="/ecocoin" className="inline-flex items-center gap-1 text-sm font-bold text-emerald-700">
        <ArrowLeft className="h-4 w-4" /> EcoCoin
      </Link>

      <div className="flex flex-wrap items-center gap-3">
        <div className="grid h-12 w-12 place-items-center rounded-2xl bg-gradient-to-br from-amber-400 to-yellow-600 text-white shadow-lg">
          <Trophy className="h-6 w-6" />
        </div>
        <div className="flex-1">
          <h1 className="font-display text-3xl">{s.challenges}</h1>
          <p className="text-sm text-stone-500">{s.challengesSub}</p>
        </div>
        <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-2 text-center">
          <p className="text-[10px] font-bold uppercase text-amber-700">Pending</p>
          <p className="font-display text-xl font-black tabular-nums text-amber-900">
            {pending.toLocaleString(locale)}
          </p>
          <button
            type="button"
            disabled={pending <= 0 || busyId === "rewards"}
            onClick={() => void onClaimPending()}
            className="mt-1 inline-flex items-center gap-1 rounded-lg bg-amber-600 px-2 py-1 text-[11px] font-bold text-white disabled:opacity-40"
          >
            {busyId === "rewards" ? <Loader2 className="h-3 w-3 animate-spin" /> : <Gift className="h-3 w-3" />}
            {s.claim}
          </button>
        </div>
      </div>

      {msg && (
        <p className="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-900">{msg}</p>
      )}
      {lastTx && (
        <p className="flex items-center gap-1 font-mono text-[11px] text-stone-500">
          <Link2 className="h-3 w-3" /> {lastTx.slice(0, 18)}…
        </p>
      )}

      {loading ? (
        <Loader2 className="mx-auto h-8 w-8 animate-spin text-emerald-600" />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {items.map((c) => {
            const pct = Math.min(100, Math.round((c.total_score / Math.max(c.target, 1)) * 100));
            return (
              <article
                key={c.id}
                className="flex flex-col rounded-2xl border border-stone-200 bg-white p-5 shadow-sm"
              >
                <div className="mb-2 flex items-start justify-between gap-2">
                  <h3 className="font-bold text-stone-800">{c.title}</h3>
                  <span className="shrink-0 rounded-full bg-amber-50 px-2 py-0.5 text-xs font-bold text-amber-800">
                    pool {c.pool_eco.toLocaleString(locale)}
                  </span>
                </div>
                <p className="text-xs text-stone-500">
                  {c.metric} · target {c.target.toLocaleString(locale)} · {c.participants} joined
                </p>
                <div className="mt-3 h-2 overflow-hidden rounded-full bg-stone-100">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-green-500 to-emerald-400"
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  <button
                    type="button"
                    disabled={!!c.joined || busyId === c.id}
                    onClick={() => void onJoin(c.id)}
                    className="rounded-xl border px-3 py-2 text-xs font-bold disabled:opacity-40"
                  >
                    {c.joined ? "Joined" : "Join"}
                  </button>
                  <button
                    type="button"
                    disabled={!!c.claimed || busyId === c.id}
                    onClick={() => void onClaimChallenge(c.id, c.target)}
                    className="inline-flex items-center gap-1 rounded-xl bg-emerald-600 px-3 py-2 text-xs font-bold text-white disabled:opacity-40"
                  >
                    {busyId === c.id && <Loader2 className="h-3 w-3 animate-spin" />}
                    {c.claimed ? s.claimed : s.claim}
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}
