import { Link, useSearchParams } from "react-router-dom";
import { XCircle } from "lucide-react";

export default function PaymentCancelPage() {
  const [params] = useSearchParams();
  const intent = params.get("intent");
  const reason = params.get("reason");

  return (
    <div className="mx-auto max-w-lg space-y-6 p-8 text-center">
      <XCircle className="mx-auto h-14 w-14 text-red-500" />
      <h1 className="font-display text-2xl text-stone-800">Payment cancelled</h1>
      <p className="text-sm text-stone-600">
        {reason ? `Reason: ${reason}` : "You left the gateway or verification failed."}
      </p>
      {intent && <p className="font-mono text-xs text-stone-400">{intent}</p>}
      <div className="flex justify-center gap-3">
        <Link to="/payments" className="rounded-xl bg-stone-900 px-4 py-2.5 text-sm font-bold text-white">Try again</Link>
        <Link to="/invoices" className="rounded-xl border px-4 py-2.5 text-sm font-bold">Invoices</Link>
      </div>
    </div>
  );
}
