// apps/web/src/components/payments/PaymentMethods.tsx
// روش‌های پرداخت — آیکون‌ها همه CSS/emoji (بدون لوگوی خارجی؛ درس gamecoca).
// تعامل: set-default (فقط fiat) + افزودن کارت اعتباری.
import { useState } from "react";
import { CreditCard, Star, Plus, Check, X } from "lucide-react";
import { SectionReveal } from "../eco/SectionReveal";
import type { PaymentMethod, PaymentMethodKind } from "./paymentsData";
import { payText, localeOf, type PaymentStrings, type PayLang } from "./paymentsI18n";

const KIND_BADGE: Record<PaymentMethodKind, { node: React.ReactNode; ring: string }> = {
  credit_card: { node: <CreditCard className="h-5 w-5 text-blue-700" />, ring: "ring-blue-600/15 bg-blue-50" },
  ecocoin: { node: <span className="font-display text-sm font-black text-white">E</span>, ring: "ring-emerald-600/20 bg-gradient-to-br from-emerald-600 to-teal-500" },
  bitcoin: { node: <span className="font-display text-base font-black text-white">₿</span>, ring: "ring-orange-600/20 bg-gradient-to-br from-orange-500 to-amber-500" },
  bank_transfer: { node: <CreditCard className="h-5 w-5 text-violet-700" />, ring: "ring-violet-600/15 bg-violet-50" },
};

interface Props {
  methods: PaymentMethod[];
  strings: PaymentStrings;
  lang: PayLang;
  onSetDefault: (id: string) => void;
  onAddCard: (last4: string, holder: string) => void;
}

export function PaymentMethods({ methods, strings: s, lang, onSetDefault, onAddCard }: Props) {
  const locale = localeOf(lang);
  const [adding, setAdding] = useState(false);
  const [last4, setLast4] = useState("");
  const [holder, setHolder] = useState("");
  const [err, setErr] = useState("");

  const submit = () => {
    if (!/^\d{4}$/.test(last4)) { setErr(s.last4Invalid); return; }
    onAddCard(last4, holder.trim() || "—");
    setLast4(""); setHolder(""); setErr(""); setAdding(false);
  };

  const sub = (m: PaymentMethod): string => {
    if (m.kind === "credit_card") return `•••• ${m.last4}`;
    if (m.kind === "bitcoin") return `${(m.balanceBtc ?? 0).toLocaleString(locale, { maximumFractionDigits: 3 })} BTC`;
    return m.wallet ?? s.connected;
  };

  return (
    <SectionReveal delay={80}>
      <div className="rounded-2xl border border-stone-200/80 bg-white p-5 shadow-sm sm:p-6">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-display text-lg text-stone-800">{s.methodsTitle}</h2>
          {!adding && (
            <button onClick={() => setAdding(true)} className="inline-flex items-center gap-1.5 rounded-xl border border-stone-200 px-3 py-1.5 text-xs font-bold text-stone-700 transition-colors hover:bg-stone-50">
              <Plus className="h-3.5 w-3.5" />{s.addCard}
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          {methods.map((m) => {
            const b = KIND_BADGE[m.kind];
            const fiat = m.kind === "credit_card" || m.kind === "bank_transfer";
            return (
              <div key={m.id} className={`relative rounded-xl border p-4 text-center transition-all ${m.isDefault ? "border-green-300 bg-green-50/40" : "border-stone-200"}`}>
                {m.isDefault && (
                  <span className="absolute top-2 end-2 inline-flex items-center gap-1 rounded-full bg-green-100 px-2 py-0.5 text-[10px] font-bold text-green-700">
                    <Star className="h-3 w-3 fill-green-600 text-green-600" />{s.defaultBadge}
                  </span>
                )}
                <span className={`mx-auto mb-2 grid h-10 w-10 place-items-center rounded-full ring-1 ${b.ring}`}>{b.node}</span>
                <p className="font-semibold text-stone-800">{payText(s, `method_${m.kind}` as any)}</p>
                <p className="mt-0.5 text-xs text-stone-500">{sub(m)}</p>
                {fiat && !m.isDefault && (
                  <button onClick={() => onSetDefault(m.id)} className="mt-2 text-xs font-bold text-green-700 hover:underline">{s.setDefault}</button>
                )}
                {!fiat && <p className="mt-2 inline-flex items-center gap-1 text-xs font-bold text-emerald-700"><Check className="h-3 w-3" />{s.connected}</p>}
              </div>
            );
          })}
        </div>

        {adding && (
          <div className="mt-4 rounded-xl border border-stone-200 bg-stone-50 p-4" style={{ animation: "fade-up .25s var(--ease-out)" }}>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div>
                <label className="mb-1 block text-xs font-semibold text-stone-700">{s.cardLast4}</label>
                <input value={last4} onChange={(e) => setLast4(e.target.value.replace(/\D/g, "").slice(0, 4))} inputMode="numeric" maxLength={4}
                  className="w-full rounded-xl border border-stone-200 bg-white px-3 py-2 text-sm text-stone-800 outline-none focus:border-green-500 focus:ring-2 focus:ring-green-500/15" />
              </div>
              <div>
                <label className="mb-1 block text-xs font-semibold text-stone-700">{s.cardHolder}</label>
                <input value={holder} onChange={(e) => setHolder(e.target.value)}
                  className="w-full rounded-xl border border-stone-200 bg-white px-3 py-2 text-sm text-stone-800 outline-none focus:border-green-500 focus:ring-2 focus:ring-green-500/15" />
              </div>
            </div>
            {err && <p className="mt-2 text-xs font-bold text-red-700">{err}</p>}
            <div className="mt-3 flex items-center gap-2">
              <button onClick={submit} className="rounded-xl bg-green-600 px-4 py-2 text-sm font-bold text-white shadow-sm transition-colors hover:bg-green-700">{s.add}</button>
              <button onClick={() => { setAdding(false); setErr(""); }} className="inline-flex items-center gap-1 rounded-xl border border-stone-200 bg-white px-4 py-2 text-sm font-bold text-stone-700 hover:bg-stone-50"><X className="h-3.5 w-3.5" />{s.cancel}</button>
            </div>
          </div>
        )}
      </div>
    </SectionReveal>
  );
}