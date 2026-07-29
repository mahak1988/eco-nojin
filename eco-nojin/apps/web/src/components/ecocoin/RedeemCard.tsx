// apps/web/src/components/ecocoin/RedeemCard.tsx
import { ShoppingBag, Check, Lock } from "lucide-react";
import type { RedeemItem } from "./ecocoinData";
import { ecoText, localeOf, type EcoStrings, type EcoLang } from "./ecocoinI18n";

interface Props {
  item: RedeemItem;
  balance: number;
  redeemed: boolean;
  strings: EcoStrings;
  lang: EcoLang;
  onRedeem: (id: string) => void;
}

export function RedeemCard({ item, balance, redeemed, redeemed: _r, strings: s, lang, onRedeem }: Props) {
  void _r;
  const locale = localeOf(lang);
  const affordable = balance >= item.cost && !redeemed;

  return (
    <article className="flex flex-col rounded-2xl border border-stone-200/80 bg-white p-5 shadow-sm transition-all hover:shadow-md">
      <div className="mb-3 grid h-14 w-14 place-items-center rounded-2xl bg-gradient-to-br from-emerald-50 to-teal-50 text-3xl ring-1 ring-emerald-600/10">
        {item.icon}
      </div>
      <h3 className="flex-1 font-bold text-stone-800">{ecoText(s, item.titleKey)}</h3>
      <p className="mt-1 font-display text-lg font-black tabular-nums text-emerald-700">
        {item.cost.toLocaleString(locale)} <span className="text-xs font-bold text-stone-500">{s.ecoUnit}</span>
      </p>

      <button
        onClick={() => affordable && onRedeem(item.id)}
        disabled={!affordable}
        className={`mt-4 inline-flex items-center justify-center gap-1.5 rounded-xl px-4 py-2 text-sm font-bold transition-all ${
          redeemed
            ? "cursor-default bg-green-50 text-green-700"
            : affordable
            ? "bg-emerald-600 text-white shadow-sm hover:-translate-y-0.5 hover:bg-emerald-700"
            : "cursor-not-allowed bg-stone-100 text-stone-400"
        }`}
      >
        {redeemed ? (
          <><Check className="h-4 w-4" />{s.redeemed}</>
        ) : affordable ? (
          <><ShoppingBag className="h-4 w-4" />{s.redeem}</>
        ) : (
          <><Lock className="h-4 w-4" />{s.notEnough}</>
        )}
      </button>
    </article>
  );
}