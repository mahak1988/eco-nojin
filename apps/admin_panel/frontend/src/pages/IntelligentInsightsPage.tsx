/**
 * Phase 4 — Intelligent insights (recommendations + alerts from real admin API)
 */
import { useEffect, useState } from 'react'
import { Brain, AlertTriangle, Lightbulb, Loader2, RefreshCw } from 'lucide-react'
import { api } from '../api/adminApi'

export default function IntelligentInsightsPage() {
  const [recs, setRecs] = useState<any[]>([])
  const [alerts, setAlerts] = useState<any[]>([])
  const [analytics, setAnalytics] = useState<any | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const [r1, r2, r3] = await Promise.allSettled([
        api.get('/smart-recommendations'),
        api.get('/intelligent-alerts'),
        api.get('/intelligent-analytics'),
      ])
      if (r1.status === 'fulfilled') setRecs(Array.isArray(r1.value.data) ? r1.value.data : [])
      if (r2.status === 'fulfilled') setAlerts(Array.isArray(r2.value.data) ? r2.value.data : [])
      if (r3.status === 'fulfilled') setAnalytics(r3.value.data)
      if (r1.status === 'rejected' && r2.status === 'rejected') {
        setError('خطا در دریافت بینش‌های هوشمند')
      }
    } catch (e: any) {
      setError(e?.message || 'خطا')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  return (
    <div className="space-y-6" dir="rtl">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Brain className="w-7 h-7 text-violet-600" />
          <div>
            <h1 className="text-2xl font-bold">بینش‌های هوشمند</h1>
            <p className="text-sm text-muted-foreground">توصیه‌ها و هشدارهای مبتنی بر داده سیستم</p>
          </div>
        </div>
        <button
          onClick={load}
          className="flex items-center gap-2 px-3 py-2 border rounded-lg text-sm hover:bg-accent"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          به‌روزرسانی
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-lg border border-red-200 bg-red-50 text-red-700 text-sm">{error}</div>
      )}

      {loading ? (
        <div className="flex justify-center py-16">
          <Loader2 className="w-8 h-8 animate-spin text-violet-600" />
        </div>
      ) : (
        <>
          {analytics?.summary && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {Object.entries(analytics.summary).map(([k, v]) => (
                <div key={k} className="rounded-xl border bg-card p-4">
                  <p className="text-xs text-muted-foreground">{k}</p>
                  <p className="text-lg font-bold">{String(v)}</p>
                </div>
              ))}
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-6">
            <div className="rounded-xl border bg-card p-5">
              <h2 className="font-semibold mb-3 flex items-center gap-2">
                <Lightbulb className="w-4 h-4 text-amber-500" /> توصیه‌ها ({recs.length})
              </h2>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {recs.length === 0 ? (
                  <p className="text-sm text-muted-foreground">توصیه‌ای موجود نیست</p>
                ) : (
                  recs.map((r, i) => (
                    <div key={r.id || i} className="p-3 rounded-lg bg-muted/30 text-sm">
                      <p className="font-medium">{r.title || r.name}</p>
                      <p className="text-muted-foreground text-xs mt-1">{r.description}</p>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="rounded-xl border bg-card p-5">
              <h2 className="font-semibold mb-3 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-red-500" /> هشدارها ({alerts.length})
              </h2>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {alerts.length === 0 ? (
                  <p className="text-sm text-muted-foreground">هشداری نیست</p>
                ) : (
                  alerts.map((a, i) => (
                    <div key={a.id || i} className="p-3 rounded-lg border border-amber-100 bg-amber-50/50 text-sm">
                      <p className="font-medium">{a.title}</p>
                      <p className="text-muted-foreground text-xs mt-1">{a.description}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
