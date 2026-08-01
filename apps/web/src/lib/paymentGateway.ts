/**
 * Client for Stripe / Zarinpal + demo fallback.
 */
const API_BASE =
  (import.meta as any).env?.VITE_API_URL?.replace(/\/$/, "") ||
  "http://localhost:8000";

export type GatewayStatus = {
  stripe: { configured: boolean; publishable_key?: string | null; webhook_configured: boolean };
  zarinpal: { configured: boolean; sandbox: boolean };
  demo_fallback: boolean;
};

export type CheckoutResult = {
  intent_id: string;
  provider: "stripe" | "zarinpal" | "demo";
  checkout_url?: string;
  status: string;
  message?: string;
  invoice_id?: string;
  amount?: number;
  currency?: string;
};

export async function fetchGatewayStatus(): Promise<GatewayStatus> {
  const r = await fetch(`${API_BASE}/api/v1/payments/status`);
  if (!r.ok) throw new Error(`status ${r.status}`);
  return r.json();
}

export async function createCheckout(input: {
  amount: number;
  currency: string;
  description: string;
  invoiceId?: string;
  provider?: "auto" | "stripe" | "zarinpal" | "demo";
  customerEmail?: string;
}): Promise<CheckoutResult> {
  const r = await fetch(`${API_BASE}/api/v1/payments/checkout`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      amount: input.amount,
      currency: input.currency,
      description: input.description,
      invoice_id: input.invoiceId,
      provider: input.provider ?? "auto",
      customer_email: input.customerEmail,
    }),
  });
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `checkout ${r.status}`);
  }
  return r.json();
}

export async function getIntent(intentId: string): Promise<CheckoutResult & { ref_id?: string }> {
  const r = await fetch(`${API_BASE}/api/v1/payments/intent/${intentId}`);
  if (!r.ok) throw new Error(`intent ${r.status}`);
  return r.json();
}

export function redirectToCheckout(result: CheckoutResult) {
  if (result.checkout_url) {
    window.location.href = result.checkout_url;
  }
}
