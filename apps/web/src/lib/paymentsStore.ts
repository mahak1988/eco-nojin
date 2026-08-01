/**
 * Payments + payment methods — offline-first, localStorage.
 * Mirrors warehouseStore / currencyStore pattern.
 */

import {
  INITIAL_PAYMENTS,
  INITIAL_METHODS,
  type Payment,
  type PaymentMethod,
  type PaymentStatus,
  type PaymentMethodKind,
} from "../components/payments/paymentsData";

const KEY_PAYMENTS = "econojin_payments_v1";
const KEY_METHODS = "econojin_payment_methods_v1";

export function readPayments(): Payment[] {
  try {
    const raw = localStorage.getItem(KEY_PAYMENTS);
    if (raw) {
      const parsed = JSON.parse(raw) as Payment[];
      if (Array.isArray(parsed) && parsed.length) return parsed;
    }
  } catch {
    /* ignore */
  }
  return [...INITIAL_PAYMENTS];
}

export function writePayments(list: Payment[]) {
  try {
    localStorage.setItem(KEY_PAYMENTS, JSON.stringify(list));
  } catch {
    /* ignore */
  }
}

export function readMethods(): PaymentMethod[] {
  try {
    const raw = localStorage.getItem(KEY_METHODS);
    if (raw) {
      const parsed = JSON.parse(raw) as PaymentMethod[];
      if (Array.isArray(parsed) && parsed.length) return parsed;
    }
  } catch {
    /* ignore */
  }
  return [...INITIAL_METHODS];
}

export function writeMethods(list: PaymentMethod[]) {
  try {
    localStorage.setItem(KEY_METHODS, JSON.stringify(list));
  } catch {
    /* ignore */
  }
}

export function addPayment(
  data: { method: PaymentMethodKind; amount: number; reference: string; last4?: string },
  current: Payment[]
): Payment[] {
  const next: Payment = {
    id: `p${Date.now()}`,
    method: data.method,
    amount: data.amount,
    status: "pending",
    date: new Date().toISOString(),
    reference: data.reference,
    last4: data.last4,
  };
  const list = [next, ...current];
  writePayments(list);
  return list;
}

export function updatePaymentStatus(id: string, status: PaymentStatus, current: Payment[]): Payment[] {
  const list = current.map((p) => (p.id === id ? { ...p, status } : p));
  writePayments(list);
  return list;
}

export function removePayment(id: string, current: Payment[]): Payment[] {
  const list = current.filter((p) => p.id !== id);
  writePayments(list);
  return list;
}

export function setDefaultMethod(id: string, current: PaymentMethod[]): PaymentMethod[] {
  const list = current.map((m) => ({
    ...m,
    isDefault:
      m.id === id
        ? true
        : m.kind === "credit_card" || m.kind === "bank_transfer"
          ? false
          : m.isDefault,
  }));
  writeMethods(list);
  return list;
}

export function addCardMethod(last4: string, holder: string, current: PaymentMethod[]): PaymentMethod[] {
  const next: PaymentMethod = {
    id: `m${Date.now()}`,
    kind: "credit_card",
    last4,
    holder: holder || "—",
    isDefault: current.every((m) => m.kind !== "credit_card" && m.kind !== "bank_transfer"),
  };
  const list = [...current, next];
  writeMethods(list);
  return list;
}

export function removeMethod(id: string, current: PaymentMethod[]): PaymentMethod[] {
  const target = current.find((m) => m.id === id);
  if (!target || target.kind === "ecocoin" || target.kind === "bitcoin") return current;
  let list = current.filter((m) => m.id !== id);
  if (target.isDefault) {
    const firstFiat = list.find((m) => m.kind === "credit_card" || m.kind === "bank_transfer");
    if (firstFiat) {
      list = list.map((m) => (m.id === firstFiat.id ? { ...m, isDefault: true } : m));
    }
  }
  writeMethods(list);
  return list;
}
