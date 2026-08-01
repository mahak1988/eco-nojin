/**
 * Invoices — offline-first localStorage + link to payments.
 */

import {
  INITIAL_INVOICES,
  type Invoice,
  type InvoiceStatus,
} from "../components/invoices/invoicesData";
import { readPayments, writePayments } from "./paymentsStore";
import {
  type Payment,
  type PaymentMethodKind,
} from "../components/payments/paymentsData";

const KEY = "econojin_invoices_v1";

export function readInvoices(): Invoice[] {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as Invoice[];
      if (Array.isArray(parsed) && parsed.length) return parsed;
    }
  } catch {
    /* ignore */
  }
  return [...INITIAL_INVOICES];
}

export function writeInvoices(list: Invoice[]) {
  try {
    localStorage.setItem(KEY, JSON.stringify(list));
  } catch {
    /* ignore */
  }
}

export function addInvoice(
  data: { client: string; amount: number; status: InvoiceStatus },
  current: Invoice[]
): Invoice[] {
  const nums = current
    .map((i) => parseInt(i.id.replace(/\D/g, ""), 10))
    .filter((n) => !isNaN(n));
  const max = nums.length ? Math.max(...nums) : 0;
  const id = `INV-${String(max + 1).padStart(3, "0")}`;
  const next: Invoice = {
    id,
    client: data.client,
    amount: data.amount,
    date: new Date().toISOString(),
    status: data.status,
  };
  const list = [next, ...current];
  writeInvoices(list);
  return list;
}

export function setInvoiceStatus(
  id: string,
  status: InvoiceStatus,
  current: Invoice[]
): Invoice[] {
  const list = current.map((i) => (i.id === id ? { ...i, status } : i));
  writeInvoices(list);
  return list;
}

/**
 * Pay an invoice: creates a completed payment linked by invoiceId,
 * marks invoice as paid.
 */
export function payInvoice(
  inv: Invoice,
  method: PaymentMethodKind = "credit_card",
  invoices: Invoice[]
): { invoices: Invoice[]; paymentId: string } {
  if (inv.status === "paid") {
    return { invoices, paymentId: "" };
  }

  const paymentId = `p${Date.now()}`;
  const payment: Payment = {
    id: paymentId,
    method,
    amount: inv.amount,
    status: "completed",
    date: new Date().toISOString(),
    reference: `INV-PAY-${inv.id}-${Date.now().toString().slice(-6)}`,
    invoiceId: inv.id,
  };

  const payments = readPayments();
  writePayments([payment, ...payments]);

  const nextInvoices = setInvoiceStatus(inv.id, "paid", invoices);
  return { invoices: nextInvoices, paymentId };
}
