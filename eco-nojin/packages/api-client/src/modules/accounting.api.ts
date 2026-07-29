/**
 * Accounting API Client
 * =====================
 * TypeScript client for accounting module endpoints.
 */

import { apiClient } from '../core/instance';

// ── Types ─────────────────────────────────────────────────────────────
export interface Account {
  id: string;
  code: string;
  name: string;
  name_fa?: string;
  account_type: 'asset' | 'liability' | 'equity' | 'income' | 'expense';
  parent_id?: string;
  description?: string;
  is_active: boolean;
  is_system: boolean;
  created_at: string;
  updated_at: string;
  balance: string;
}

export interface JournalItem {
  id: number;
  entry_id: string;
  account_id: string;
  entry_type: 'debit' | 'credit';
  amount: string;
  description?: string;
  created_at: string;
}

export interface JournalEntry {
  id: string;
  date: string;
  description: string;
  reference?: string;
  is_posted: boolean;
  created_at: string;
  updated_at: string;
  total_debits: string;
  total_credits: string;
  is_balanced: boolean;
  items: JournalItem[];
}

export interface InvoiceItem {
  id: number;
  invoice_id: string;
  description: string;
  quantity: string;
  unit_price: string;
  tax_rate: string;
  line_total: string;
}

export interface Invoice {
  id: string;
  number: string;
  client_name: string;
  client_email?: string;
  issue_date: string;
  due_date: string;
  status: 'draft' | 'pending' | 'paid' | 'overdue' | 'cancelled';
  subtotal: string;
  tax_amount: string;
  total: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  items: InvoiceItem[];
}

export interface Payment {
  id: string;
  invoice_id?: string;
  amount: string;
  currency?: string;
  payment_method: 'cash' | 'bank_transfer' | 'check' | 'credit_card' | 'ecocoin' | 'carbon_credit';
  reference?: string;
  notes?: string;
  paid_at: string;
  created_at: string;
}

export interface Budget {
  id: string;
  name: string;
  account_id: string;
  period_start: string;
  period_end: string;
  planned_amount: string;
  actual_amount: string;
  variance?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface DashboardSummary {
  total_income: string;
  total_expense: string;
  net_profit: string;
  eco_rewards_distributed: string;
  carbon_credits_value: string;
  transactions_count: number;
  current_balance: string;
}

// ── API Functions ───────────────────────────────────────────────────────
export const accountingApi = {
  // Accounts
  getAccounts: (params?: { skip?: number; limit?: number; account_type?: string }) =>
    apiClient.get<Account[]>('/accounting/accounts', { params }),

  getAccount: (accountId: string) =>
    apiClient.get<Account>(`/accounting/accounts/${accountId}`),

  createAccount: (data: Partial<Account>) =>
    apiClient.post<Account>('/accounting/accounts', data),

  updateAccount: (accountId: string, data: Partial<Account>) =>
    apiClient.patch<Account>(`/accounting/accounts/${accountId}`, data),

  // Journal Entries
  getJournalEntries: (params?: { skip?: number; limit?: number; is_posted?: boolean }) =>
    apiClient.get<{ items: JournalEntry[]; total: number }>('/accounting/journal-entries', { params }),

  createJournalEntry: (data: {
    date: string;
    description: string;
    reference?: string;
    items: Array<{
      account_id: string;
      entry_type: 'debit' | 'credit';
      amount: string;
      description?: string;
    }>;
  }) => apiClient.post<JournalEntry>('/accounting/journal-entries', data),

  // Invoices
  getInvoices: (params?: { skip?: number; limit?: number; status?: string }) =>
    apiClient.get<{ items: Invoice[]; total: number }>('/accounting/invoices', { params }),

  getInvoice: (invoiceId: string) =>
    apiClient.get<Invoice>(`/accounting/invoices/${invoiceId}`),

  createInvoice: (data: {
    client_name: string;
    client_email?: string;
    issue_date: string;
    due_date: string;
    notes?: string;
    items: Array<{
      description: string;
      quantity: string;
      unit_price: string;
      tax_rate?: string;
    }>;
  }) => apiClient.post<Invoice>('/accounting/invoices', data),

  updateInvoice: (invoiceId: string, data: Partial<Invoice>) =>
    apiClient.patch<Invoice>(`/accounting/invoices/${invoiceId}`, data),

  // Payments
  getPayments: (params?: { skip?: number; limit?: number }) =>
    apiClient.get<{ items: Payment[]; total: number }>('/accounting/payments', { params }),

  createPayment: (data: Partial<Payment>) =>
    apiClient.post<Payment>('/accounting/payments', data),

  // Budgets
  getBudgets: (params?: { skip?: number; limit?: number }) =>
    apiClient.get<{ items: Budget[]; total: number }>('/accounting/budgets', { params }),

  createBudget: (data: Partial<Budget>) =>
    apiClient.post<Budget>('/accounting/budgets', data),

  // Dashboard
  getDashboardSummary: () =>
    apiClient.get<DashboardSummary>('/accounting/summary'),
};

export default accountingApi;