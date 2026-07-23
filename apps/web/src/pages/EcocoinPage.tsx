// apps/web/src/pages/EcocoinPage.tsx
import { useMemo, useState } from "react";
import { Coins, TrendingUp, ArrowDownToLine, Lock, Receipt, LineChart as LineIcon, Trophy, ShoppingBag } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { AnimatedCounter } from "../components/eco/AnimatedCounter";
import { LineChart } from "../components/charts/LineChart";
import { WalletCard } from "../components/ecocoin/WalletCard";
import { TransactionItem } from "../components/ecocoin/TransactionItem";
import { ChallengeCard } from "../components/ecocoin/ChallengeCard";
import { RedeemCard } from "../components/ecocoin/RedeemCard";
import { ECO_STR, ecoText, type EcoLang } from "../components/ecocoin/ecocoinI18n";
import {
  WALLET, BALANCE_SERIES, INITIAL_TRANSACTIONS, INITIAL_CHALLENGES, REDEEM_ITEMS,
  type EcoTx, type Challenge, type TxType,
} from "../components/ecocoin/ecocoinData";

type Filter = "all" | TxType;
const FILTERS: Filter[] = ["all", "earn", "spend"];

export default function EcocoinPage() {
  const { lang } = useLang();
  const s = ECO_STR[lang as EcoLang];
  const locale = lang === "fa" ? "fa-IR" : lang === "ar" ? "ar-EG" : "en-US";

  const [balance, setBalance] = useState(WALLET.balance);
  const [txs, setTxs] = useState<EcoTx[]>(INITIAL_TRANSACTIONS);
  const [challenges, setChallenges] = useState<Challenge[]>(INITIAL_CHALLENGES);
  const [redeemed, setRedeemed] = useState<Record<string, boolean>>({});
  const [filter, setFilter] = useState<Filter>("all");

  const prependTx = (category: EcoTx["category"], type: TxType, amount: number, titleKey: string) =>
    setTxs((prev) => [{ id: `u${Date.now()}`, category, type, amount, titleKey, timestamp: new Date().toISOString() }, ...prev]);

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

  const visibleTx = useMemo(
    () => (filter === "all" ? txs : txs.filter((t) => t.type === filter)),
    [txs, filter]
  );

  const weekLabels =
    lang === "fa" ? ["ش", "ی", "د", "س", "چ", "پ", "ج"]
    : lang === "ar" ? ["ح", "ن", "ث", "ر", "خ", "ج", "س"]
    : ["Sat", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri"];

  const kpis = [
    { icon: TrendingUp, label: s.totalEarned, value: WALLET.totalEarned, color: "text-green-700", bg: "bg-green-50" },
    { icon: ArrowDownToLine, label: s.totalSpent, value: WALLET.totalSpent, color: "text-red-700", bg: "bg-red-50" },
    { icon: Lock, label: s.staked, value: WALLET.staked, color: "text-violet-700", bg: "bg-violet-50" },
    { icon: Receipt, label: s.txMonth, value: WALLET.txCountMonth, color: "text-blue-700", bg: "bg-blue-50" },
  ];

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
      {/* header */}
      <SectionReveal>
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-emerald-50 ring-1 ring-emerald-600/15">
            <Coins className="h-5 w-5 text-emerald-700" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
            <p className="mt-0.5 text-stone-600">{s.subtitle}</p>
          </div>
        </div>
      </SectionReveal>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* wallet card */}
        <SectionReveal delay={80}>
          <WalletCard address={WALLET.address} balance={balance} staked={WALLET.staked} apy={WALLET.apy} strings={s} lang={lang as EcoLang} />
        </SectionReveal>

        {/* balance trend */}
        <SectionReveal delay={140} className="lg:col-span-2">
          <div className="h-full rounded-2xl border border-stone-200/80 bg-white p-6 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
              <LineIcon className="h-4 w-4 text-emerald-700" />
              <h2 className="font-display text-lg text-stone-800">{s.balanceTrend}</h2>
            </div>
            <LineChart data={BALANCE_SERIES} labels={weekLabels} color="#059669"
              formatValue={(v) => v.toLocaleString(locale)} />
          </div>
        </SectionReveal>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {kpis.map((k, i) => (
          <SectionReveal key={k.label} delay={i * 70}>
            <div className={`rounded-2xl border border-stone-200/80 p-4 shadow-sm ${k.bg}`}>
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

      {/* challenges */}
      <SectionReveal delay={100}>
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

      {/* redeem shop */}
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
            <RedeemCard item={item} balance={balance} redeemed={!!redeemed[item.id]} strings={s} lang={lang as EcoLang} onRedeem={redeem} />
          </SectionReveal>
        ))}
      </div>

      {/* transactions */}
      <SectionReveal delay={100}>
        <div className="rounded-2xl border border-stone-200/80 bg-white p-6 shadow-sm">
          <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <Receipt className="h-4 w-4 text-stone-500" />
              <h2 className="font-display text-lg text-stone-800">{s.recentTx}</h2>
            </div>
            <div className="flex items-center gap-1 rounded-full border border-stone-200 bg-stone-50 p-1">
              {FILTERS.map((f) => (
                <button key={f} onClick={() => setFilter(f)}
                  className={`rounded-full px-3 py-1 text-xs font-bold transition-colors ${
                    filter === f ? "bg-white text-stone-800 shadow-sm" : "text-stone-500 hover:text-stone-700"
                  }`}>
                  {f === "all" ? s.filterAll : f === "earn" ? s.filterEarn : s.filterSpend}
                </button>
              ))}
            </div>
          </div>
          {visibleTx.length === 0 ? (
            <p className="py-10 text-center text-stone-500">{s.noTx}</p>
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