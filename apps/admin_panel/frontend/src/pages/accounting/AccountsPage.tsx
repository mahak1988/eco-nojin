import { useState, useEffect } from 'react'
import { Plus, Search, Loader2, AlertCircle, RefreshCw } from 'lucide-react'
import { accounting, Account } from '../../api/econojinApi'
import { useToast } from '../../components/Toast'

const typeColors: Record<string, string> = {
  asset: 'bg-green-100 text-green-800',
  liability: 'bg-red-100 text-red-800',
  equity: 'bg-purple-100 text-purple-800',
  revenue: 'bg-blue-100 text-blue-800',
  expense: 'bg-amber-100 text-amber-800',
  income: 'bg-blue-100 text-blue-800',
}

const typeLabel: Record<string, string> = {
  asset: 'دارایی',
  liability: 'بدهی',
  equity: 'حقوق صاحبان',
  revenue: 'درآمد',
  income: 'درآمد',
  expense: 'هزینه',
}

function normalizeList(raw: Account[] | { data?: Account[]; items?: Account[] }): Account[] {
  if (Array.isArray(raw)) return raw
  return raw.data ?? raw.items ?? []
}

export default function AccountsPage() {
  const { toast } = useToast()
  const [accounts, setAccounts] = useState<Account[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [filterType, setFilterType] = useState('all')
  const [summary, setSummary] = useState<Record<string, unknown> | null>(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const [accRaw, sum] = await Promise.all([
        accounting.listAccounts(),
        accounting.summary().catch(() => null),
      ])
      setAccounts(normalizeList(accRaw))
      setSummary(sum)
    } catch (e: any) {
      setError(e?.message || 'خطا در بارگذاری حساب‌ها')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const seedDemo = async () => {
    try {
      await accounting.seedDemo()
      toast('داده نمونه حسابداری بارگذاری شد', 'success')
      load()
    } catch (e: any) {
      toast(e?.message || 'خطا در seed', 'error')
    }
  }

  const filtered = accounts.filter((a) => {
    const t = (a.type || a.account_type || '').toLowerCase()
    const matchSearch =
      (a.name || '').toLowerCase().includes(search.toLowerCase()) ||
      (a.code || '').includes(search)
    const matchType = filterType === 'all' || t === filterType
    return matchSearch && matchType
  })

  return (
    <div className="space-y-6" dir="rtl">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-3xl font-bold">حساب‌ها</h1>
          <p className="text-muted-foreground">نمودار حساب‌ها · {accounts.length} مورد</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={seedDemo}
            className="px-3 py-2 border rounded-lg text-sm hover:bg-accent"
          >
            داده نمونه
          </button>
          <button
            onClick={load}
            className="flex items-center gap-2 px-3 py-2 border rounded-lg text-sm hover:bg-accent"
          >
            <RefreshCw className="w-4 h-4" /> به‌روزرسانی
          </button>
        </div>
      </div>

      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { label: 'کل درآمد', key: 'total_income' },
            { label: 'کل هزینه', key: 'total_expense' },
            { label: 'تراز', key: 'balance' },
            { label: 'تعداد حساب', key: 'account_count' },
          ].map(({ label, key }) => (
            <div key={key} className="rounded-xl border bg-card p-4">
              <p className="text-xs text-muted-foreground">{label}</p>
              <p className="text-lg font-bold">
                {summary[key] != null
                  ? Number(summary[key]).toLocaleString('fa-IR')
                  : '—'}
              </p>
            </div>
          ))}
        </div>
      )}

      <div className="flex gap-3 flex-wrap">
        <div className="relative flex-1 min-w-[180px]">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="جستجوی حساب..."
            className="w-full pr-10 pl-4 py-2 border rounded-lg text-sm"
          />
        </div>
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="px-4 py-2 border rounded-lg text-sm"
        >
          <option value="all">همه انواع</option>
          <option value="asset">دارایی</option>
          <option value="liability">بدهی</option>
          <option value="equity">حقوق صاحبان</option>
          <option value="revenue">درآمد</option>
          <option value="expense">هزینه</option>
        </select>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          {error}
          <button onClick={seedDemo} className="mr-auto underline text-xs">
            بارگذاری نمونه
          </button>
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
                <th className="text-right p-4">کد</th>
                <th className="text-right p-4">نام</th>
                <th className="text-right p-4">نوع</th>
                <th className="text-right p-4">مانده</th>
                <th className="text-right p-4">وضعیت</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-muted-foreground">
                    حسابی یافت نشد. از «داده نمونه» استفاده کنید.
                  </td>
                </tr>
              ) : (
                filtered.map((account) => {
                  const t = (account.type || account.account_type || '').toLowerCase()
                  return (
                    <tr key={String(account.id)} className="border-b last:border-0 hover:bg-muted/30">
                      <td className="p-4 font-mono">{account.code}</td>
                      <td className="p-4 font-medium">{account.name}</td>
                      <td className="p-4">
                        <span className={`px-2 py-1 rounded-full text-xs ${typeColors[t] || 'bg-gray-100'}`}>
                          {typeLabel[t] || t || '—'}
                        </span>
                      </td>
                      <td className="p-4 font-medium">
                        {(account.balance ?? 0).toLocaleString('fa-IR')}{' '}
                        {account.currency || 'IRR'}
                      </td>
                      <td className="p-4">
                        <span
                          className={`px-2 py-1 rounded-full text-xs ${
                            account.is_active !== false
                              ? 'bg-green-100 text-green-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {account.is_active !== false ? 'فعال' : 'غیرفعال'}
                        </span>
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
