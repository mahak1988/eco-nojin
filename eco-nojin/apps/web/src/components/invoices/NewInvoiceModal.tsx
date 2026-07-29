// apps/web/src/components/invoices/NewInvoiceModal.tsx
import { useEffect, useState } from "react";
import { X } from "lucide-react";
import type { InvoiceStatus } from "./invoicesData";
import type { InvoiceStrings, InvLang } from "./invoicesI18n";

interface Props {
  open: boolean;
  strings: InvoiceStrings;
  lang: InvLang;
  onClose: () => void;
  onCreate: (data: { client: string; amount: number; status: InvoiceStatus }) => void;
}

export function NewInvoiceModal({ open, strings: s, onClose, onCreate }: Props) {
  const [show, setShow] = useState(false);
  const [client, setClient] = useState("");
  const [amount, setAmount] = useState("");
  const [status, setStatus] = useState<InvoiceStatus>("pending");
  const [errors, setErrors] = useState<{ client?: string; amount?: string }>({});

  // انیمیشن fade (بدون وابستگی به keyframe خاص)
  useEffect(() => {
    if (open) {
      const r = requestAnimationFrame(() => setShow(true));
      return () => cancelAnimationFrame(r);
    }
    setShow(false);
  }, [open]);

  // close on Escape
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  const submit = () => {
    const amt = Number(amount);
    const next: typeof errors = {};
    if (!client.trim()) next.client = s.fieldRequired;
    if (!amount || isNaN(amt) || amt <= 0) next.amount = s.amountInvalid;
    setErrors(next);
    if (Object.keys(next).length > 0) return;
    onCreate({ client: client.trim(), amount: amt, status });
    setClient(""); setAmount(""); setStatus("pending"); setErrors({});
    onClose();
  };

  const inputCls = (bad?: string) =>
    `w-full rounded-xl border px-3 py-2.5 text-sm text-stone-800 outline-none transition-colors focus:ring-2 ${
      bad ? "border-red-300 focus:border-red-500 focus:ring-red-500/15" : "border-stone-200 focus:border-green-500 focus:ring-green-500/15"
    }`;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* backdrop */}
      <div onClick={onClose} className="absolute inset-0 bg-stone-900/40 backdrop-blur-sm transition-opacity duration-200"
        style={{ opacity: show ? 1 : 0 }} />
      {/* dialog */}
      <div role="dialog" aria-modal="true" aria-label={s.modalTitle}
        className="relative w-full max-w-md rounded-2xl border border-stone-200 bg-white p-6 shadow-xl transition-all duration-200"
        style={{ opacity: show ? 1 : 0, transform: show ? "translateY(0)" : "translateY(12px)" }}>
        <div className="mb-5 flex items-center justify-between">
          <h2 className="font-display text-xl text-stone-800">{s.modalTitle}</h2>
          <button onClick={onClose} className="grid h-8 w-8 place-items-center rounded-lg text-stone-500 transition-colors hover:bg-stone-100">
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-semibold text-stone-700">{s.clientLabel}</label>
            <input autoFocus value={client} onChange={(e) => setClient(e.target.value)} placeholder={s.clientPlaceholder} className={inputCls(errors.client)} />
            {errors.client && <p className="mt-1 text-xs font-bold text-red-700">{errors.client}</p>}
          </div>
          <div>
            <label className="mb-1 block text-sm font-semibold text-stone-700">{s.amountLabel}</label>
            <input type="number" min="0" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="0" className={inputCls(errors.amount)} />
            {errors.amount && <p className="mt-1 text-xs font-bold text-red-700">{errors.amount}</p>}
          </div>
          <div>
            <label className="mb-1 block text-sm font-semibold text-stone-700">{s.statusLabel}</label>
            <select value={status} onChange={(e) => setStatus(e.target.value as InvoiceStatus)} className={inputCls()}>
              <option value="pending">{s.status_pending}</option>
              <option value="paid">{s.status_paid}</option>
            </select>
          </div>
        </div>

        <div className="mt-6 flex items-center gap-2">
          <button onClick={submit} className="flex-1 rounded-xl bg-green-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-green-700">
            {s.create}
          </button>
          <button onClick={onClose} className="rounded-xl border border-stone-200 px-4 py-2.5 text-sm font-bold text-stone-700 transition-colors hover:bg-stone-50">
            {s.cancel}
          </button>
        </div>
      </div>
    </div>
  );
}