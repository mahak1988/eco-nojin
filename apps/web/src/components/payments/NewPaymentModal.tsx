// apps/web/src/components/payments/NewPaymentModal.tsx
// فرم پرداخت جدید — روش، مبلغ، مرجع، پیش‌نمایش؛ انتخاب کارت پیش‌فرض برای fiat.
import { useEffect, useState } from "react";
import { X } from "lucide-react";
import type { PaymentMethod, PaymentMethodKind } from "./paymentsData";
import { METHOD_FILTERS } from "./paymentsData";
import { methodText, formatAmount, type PaymentStrings, type PayLang } from "./paymentsI18n";
import { readCurrencySettings, formatMoney } from "../../lib/currencyStore";

export interface NewPaymentData { method: PaymentMethodKind; amount: number; reference: string; }

interface Props {
  open: boolean;
  strings: PaymentStrings;
  lang: PayLang;
  onClose: () => void;
  onCreate: (d: NewPaymentData) => void;
  methods?: PaymentMethod[];
}

export function NewPaymentModal({ open, strings: s, lang, onClose, onCreate, methods = [] }: Props) {
  const [show, setShow] = useState(false);
  const [method, setMethod] = useState<PaymentMethodKind>("credit_card");
  const [amount, setAmount] = useState("");
  const [reference, setReference] = useState("");
  const [err, setErr] = useState("");

  useEffect(() => {
    if (open) {
      const r = requestAnimationFrame(() => setShow(true));
      return () => cancelAnimationFrame(r);
    }
    setShow(false);
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  useEffect(() => {
    if (!open) {
      setMethod("credit_card");
      setAmount("");
      setReference("");
      setErr("");
    }
  }, [open]);

  if (!open) return null;

  const num = Number(amount);
  const valid = amount !== "" && !isNaN(num) && num > 0;
  const defaultCard = methods.find((m) => m.isDefault && m.kind === "credit_card");
  const cs = readCurrencySettings();
  const locale = lang === "fa" ? "fa-IR" : lang === "ar" ? "ar-EG" : "en-US";

  const previewLabel = () => {
    if (!valid) return null;
    if (method === "credit_card" || method === "bank_transfer") {
      return formatMoney(num, cs.primary, cs, locale);
    }
    return formatAmount(method, num, lang);
  };

  const submit = () => {
    if (!valid) { setErr(s.amountLabel); return; }
    onCreate({
      method,
      amount: num,
      reference: reference.trim() || `PAY-${Date.now().toString().slice(-6)}`,
    });
    onClose();
  };

  const inputCls = "w-full rounded-xl border border-stone-200 px-3 py-2.5 text-sm text-stone-800 outline-none transition-colors focus:border-green-500 focus:ring-2 focus:ring-green-500/15";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div onClick={onClose} className="absolute inset-0 bg-stone-900/40 backdrop-blur-sm transition-opacity duration-200" style={{ opacity: show ? 1 : 0 }} aria-hidden />
      <div
        role="dialog"
        aria-modal="true"
        aria-label={s.modalTitle}
        className="relative w-full max-w-md rounded-2xl border border-stone-200 bg-white p-6 shadow-xl transition-all duration-200"
        style={{ opacity: show ? 1 : 0, transform: show ? "translateY(0)" : "translateY(12px)" }}
      >
        <div className="mb-5 flex items-center justify-between">
          <h2 className="font-display text-xl text-stone-800">{s.modalTitle}</h2>
          <button type="button" onClick={onClose} className="grid h-8 w-8 place-items-center rounded-lg text-stone-500 hover:bg-stone-100" aria-label={s.cancel}>
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-semibold text-stone-700">{s.methodLabel}</label>
            <select value={method} onChange={(e) => setMethod(e.target.value as PaymentMethodKind)} className={inputCls}>
              {METHOD_FILTERS.filter((m) => m !== "all").map((m) => (
                <option key={m} value={m}>{methodText(s, m)}</option>
              ))}
            </select>
            {method === "credit_card" && defaultCard && (
              <p className="mt-1 text-xs text-stone-500">•••• {defaultCard.last4}{defaultCard.holder ? ` · ${defaultCard.holder}` : ""}</p>
            )}
          </div>
          <div>
            <label className="mb-1 block text-sm font-semibold text-stone-700">{s.amountLabel}</label>
            <input
              autoFocus
              type="number"
              min="0"
              step="any"
              value={amount}
              onChange={(e) => { setAmount(e.target.value); setErr(""); }}
              onKeyDown={(e) => { if (e.key === "Enter" && valid) submit(); }}
              className={inputCls}
              placeholder="0"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-semibold text-stone-700">{s.refLabel}</label>
            <input
              value={reference}
              onChange={(e) => setReference(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter" && valid) submit(); }}
              className={inputCls}
              placeholder="PAY-…"
            />
          </div>

          {valid && (
            <div className="flex items-center justify-between rounded-xl bg-stone-50 px-3 py-2.5">
              <span className="text-xs font-bold text-stone-500">{s.preview}</span>
              <span className="font-display text-base font-black tabular-nums text-stone-800">{previewLabel()}</span>
            </div>
          )}
          {err && <p className="rounded-xl bg-red-50 px-3 py-2 text-sm font-bold text-red-700">{err}</p>}
        </div>

        <div className="mt-6 flex items-center gap-2">
          <button
            type="button"
            onClick={submit}
            disabled={!valid}
            className="flex-1 rounded-xl bg-green-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-green-700 disabled:cursor-not-allowed disabled:bg-stone-300"
          >
            {s.create}
          </button>
          <button type="button" onClick={onClose} className="rounded-xl border border-stone-200 px-4 py-2.5 text-sm font-bold text-stone-700 hover:bg-stone-50">
            {s.cancel}
          </button>
        </div>
      </div>
    </div>
  );
}
