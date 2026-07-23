// apps/web/src/components/ecocoin/WalletCard.tsx
// کارت کیف‌پول گرادیانی (تیره، مستقل — متن روشن با کنتراست OK).
import { useState } from "react";
import { Wallet, Send, ArrowDownToLine, Lock, Copy, Check } from "lucide-react";
import { AnimatedCounter } from "../eco/AnimatedCounter";
import { ecoText, shortAddr, type EcoStrings, type EcoLang } from "./ecocoinI18n";

interface Props {
  address: string;
  balance: number;
  staked: number;
  apy: number;
  strings: EcoStrings;
  lang: EcoLang;
}

export function WalletCard({ address, balance, staked, apy, strings: s, lang }: Props) {
  const [copied, setCopied] = useState(false);
  const locale = lang === "fa" ? "fa-IR" : lang === "ar" ? "ar-EG" : "en-US";

  const copy = async () => {
    try { await navigator.clipboard.writeText(address); } catch { /* ممکن است در دسترس نباشد */ }
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };

  return (
    <div className="relative overflow-hidden rounded-3xl p-6 text-white shadow-xl sm:p-7"
      style={{ background: "linear-gradient(135deg, #064e3b 0%, #065f46 40%, #0f766e 100%)" }}>
      {/* حلقه‌های تزئینی */}
      <div className="pointer-events-none absolute -top-16 -end-16 h-48 w-48 rounded-full bg-emerald-300/20 blur-2xl" />
      <div className="pointer-events-none absolute -bottom-20 -start-10 h-48 w-48 rounded-full bg-teal-200/10 blur-2xl" />

      <div className="relative flex items-start justify-between">
        <div className="flex items-center gap-2 text-emerald-100/90">
          <Wallet className="h-5 w-5" />
          <span className="text-sm font-bold">{s.walletTitle}</span>
        </div>
        <button onClick={copy} title={s.copyAddress}
          className="inline-flex items-center gap-1.5 rounded-full bg-white/10 px-3 py-1 text-xs font-bold backdrop-blur transition-colors hover:bg-white/20">
          {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
          <span dir="ltr" className="font-mono">{shortAddr(address)}</span>
        </button>
      </div>

      <div className="relative mt-6">
        <p className="text-sm text-emerald-100/80">{s.balance}</p>
        <p className="mt-1 font-display text-4xl font-black tabular-nums sm:text-5xl">
          <AnimatedCounter end={balance} />
          <span className="ms-2 text-base font-bold text-emerald-200/80">{s.ecoUnit}</span>
        </p>
      </div>

      {/* staking mini-stat */}
      <div className="relative mt-5 flex items-center gap-4 rounded-2xl bg-white/10 p-3 backdrop-blur">
        <Lock className="h-5 w-5 text-emerald-200" />
        <div className="flex-1">
          <p className="text-xs text-emerald-100/80">{s.staked}</p>
          <p className="font-bold tabular-nums">{staked.toLocaleString(locale)} <span className="text-emerald-200/80">{s.ecoUnit}</span></p>
        </div>
        <div className="text-end">
          <p className="text-xs text-emerald-100/80">{s.apyLabel}</p>
          <p className="font-bold text-emerald-200">+{apy.toLocaleString(locale)}٪</p>
        </div>
      </div>

      {/* actions */}
      <div className="relative mt-5 grid grid-cols-3 gap-2">
        <button className="flex flex-col items-center gap-1 rounded-xl bg-white/10 py-2.5 text-xs font-bold backdrop-blur transition-colors hover:bg-white/20">
          <Send className="h-4 w-4" />{s.send}
        </button>
        <button className="flex flex-col items-center gap-1 rounded-xl bg-white/10 py-2.5 text-xs font-bold backdrop-blur transition-colors hover:bg-white/20">
          <ArrowDownToLine className="h-4 w-4" />{s.receive}
        </button>
        <button className="flex flex-col items-center gap-1 rounded-xl bg-emerald-400 py-2.5 text-xs font-bold text-emerald-950 transition-colors hover:bg-emerald-300">
          <Lock className="h-4 w-4" />{s.stake}
        </button>
      </div>
    </div>
  );
}