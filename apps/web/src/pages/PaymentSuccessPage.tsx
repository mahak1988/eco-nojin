import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { CheckCircle2, Loader2 } from "lucide-react";
import { getIntent, fetchGatewayStatus, type CheckoutResult, type GatewayStatus } from "../lib/paymentGateway";
import { updatePaymentStatus, readPayments, writePayments } from "../lib/paymentsStore";
import { setInvoiceStatus, readInvoices } from "../lib/invoiceStore";

export default function PaymentSuccessPage() {
  const [params] = useSearchParams();
  const intentId = params.get("intent") || "";
  const demo = params.get("demo") === "1";
  const [intent, setIntent] = useState<(CheckoutResult & { ref_id?: string }) | null>(null);
  const [gw, setGw] = useState<GatewayStatus | null>(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    void fetchGatewayStatus().then(setGw).catch(() => null);
    if (!intentId) return;
    void getIntent(intentId)
      .then((i) => {
        setIntent(i);
        try {
          const pays = readPayments();
          const match = pays.find((p) => p.reference === intentId || p.id === intentId);
          if (match) writePayments(updatePaymentStatus(match.id, "completed", pays));
          if (i.invoice_id) {
            const invs = readInvoices();
            writePayments; // keep store pattern
            setInvoiceStatus(i.invoice_id, "paid", invs);
          }
        } catch { /* offline */ }
      })
      .catch((e) => setErr(String(e)));
  }, [intentId]);

  return (
    <div className="mx-auto max-w-lg space-y-6 p-8 text-center">
      <CheckCircle2 className="mx-auto h-14 w-14 text-emerald-600" />
      <h1 className="font-display text-2xl text-stone-800">Payment success</h1>
      {demo && (
        <p className="rounded-xl bg-amber-50 px-3 py-2 text-sm text-amber-900 ring-1 ring-amber-200">
          Demo mode. Set STRIPE_SECRET_KEY or ZARINPAL_MERCHANT_ID for live.
        </p>
      )}
      {!intent && !err && <Loader2 className="mx-auto h-6 w-6 animate-spin text-emerald-600" />}
      {err && <p className="text-sm text-red-600">{err}</p>}
      {intent && (
        <div className="rounded-2xl border border-stone-200 bg-white p-4 text-start text-sm">
          <p><span className="text-stone-500">Intent:</span> <span className="font-mono">{intent.intent_id}</span></p>
          <p><span className="text-stone-500">Provider:</span> {intent.provider}</p>
          <p><span className="text-stone-500">Status:</span> {intent.status}</p>
          {intent.ref_id && <p><span className="text-stone-500">Ref:</span> {intent.ref_id}</p>}
          {intent.invoice_id && <p><span className="text-stone-500">Invoice:</span> {intent.invoice_id}</p>}
        </div>
      )}
      {gw && (
        <p className="text-xs text-stone-500">
          Live: Stripe {gw.stripe.configured ? "✓" : "—"} · Zarinpal {gw.zarinpal.configured ? "✓" : "—"}
        </p>
      )}
      <div className="flex justify-center gap-3">
        <Link to="/payments" className="rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-bold text-white">Payments</Link>
        <Link to="/invoices" className="rounded-xl border px-4 py-2.5 text-sm font-bold">Invoices</Link>
      </div>
    </div>
  );
}
