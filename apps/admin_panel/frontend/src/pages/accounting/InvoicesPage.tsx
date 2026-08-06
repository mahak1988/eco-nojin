import { useState, useEffect } from 'react'
import { Search, Loader2, AlertCircle, RefreshCw } from 'lucide-react'
import { accounting } from '../../api/econojinApi'

interface Invoice {
  id: string | number
  invoice_number?: string
  number?: string
  client_name?: string
  customer_name?: string
  status?: string
  amount?: number
  total?: number
  currency?: string
  issue_date?: string
  due_date?: string
  created_at?: string
}

const statusColors: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-800',
  sent: 'bg-blue-100 text-blue-800',
  paid: 'bg-green-100 text-green-800',
  overdue: 'bg-red-100 text-red-800',
  cancelled: 'bg-red-50 text-red-600',
}

const statusLabel: Record<string, string> = {
  draft: 'پیش‌نویس',
  sent: 'ارسال‌شده',
  paid: 'پرداخت‌شده',
  overdue: 'معوق',
  cancelled: 'لغو شده',
}

function normalizeList(raw: unknown): Invoice[] {
  if (Array.isArray(raw)) return raw as Invoice[]
  if (raw && typeof raw === 'object') {
    const o = raw as { data?: Invoice[]; items?: Invoice[] }
    return o.data ?? o.items ?? []
  }
  return []
}

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const raw = await accounting.listInvoices()
      setInvoices(normalizeList(raw))
    } catch (e: any) {
      setError(e?.message || 'خطا در بارگذاری صورتحساب‌ها')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const filtered = invoices.filter((inv) => {
    const num = inv.invoice_number || inv.number || ''
    const client = inv.client_name || inv.customer_name || ''
    const st = (inv.status || '').toLowerCase()
    const matchSearch =
      client.toLowerCase().includes(search.toLowerCase()) ||
      num.toLowerCase().includes(search.toLowerCase())
    const matchStatus = statusFilter === 'all' || st === statusFilter
    return matchSearch && matchStatus
  })

  const totalAmount = filtered.reduce(
    (sum, inv) => sum + Number(inv.amount ?? inv.total ?? 0),
    0
  )

  return (
    <div className="space-y-6" dir="rtl">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-3xl font-bold">صورتحساب‌ها</h1>
          <p className="text-muted-foreground">
            {filtered.length} مورد · مجموع{' '}
            {totalAmount.toLocaleString('fa-IR')}
          </p>
        </div>
        <button
          onClick={load}
          className="flex items-center gap-2 px-3 py-2 border rounded-lg text-sm hover:bg-accent"
        >
          <RefreshCw className="w-4 h-4" /> به‌روزرسانی
        </button>
      </div>

      <div className="flex gap-3 flex-wrap">
        <div className="relative flex-1 min-w-[180px]">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="جستجوی صورتحساب..."
            className="w-full pr-10 pl-4 py-2 border rounded-lg text-sm"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 border rounded-lg text-sm"
        >
          <option value="all">همه وضعیت‌ها</option>
          <option value="draft">پیش‌نویس</option>
          <option value="sent">ارسال‌شده</option>
          <option value="paid">پرداخت‌شده</option>
          <option value="overdue">معوق</option>
          <option value="cancelled">لغو شده</option>
        </select>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-eco-600" />
        </div>
      ) : (
        <div className="rounded-xl border bg-card shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="text-right p-4">شماره</th>
                <th className="text-right p-4">مشتری</th>
                <th className="text-right p-4">وضعیت</th>
                <th className="text-right p-4">مبلغ</th>
                <th className="text-right p-4">صدور</th>
                <th className="text-right p-4">سررسید</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-muted-foreground">
                    صورتحسابی یافت نشد
                  </td>
                </tr>
              ) : (
                filtered.map((invoice) => {
                  const st = (invoice.status || 'draft').toLowerCase()
                  return (
                    <tr key={String(invoice.id)} className="border-b last:border-0 hover:bg-muted/30">
                      <td className="p-4 font-mono">
                        {invoice.invoice_number || invoice.number || `#${invoice.id}`}
                      </td>
                      <td className="p-4 font-medium">
                        {invoice.client_name || invoice.customer_name || '—'}
                      </td>
                      <td className="p-4">
                        <span className={`px-2 py-1 rounded-full text-xs ${statusColors[st] || 'bg-gray-100'}`}>
                          {statusLabel[st] || st}
                        </span>
                      </td>
                      <td className="p-4 font-medium">
                        {Number(invoice.amount ?? invoice.total ?? 0).toLocaleString('fa-IR')}{' '}
                        {invoice.currency || 'IRR'}
                      </td>
                      <td className="p-4 text-muted-foreground text-xs">
                        {(invoice.issue_date || invoice.created_at || '—') &&
                          (invoice.issue_date || invoice.created_at
                            ? new Date(invoice.issue_date || invoice.created_at!).toLocaleDateString('fa-IR')
                            : '—')}
                      </td>
                      <td className="p-4 text-muted-foreground text-xs">
                        {invoice.due_date
                          ? new Date(invoice.due_date).toLocaleDateString('fa-IR')
                          : '—'}
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
