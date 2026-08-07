import { useState, useEffect } from 'react'
import { Search, Loader2, AlertCircle, RefreshCw } from 'lucide-react'
import { accounting } from '../../api/econojinApi'

interface Payment {
  id: string | number
  invoice_number?: string
  client_name?: string
  amount?: number
  payment_method?: string
  method?: string
  paid_at?: string
  created_at?: string
  currency?: string
}

const methodLabel: Record<string, string> = {
  bank_transfer: 'انتقال بانکی',
  credit_card: 'کارت',
  cash: 'نقد',
  cheque: 'چک',
  online: 'آنلاین',
}

function normalizeList(raw: unknown): Payment[] {
  if (Array.isArray(raw)) return raw as Payment[]
  if (raw && typeof raw === 'object') {
    const o = raw as { data?: Payment[]; items?: Payment[] }
    return o.data ?? o.items ?? []
  }
  return []
}

export default function PaymentsPage() {
  const [payments, setPayments] = useState<Payment[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const raw = await accounting.listPayments()
      setPayments(normalizeList(raw))
    } catch (e: any) {
      setError(e?.message || 'خطا در بارگذاری پرداخت‌ها')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const filtered = payments.filter(
    (p) =>
      (p.client_name || '').toLowerCase().includes(search.toLowerCase()) ||
      (p.invoice_number || '').toLowerCase().includes(search.toLowerCase())
  )
  const totalReceived = filtered.reduce((sum, p) => sum + Number(p.amount ?? 0), 0)

  return (
    <div className="space-y-6" dir="rtl">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-3xl font-bold">پرداخت‌ها</h1>
          <p className="text-muted-foreground">
            مجموع دریافتی: {totalReceived.toLocaleString('fa-IR')}
          </p>
        </div>
        <button
          onClick={load}
          className="flex items-center gap-2 px-3 py-2 border rounded-lg text-sm hover:bg-accent"
        >
          <RefreshCw className="w-4 h-4" /> به‌روزرسانی
        </button>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="جستجوی پرداخت..."
          className="w-full pr-10 pl-4 py-2 border rounded-lg text-sm"
        />
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
                <th className="text-right p-4">صورتحساب</th>
                <th className="text-right p-4">مشتری</th>
                <th className="text-right p-4">مبلغ</th>
                <th className="text-right p-4">روش</th>
                <th className="text-right p-4">تاریخ</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-muted-foreground">
                    پرداختی ثبت نشده است
                  </td>
                </tr>
              ) : (
                filtered.map((payment) => {
                  const method = (payment.payment_method || payment.method || '').toLowerCase()
                  const date = payment.paid_at || payment.created_at
                  return (
                    <tr key={String(payment.id)} className="border-b last:border-0 hover:bg-muted/30">
                      <td className="p-4 font-mono">{payment.invoice_number || '—'}</td>
                      <td className="p-4 font-medium">{payment.client_name || '—'}</td>
                      <td className="p-4 font-medium">
                        {Number(payment.amount ?? 0).toLocaleString('fa-IR')}{' '}
                        {payment.currency || 'IRR'}
                      </td>
                      <td className="p-4">{methodLabel[method] || method || '—'}</td>
                      <td className="p-4 text-muted-foreground text-xs">
                        {date ? new Date(date).toLocaleDateString('fa-IR') : '—'}
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
