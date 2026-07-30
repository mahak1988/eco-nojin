// apps/web/src/pages/EcocoinPage.tsx — hub with active actions + subpage links
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  Coins,
  TrendingUp,
  ArrowDownToLine,
  Lock,
  Receipt,
  Trophy,
  ShoppingBag,
  Sparkles,
  Pickaxe,
  Leaf,
  Scale,
} from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { AnimatedCounter } from "../components/eco/AnimatedCounter";
import { WalletCard } from "../components/ecocoin/WalletCard";
import { TransactionItem } from "../components/ecocoin/TransactionItem";
import { ChallengeCard } from "../components/ecocoin/ChallengeCard";
import { RedeemCard } from "../components/ecocoin/RedeemCard";
import { MiningPanel } from "../components/ecocoin/MiningPanel";
import { EconomicsPanel } from "../components/ecocoin/EconomicsPanel";
import { StakingTiersPanel } from "../components/ecocoin/StakingTiersPanel";
import { ProtocolStatsBar } from "../components/ecocoin/ProtocolStatsBar";
import { InteractiveBalanceChart } from "../components/ecocoin/InteractiveBalanceChart";
import { WalletActionsModal, type WalletAction } from "../components/ecocoin/WalletActionsModal";
import { ECO_STR, type EcoLang } from "../components/ecocoin/ecocoinI18n";
import {
  WALLET,
  INITIAL_TRANSACTIONS,
  INITIAL_CHALLENGES,
  REDEEM_ITEMS,
  type EcoTx,
  type Challenge,
  type TxType,
} from "../components/ecocoin/ecocoinData";

type Filter = "all" | TxType;
const FILTERS: Filter[] = ["all", "earn", "spend"];

export default function EcocoinPage() {
  const { lang } = useLang();
  const s = ECO_STR[lang as EcoLang];
  const locale = lang === "fa" ? "fa-IR" : lang === "ar" ? "ar-EG" : "en-US";

  const [balance, setBalance] = useState(WALLET.balance);
  const [staked, setStaked] = useState(WALLET.staked);
  const [txs, setTxs] = useState<EcoTx[]>(INITIAL_TRANSACTIONS);
  const [challenges, setChallenges] = useState<Challenge[]>(INITIAL_CHALLENGES);
  const [redeemed, setRedeemed] = useState<Record<string, boolean>>({});
  const [filter, setFilter] = useState<Filter>("all");
  const [modal, setModal] = useState<WalletAction | null>(null);

  const prependTx = (category: EcoTx["category"], type: TxType, amount: number, titleKey: string) =>
    setTxs((prev) => [
      { id: `u${Date.now()}`, category, type, amount, titleKey, timestamp: new Date().toISOString() },
      ...prev,
    ]);

  const claim = (id: string) => {
    const c = challenges.find((x) => x.id === id);
    if (!c || c.claimed || c.progress < c.goal) return;
    setChallenges((prev) => prev.map((x) => (x.id === id ? { ...x, claimed: true } : x)));
    setBalance((b) => b + c.reward);
    prependTx("challenge", "earn", c.reward, "txClaim");
  };

  const redeem = (id: string) => {
    const item = REDEEM_ITEMS.find((x) => x.id === id);
    if (!item || redeemed[id] || balance < item.cost) return;
    setRedeemed((prev) => ({ ...prev, [id]: true }));
    setBalance((b) => b - item.cost);
    prependTx("redeem", "spend", -item.cost, "txRedeem");
  };

  const onSend = async (to: string, amount: number) => {
    try {
      await fetch("/api/v1/ecocoin/transfer", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          from_address: WALLET.address,
          to_address: to,
          amount,
        }),
      });
    } catch {
      /* local fallback */
    }
    setBalance((b) => b - amount);
    prependTx("transfer", "spend", -amount, "tx6");
  };

  const onStake = async (amount: number, tierId: number) => {
    try {
      await fetch("/api/v1/ecocoin/staking/stake", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ address: WALLET.address, amount, tier_id: tierId }),
      });
    } catch {
      /* local */
    }
    setBalance((b) => b - amount);
    setStaked((x) => x + amount);
    prependTx("stake", "spend", -amount, "tx4");
  };

  const visibleTx = useMemo(
    () => (filter === "all" ? txs : txs.filter((t) => t.type === filter)),
    [txs, filter],
  );

  const kpis = [
    { icon: TrendingUp, label: s.totalEarned, value: WALLET.totalEarned, color: "text-green-700", bg: "bg-green-50" },
    { icon: ArrowDownToLine, label: s.totalSpent, value: WALLET.totalSpent, color: "text-red-700", bg: "bg-red-50" },
    { icon: Lock, label: s.staked, value: staked, color: "text-violet-700", bg: "bg-violet-50" },
    { icon: Receipt, label: s.txMonth, value: WALLET.txCountMonth, color: "text-blue-700", bg: "bg-blue-50" },
  ];

  const subLinks = [
    { to: "/ecocoin/staking", icon: Lock, label: s.stakeTitle },
    { to: "/ecocoin/mining", icon: Pickaxe, label: s.miningTitle },
    { to: "/ecocoin/bioeconomy", icon: Leaf, label: s.econTitle },
    { to: "/ecocoin/challenges", icon: Trophy, label: s.challenges },
  ];

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
      {modal && (
        <WalletActionsModal
          action={modal}
          onClose={() => setModal(null)}
          balance={balance}
          address={WALLET.address}
          onSend={onSend}
          onStake={onStake}
          labels={{
            send: s.send,
            receive: s.receive,
            stake: s.stake,
            to: "To",
            amount: s.ecoUnit,
            tier: "Tier",
            submit: s.stake,
            cancel: lang === "fa" ? "انصراف" : lang === "ar" ? "إلغاء" : "Cancel",
            yourAddress: s.copyAddress,
            copied: s.copied,
          }}
        />
      )}

      <SectionReveal>
        <div className="relative overflow-hidden rounded-3xl border border-emerald-200/60 bg-gradient-to-br from-emerald-600 via-teal-600 to-cyan-700 p-6 text-white shadow-xl shadow-emerald-600/20">
          <div className="pointer-events-none absolute -end-8 -top-8 h-40 w-40 rounded-full bg-white/10 blur-2xl" />
          <div className="relative flex flex-wrap items-center gap-4">
            <div className="grid h-14 w-14 place-items-center rounded-2xl bg-white/15 ring-1 ring-white/30 backdrop-blur">
              <Coins className="h-7 w-7" />
            </div>
            <div>
              <h1 className="font-display text-3xl drop-soft">{s.title}</h1>
              <p className="mt-1 text-sm text-emerald-50/90">{s.subtitle}</p>
            </div>
            <div className="ms-auto rounded-2xl bg-white/15 px-4 py-2 text-center backdrop-blur">
              <p className="text-[10px] font-bold uppercase tracking-wide text-emerald-100">{s.balance}</p>
              <p className="font-display text-2xl font-black tabular-nums">
                <AnimatedCounter end={balance} />
              </p>
            </div>
          </div>
        </div>
      </SectionReveal>

      <div className="flex flex-wrap gap-2">
        {subLinks.map((l) => (
          <Link
            key={l.to}
            to={l.to}
            className="inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-bold text-emerald-800 hover:bg-emerald-100"
          >
            <l.icon className="h-3.5 w-3.5" />
            {l.label}
          </Link>
        ))}
      </div>

      <SectionReveal delay={60}>
        <ProtocolStatsBar strings={s} />
      </SectionReveal>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <SectionReveal delay={80}>
          <WalletCard
            address={WALLET.address}
            balance={balance}
            staked={staked}
            apy={WALLET.apy}
            strings={s}
            lang={lang as EcoLang}
            onAction={setModal}
          />
        </SectionReveal>
        <SectionReveal delay={140} className="lg:col-span-2">
          <InteractiveBalanceChart
            locale={locale}
            title={s.balanceTrend}
            period7="7D"
            period30="30D"
            period90="90D"
          />
        </SectionReveal>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {kpis.map((k, i) => (
          <SectionReveal key={k.label} delay={i * 70}>
            <div className={`card-hover rounded-2xl border border-stone-200/80 p-4 shadow-sm ${k.bg}`}>
              <div className="flex items-center gap-2">
                <k.icon className={`h-4 w-4 ${k.color}`} />
                <p className="text-sm font-medium text-stone-600">{k.label}</p>
              </div>
              <p className={`mt-1 font-display text-2xl font-black tabular-nums ${k.color}`}>
                <AnimatedCounter end={k.value} />
              </p>
            </div>
          </SectionReveal>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <SectionReveal delay={100}>
          <MiningPanel strings={s} />
        </SectionReveal>
        <SectionReveal delay={140}>
          <EconomicsPanel strings={s} />
        </SectionReveal>
      </div>

      <SectionReveal delay={100}>
        <StakingTiersPanel strings={s} />
      </SectionReveal>

      <SectionReveal delay={80}>
        <div className="mb-3 flex items-center gap-2">
          <Trophy className="h-5 w-5 text-amber-600" />
          <div>
            <h2 className="font-display text-xl text-stone-800">{s.challenges}</h2>
            <p className="text-sm text-stone-600">{s.challengesSub}</p>
          </div>
        </div>
      </SectionReveal>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {challenges.map((c, i) => (
          <SectionReveal key={c.id} delay={i * 70}>
            <ChallengeCard challenge={c} strings={s} lang={lang as EcoLang} onClaim={claim} />
          </SectionReveal>
        ))}
      </div>

      <SectionReveal delay={100}>
        <div className="mb-3 flex items-center gap-2">
          <ShoppingBag className="h-5 w-5 text-rose-600" />
          <div>
            <h2 className="font-display text-xl text-stone-800">{s.redeemShop}</h2>
            <p className="text-sm text-stone-600">{s.redeemShopSub}</p>
          </div>
        </div>
      </SectionReveal>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {REDEEM_ITEMS.map((item, i) => (
          <SectionReveal key={item.id} delay={i * 70}>
            <RedeemCard
              item={item}
              balance={balance}
              redeemed={!!redeemed[item.id]}
              strings={s}
              lang={lang as EcoLang}
              onRedeem={redeem}
            />
          </SectionReveal>
        ))}
      </div>

      <SectionReveal delay={100}>
        <div className="rounded-2xl border border-stone-200/80 bg-white p-6 shadow-sm">
          <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <Receipt className="h-4 w-4 text-stone-500" />
              <h2 className="font-display text-lg text-stone-800">{s.recentTx}</h2>
            </div>
            <div className="flex items-center gap-1 rounded-full border border-stone-200 bg-stone-50 p-1">
              {FILTERS.map((f) => (
                <button
                  key={f}
                  type="button"
                  onClick={() => setFilter(f)}
                  className={`rounded-full px-3 py-1 text-xs font-bold transition-colors ${
                    filter === f ? "bg-white text-stone-800 shadow-sm" : "text-stone-500 hover:text-stone-700"
                  }`}
                >
                  {f === "all" ? s.filterAll : f === "earn" ? s.filterEarn : s.filterSpend}
                </button>
              ))}
            </div>
          </div>
          {visibleTx.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-stone-300 py-12 text-center text-stone-500">
              {s.noTx}
            </div>
          ) : (
            <ul className="divide-y divide-stone-100">
              {visibleTx.map((t) => (
                <TransactionItem key={t.id} tx={t} strings={s} lang={lang as EcoLang} />
              ))}
            </ul>
          )}
        </div>
      </SectionReveal>
    </div>
  );
}
