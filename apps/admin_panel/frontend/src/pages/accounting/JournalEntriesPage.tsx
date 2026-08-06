import { useState, useEffect } from 'react'
import { Search, CheckCircle2, Loader2, AlertCircle, RefreshCw } from 'lucide-react'
import { accounting } from '../../api/econojinApi'

interface JournalEntry {
  id: string | number
  entry_date?: string
  date?: string
  created_at?: string
  description?: string
  is_posted?: boolean
  status?: string
  lines_count?: number
  total_debit?: number
  total_credit?: number
  debit?: number
  credit?: number
}

function normalizeList(raw: unknown): JournalEntry[] {
  if (Array.isArray(raw)) return raw as JournalEntry[]
  if (raw && typeof raw === 'object') {
    const o = raw as { data?: JournalEntry[]; items?: JournalEntry[] }
    return o.data ?? o.items ?? []
  }
  return []
}

export default function JournalEntriesPage() {
  const [entries, setEntries] = useState<JournalEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const raw = await accounting.listJournals()
      setEntries(normalizeList(raw))
    } catch (e: any) {
      setError(e?.message || 'خطا در بارگذاری اسناد دفتر روزنامه')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const filtered = entries.filter((e) =>
    (e.description || '').toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-6" dir="rtl">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-3xl font-bold">دفتر روزنامه</h1>
          <p className="text-muted-foreground">ثبت دوطرفه حسابداری · {entries.length} سند</p>
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
          placeholder="جستجوی شرح سند..."
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
                <th className="text-right p-4">تاریخ</th>
                <th className="text-right p-4">شرح</th>
                <th className="text-right p-4">ردیف‌ها</th>
                <th className="text-right p-4">بدهکار</th>
                <th className="text-right p-4">بستانکار</th>
                <th className="text-right p-4">وضعیت</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-muted-foreground">
                    سندی یافت نشد
                  </td>
                </tr>
              ) : (
                filtered.map((entry) => {
                  const posted =
                    entry.is_posted === true ||
                    (entry.status || '').toLowerCase() === 'posted'
                  const date = entry.entry_date || entry.date || entry.created_at
                  return (
                    <tr key={String(entry.id)} className="border-b last:border-0 hover:bg-muted/30">
                      <td className="p-4 font-mono text-xs">
                        {date ? new Date(date).toLocaleDateString('fa-IR') : '—'}
                      </td>
                      <td className="p-4 font-medium">{entry.description || '—'}</td>
                      <td className="p-4 text-center">{entry.lines_count ?? '—'}</td>
                      <td className="p-4 font-medium">
                        {Number(entry.total_debit ?? entry.debit ?? 0).toLocaleString('fa-IR')}
                      </td>
                      <td className="p-4 font-medium">
                        {Number(entry.total_credit ?? entry.credit ?? 0).toLocaleString('fa-IR')}
                      </td>
                      <td className="p-4">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs ${
                            posted
                              ? 'bg-green-100 text-green-800'
                              : 'bg-amber-100 text-amber-800'
                          }`}
                        >
                          {posted && <CheckCircle2 className="w-3 h-3" />}
                          {posted ? 'ثبت‌شده' : 'پیش‌نویس'}
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
