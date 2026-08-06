import { useState, useEffect } from 'react'
import { Search, Filter, Loader2, AlertCircle, RefreshCw, Calendar } from 'lucide-react'
import { fetchAuditLogs, AuditLog } from '../api/adminApi'

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [eventType, setEventType] = useState('')
  const [actorEmail, setActorEmail] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')

  const loadLogs = () => {
    setLoading(true)
    setError(null)
    const params: Record<string, unknown> = { limit: 100 }
    if (eventType) params.event_type = eventType
    if (actorEmail) params.actor_email = actorEmail
    if (dateFrom) params.date_from = new Date(dateFrom).toISOString()
    if (dateTo) params.date_to = new Date(dateTo).toISOString()

    fetchAuditLogs(params as any)
      .then(setLogs)
      .catch((err) => setError(err?.message || 'خطا در بارگذاری لاگ‌های حسابرسی'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadLogs()
  }, [])

  return (
    <div className="space-y-6" dir="rtl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">لاگ‌های حسابرسی</h1>
          <p className="text-muted-foreground">ردیابی فعالیت‌های سیستم · {logs.length} مورد</p>
        </div>
        <button
          onClick={loadLogs}
          className="flex items-center gap-2 px-3 py-2 border rounded-lg hover:bg-accent text-sm"
        >
          <RefreshCw className="w-4 h-4" /> به‌روزرسانی
        </button>
      </div>

      <div className="rounded-xl border bg-card p-4 shadow-sm">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
          <div className="relative">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              value={eventType}
              onChange={(e) => setEventType(e.target.value)}
              placeholder="نوع رویداد (مثلاً login)"
              className="w-full pr-10 pl-4 py-2 border rounded-lg text-sm"
            />
          </div>
          <div>
            <input
              value={actorEmail}
              onChange={(e) => setActorEmail(e.target.value)}
              placeholder="ایمیل عامل"
              className="w-full px-4 py-2 border rounded-lg text-sm"
            />
          </div>
          <div className="relative">
            <Calendar className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="w-full pr-10 pl-4 py-2 border rounded-lg text-sm"
            />
          </div>
          <div className="relative">
            <Calendar className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="w-full pr-10 pl-4 py-2 border rounded-lg text-sm"
            />
          </div>
          <button
            onClick={loadLogs}
            className="flex items-center justify-center gap-2 px-4 py-2 bg-eco-600 text-white rounded-lg hover:bg-eco-700 text-sm"
          >
            <Filter className="w-4 h-4" /> فیلتر
          </button>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          {error}
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-eco-600" />
        </div>
      )}

      {!loading && (
        <div className="rounded-xl border bg-card shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="text-right p-4">شناسه</th>
                  <th className="text-right p-4">نوع رویداد</th>
                  <th className="text-right p-4">عامل</th>
                  <th className="text-right p-4">داده</th>
                  <th className="text-right p-4">زمان</th>
                </tr>
              </thead>
              <tbody>
                {logs.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-muted-foreground">
                      لاگی یافت نشد
                    </td>
                  </tr>
                ) : (
                  logs.map((log) => (
                    <tr key={log.id} className="border-b last:border-0 hover:bg-muted/30">
                      <td className="p-4 font-mono text-xs">{log.id}</td>
                      <td className="p-4">
                        <span className="px-2 py-1 rounded-full bg-blue-100 text-blue-800 text-xs">
                          {log.event_type}
                        </span>
                      </td>
                      <td className="p-4">
                        <span className="text-sm">{log.actor_email || 'سیستم'}</span>
                      </td>
                      <td className="p-4 max-w-[200px] truncate text-muted-foreground text-xs font-mono">
                        {log.event_data || '—'}
                      </td>
                      <td className="p-4 text-muted-foreground text-xs">
                        {new Date(log.created_at).toLocaleString('fa-IR')}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
