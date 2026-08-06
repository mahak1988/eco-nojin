/**
 * SatellitePage — Phase 2: unified API paths + credentials
 */
import { useState, useEffect } from 'react'
import {
  Satellite, MapPin, TrendingUp, TrendingDown, Minus,
  RefreshCw, AlertCircle, CheckCircle, Leaf,
} from 'lucide-react'
import { satellite } from '../api/econojinApi'

interface NDVIPoint {
  date: string
  mean_ndvi: number
  cloud_free_percentage: number
  source: string
}

interface ChangeDetection {
  period_a?: { start: string; end: string; mean_ndvi: number }
  period_b?: { start: string; end: string; mean_ndvi: number }
  delta_ndvi: number
  signal: 'greening' | 'browning' | 'stable'
}

const SIGNAL_ICON = {
  greening: <TrendingUp className="text-green-500 w-5 h-5" />,
  browning: <TrendingDown className="text-red-500 w-5 h-5" />,
  stable: <Minus className="text-yellow-500 w-5 h-5" />,
}
const SIGNAL_COLOR = {
  greening: 'bg-green-100 text-green-800',
  browning: 'bg-red-100 text-red-800',
  stable: 'bg-yellow-100 text-yellow-800',
}

export default function SatellitePage() {
  const [lat, setLat] = useState(32.65)
  const [lon, setLon] = useState(51.67)
  const [days, setDays] = useState(90)
  const [timeseries, setTimeseries] = useState<NDVIPoint[]>([])
  const [change, setChange] = useState<ChangeDetection | null>(null)
  const [geeStatus, setGeeStatus] = useState<{ available: boolean; provider?: string } | null>(null)
  const [mrvResult, setMrvResult] = useState<Record<string, number> | null>(null)
  const [loading, setLoading] = useState(false)
  const [mrvLoading, setMrvLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [red, setRed] = useState(0.08)
  const [nir, setNir] = useState(0.45)

  useEffect(() => {
    satellite.geeStatus().then(setGeeStatus).catch(() => setGeeStatus({ available: false, provider: 'synthetic' }))
  }, [])

  async function fetchData() {
    setLoading(true)
    setError(null)
    try {
      const [tsData, cd] = await Promise.all([
        satellite.timeseries(lat, lon, days),
        satellite.changeDetection(lat, lon, days).catch(() => null),
      ])
      setTimeseries((tsData.data as NDVIPoint[]) ?? [])
      if (cd) setChange(cd as ChangeDetection)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function calculateMrv() {
    setMrvLoading(true)
    try {
      setMrvResult(await satellite.mrvBands(red, nir))
    } catch (e: any) {
      setError(e.message)
    } finally {
      setMrvLoading(false)
    }
  }

  const avgNdvi =
    timeseries.length > 0
      ? (timeseries.reduce((s, p) => s + p.mean_ndvi, 0) / timeseries.length).toFixed(3)
      : '—'

  return (
    <div className="space-y-6" dir="rtl">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Satellite className="w-7 h-7 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold">داده‌های ماهواره‌ای</h1>
            <p className="text-muted-foreground text-sm">Sentinel-2 · NDVI · MRV کربن</p>
          </div>
        </div>
        {geeStatus && (
          <span
            className={`flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${
              geeStatus.available ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
            }`}
          >
            {geeStatus.available ? <CheckCircle className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
            {geeStatus.available ? 'GEE متصل' : `مصنوعی (${geeStatus.provider ?? 'synthetic'})`}
          </span>
        )}
      </div>

      <div className="bg-card border rounded-xl p-5">
        <h2 className="font-semibold mb-4 flex items-center gap-2">
          <MapPin className="w-4 h-4" /> موقعیت و بازه
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <label className="text-sm text-muted-foreground block mb-1">عرض</label>
            <input type="number" step="0.01" value={lat} onChange={(e) => setLat(Number(e.target.value))} className="w-full border rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="text-sm text-muted-foreground block mb-1">طول</label>
            <input type="number" step="0.01" value={lon} onChange={(e) => setLon(Number(e.target.value))} className="w-full border rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="text-sm text-muted-foreground block mb-1">روز</label>
            <select value={days} onChange={(e) => setDays(Number(e.target.value))} className="w-full border rounded-lg px-3 py-2 text-sm">
              {[30, 60, 90, 120, 180, 365].map((d) => (
                <option key={d} value={d}>{d} روز</option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <button onClick={fetchData} disabled={loading} className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Satellite className="w-4 h-4" />}
              دریافت داده
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm flex items-center gap-2">
          <AlertCircle className="w-4 h-4" /> {error}
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-card border rounded-xl p-4">
          <p className="text-xs text-muted-foreground mb-1">میانگین NDVI</p>
          <p className="text-2xl font-bold text-green-600">{avgNdvi}</p>
        </div>
        <div className="bg-card border rounded-xl p-4">
          <p className="text-xs text-muted-foreground mb-1">تعداد تصاویر</p>
          <p className="text-2xl font-bold">{timeseries.length}</p>
        </div>
        {change && (
          <>
            <div className="bg-card border rounded-xl p-4">
              <p className="text-xs text-muted-foreground mb-1">Δ NDVI</p>
              <p className={`text-2xl font-bold ${change.delta_ndvi > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {change.delta_ndvi > 0 ? '+' : ''}{change.delta_ndvi.toFixed(3)}
              </p>
            </div>
            <div className="bg-card border rounded-xl p-4">
              <p className="text-xs text-muted-foreground mb-1">وضعیت</p>
              <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${SIGNAL_COLOR[change.signal]}`}>
                {SIGNAL_ICON[change.signal]}
                {change.signal === 'greening' ? 'سرسبز' : change.signal === 'browning' ? 'خشک' : 'پایدار'}
              </span>
            </div>
          </>
        )}
      </div>

      {timeseries.length > 0 && (
        <div className="bg-card border rounded-xl overflow-hidden">
          <div className="p-4 border-b font-semibold flex items-center gap-2">
            <Leaf className="w-4 h-4 text-green-600" /> سری زمانی NDVI
          </div>
          <div className="overflow-x-auto max-h-72">
            <table className="w-full text-sm">
              <thead className="bg-muted/50 sticky top-0">
                <tr>
                  <th className="text-right px-4 py-2">تاریخ</th>
                  <th className="text-right px-4 py-2">NDVI</th>
                  <th className="text-right px-4 py-2">بدون ابر</th>
                  <th className="text-right px-4 py-2">منبع</th>
                </tr>
              </thead>
              <tbody>
                {timeseries.map((p, i) => (
                  <tr key={i} className="border-t hover:bg-muted/20">
                    <td className="px-4 py-2 font-mono text-xs">{p.date}</td>
                    <td className="px-4 py-2 font-bold text-green-700">{p.mean_ndvi.toFixed(3)}</td>
                    <td className="px-4 py-2 text-xs">{p.cloud_free_percentage?.toFixed(0) ?? '—'}%</td>
                    <td className="px-4 py-2 text-xs text-muted-foreground">{p.source}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="bg-card border rounded-xl p-5">
        <h2 className="font-semibold mb-4 flex items-center gap-2">
          <Leaf className="w-4 h-4 text-emerald-600" /> محاسبه EcoCredit
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 items-end">
          <div>
            <label className="text-sm text-muted-foreground block mb-1">قرمز (B04)</label>
            <input type="number" step="0.01" min={0} max={1} value={red} onChange={(e) => setRed(Number(e.target.value))} className="w-full border rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="text-sm text-muted-foreground block mb-1">NIR (B08)</label>
            <input type="number" step="0.01" min={0} max={1} value={nir} onChange={(e) => setNir(Number(e.target.value))} className="w-full border rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="text-sm text-muted-foreground block mb-1">NDVI</label>
            <div className="border rounded-lg px-3 py-2 text-sm bg-muted/30 font-mono">
              {nir + red > 0 ? ((nir - red) / (nir + red)).toFixed(3) : '—'}
            </div>
          </div>
          <button onClick={calculateMrv} disabled={mrvLoading} className="flex items-center justify-center gap-2 bg-emerald-600 text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-emerald-700 disabled:opacity-50">
            {mrvLoading && <RefreshCw className="w-4 h-4 animate-spin" />}
            محاسبه MRV
          </button>
        </div>
        {mrvResult && (
          <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3">
            {Object.entries(mrvResult).slice(0, 4).map(([k, v]) => (
              <div key={k} className="bg-emerald-50 rounded-lg p-3 text-center">
                <p className="text-xs text-muted-foreground">{k}</p>
                <p className="text-xl font-bold text-emerald-700">{typeof v === 'number' ? v.toFixed(3) : String(v)}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
