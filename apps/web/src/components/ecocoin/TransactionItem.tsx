// apps/web/src/components/ecocoin/TransactionItem.tsx
import { GraduationCap, Trophy, ShoppingBag, Lock, Gift, ArrowLeftRight, ArrowUpRight, ArrowDownRight } from "lucide-react";
import type { EcoTx, TxCategory } from "./ecocoinData";
import { ecoText, catText, timeAgo, type EcoStrings, type EcoLang } from "./ecocoinI18n";

const CAT_STYLE: Record<TxCategory, { icon: typeof Gift; bg: string; text: string }> = {
  course: { icon: GraduationCap, bg: "bg-blue-50", text: "text-blue-700" },
  challenge: { icon: Trophy, bg: "bg-amber-50", text: "text-amber-700" },
  redeem: { icon: ShoppingBag, bg: "bg-rose-50", text: "text-rose-700" },
  stake: { icon: Lock, bg: "bg-violet-50", text: "text-violet-700" },
  reward: { icon: Gift, bg: "bg-green-50", text: "text-green-700" },
  transfer: { icon: ArrowLeftRight, bg: "bg-stone-100", text: "text-stone-600" },
};

interface Props {
  tx: EcoTx;
  strings: EcoStrings;
  lang: EcoLang;
}

export function TransactionItem({ tx, strings: s, lang }: Props) {
  const cfg = CAT_STYLE[tx.category];
  const Icon = cfg.icon;
  const earn = tx.type === "earn";
  const locale = lang === "fa" ? "fa-IR" : lang === "ar" ? "ar-EG" : "en-US";

  return (
    <li className="flex items-center gap-3 px-2 py-3 transition-colors hover:bg-stone-50">
      <span className={`grid h-10 w-10 shrink-0 place-items-center rounded-full ${cfg.bg} ${cfg.text}`}>
        <Icon className="h-4 w-4" />
      </span>
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-semibold text-stone-800">{ecoText(s, tx.titleKey)}</p>
        <div className="mt-0.5 flex items-center gap-2 text-xs text-stone-500">
          <span className={`rounded px-1.5 py-0.5 font-bold ${cfg.bg} ${cfg.text}`}>{catText(s, tx.category)}</span>
          <span>{timeAgo(tx.timestamp, lang)}</span>
        </div>
      </div>
      <span className={`inline-flex shrink-0 items-center gap-0.5 font-display text-base font-black tabular-nums ${earn ? "text-green-700" : "text-red-700"}`}>
        {earn ? <ArrowUpRight className="h-4 w-4" /> : <ArrowDownRight className="h-4 w-4" />}
        {earn ? "+" : "−"}{Math.abs(tx.amount).toLocaleString(locale)}
      </span>
    </li>
  );
}