/**
 * SatellitePage — داده‌های ماهواره‌ای Sentinel-2 / NDVI / تغییرات پوشش گیاهی
 */
import { useState, useEffect } from 'react'
import {
  Satellite, MapPin, TrendingUp, TrendingDown, Minus,
  RefreshCw, AlertCircle, CheckCircle, Leaf
} from 'lucide-react'

const API = import.meta.env.VITE_API_BASE_URL ?? ''

interface NDVIPoint {
  date: string
  mean_ndvi: number
  cloud_free_percentage: number
  source: string
}

interface ChangeDetection {
  period_a: { start: string; end: string; mean_ndvi: number }
  period_b: { start: string; end: string; mean_ndvi: number }
  delta_ndvi: number
  signal: 'greening' | 'browning' | 'stable'
}

interface GeeStatus {
  available: boolean
  provider?: string
}

interface MrvResult {
  ecocredit_score?: number
  carbon_t_ha?: number
  ndvi?: number
  evi?: number
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
  const [geeStatus, setGeeStatus] = useState<GeeStatus | null>(null)
  const [mrvResult, setMrvResult] = useState<MrvResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [mrvLoading, setMrvLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Red/NIR for MRV bands calculation
  const [red, setRed] = useState(0.08)
  const [nir, setNir] = useState(0.45)

  useEffect(() => {
    fetchGeeStatus()
  }, [])

  async function fetchGeeStatus() {
    try {
      const r = await fetch(`${API}/api/v1/satellite/gee/status`)
      if (r.ok) setGeeStatus(await r.json())
    } catch {
      setGeeStatus({ available: false, provider: 'synthetic' })
    }
  }

  async function fetchData() {
    setLoading(true)
    setError(null)
    try {
      const [tsResp, cdResp] = await Promise.all([
        fetch(`${API}/api/v1/satellite/timeseries?lat=${lat}&lon=${lon}&days=${days}`),
        fetch(`${API}/api/v1/satellite/change-detection?lat=${lat}&lon=${lon}&days=${days}`, {
          method: 'POST',
        }),
      ])
      if (tsResp.ok) {
        const tsData = await tsResp.json()
        setTimeseries(tsData.data ?? [])
      }
      if (cdResp.ok) {
        setChange(await cdResp.json())
      }
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function calculateMrv() {
    setMrvLoading(true)
    try {
      const resp = await fetch(`${API}/api/v1/satellite/mrv/bands`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ red, nir }),
      })
      if (resp.ok) setMrvResult(await resp.json())
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
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Satellite className="w-7 h-7 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold">داده‌های ماهواره‌ای</h1>
            <p className="text-muted-foreground text-sm">Sentinel-2 · NDVI · تغییرات پوشش گیاهی · MRV کربن</p>
          </div>
        </div>
        {/* GEE status badge */}
        {geeStatus && (
          <span
            className={`flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${
              geeStatus.available ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
            }`}
          >
            {geeStatus.available ? <CheckCircle className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
            {geeStatus.available ? 'Google Earth Engine متصل' : `داده مصنوعی (${geeStatus.provider ?? 'synthetic'})`}
          </span>
        )}
      </div>

      {/* Coordinate picker */}
      <div className="bg-card border rounded-xl p-5">
        <h2 className="font-semibold mb-4 flex items-center gap-2">
          <MapPin className="w-4 h-4" /> انتخاب موقعیت و بازه زمانی
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <label className="text-sm text-muted-foreground block mb-1">عرض جغرافیایی</label>
            <input
              type="number"
              step="0.01"
              value={lat}
              onChange={e => setLat(Number(e.target.value))}
              className="w-full border rounded-lg px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="text-sm text-muted-foreground block mb-1">طول جغرافیایی</label>
            <input
              type="number"
              step="0.01"
              value={lon}
              onChange={e => setLon(Number(e.target.value))}
              className="w-full border rounded-lg px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="text-sm text-muted-foreground block mb-1">تعداد روز</label>
            <select
              value={days}
              onChange={e => setDays(Number(e.target.value))}
              className="w-full border rounded-lg px-3 py-2 text-sm"
            >
              {[30, 60, 90, 120, 180, 365].map(d => (
                <option key={d} value={d}>{d} روز</option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={fetchData}
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
            >
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

      {/* Summary cards */}
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
              <p className="text-xs text-muted-foreground mb-1">تغییر NDVI</p>
              <p className={`text-2xl font-bold ${change.delta_ndvi > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {change.delta_ndvi > 0 ? '+' : ''}{change.delta_ndvi.toFixed(3)}
              </p>
            </div>
            <div className="bg-card border rounded-xl p-4">
              <p className="text-xs text-muted-foreground mb-1">وضعیت پوشش</p>
              <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${SIGNAL_COLOR[change.signal]}`}>
                {SIGNAL_ICON[change.signal]}
                {change.signal === 'greening' ? 'سرسبز‌شونده' : change.signal === 'browning' ? 'خشک‌شونده' : 'پایدار'}
              </span>
            </div>
          </>
        )}
      </div>

      {/* NDVI Timeseries table */}
      {timeseries.length > 0 && (
        <div className="bg-card border rounded-xl overflow-hidden">
          <div className="p-4 border-b font-semibold flex items-center gap-2">
            <Leaf className="w-4 h-4 text-green-600" />
            سری زمانی NDVI
          </div>
          <div className="overflow-x-auto max-h-72">
            <table className="w-full text-sm">
              <thead className="bg-muted/50 sticky top-0">
                <tr>
                  <th className="text-right px-4 py-2 font-medium">تاریخ</th>
                  <th className="text-right px-4 py-2 font-medium">NDVI میانگین</th>
                  <th className="text-right px-4 py-2 font-medium">پوشش ابری</th>
                  <th className="text-right px-4 py-2 font-medium">منبع</th>
                  <th className="text-right px-4 py-2 font-medium">نمودار</th>
                </tr>
              </thead>
              <tbody>
                {timeseries.map((p, i) => (
                  <tr key={i} className="border-t hover:bg-muted/20">
                    <td className="px-4 py-2 font-mono text-xs">{p.date}</td>
                    <td className="px-4 py-2 font-bold text-green-700">{p.mean_ndvi.toFixed(3)}</td>
                    <td className="px-4 py-2 text-xs">{p.cloud_free_percentage?.toFixed(0) ?? '—'}%</td>
                    <td className="px-4 py-2 text-xs text-muted-foreground">{p.source}</td>
                    <td className="px-4 py-2">
                      <div className="w-24 bg-muted rounded-full h-2">
                        <div
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${Math.max(0, Math.min(100, p.mean_ndvi * 100))}%` }}
                        />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* MRV Calculator */}
      <div className="bg-card border rounded-xl p-5">
        <h2 className="font-semibold mb-4 flex items-center gap-2">
          <Leaf className="w-4 h-4 text-emerald-600" />
          محاسبه EcoCredit از بازتاب باندها
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 items-end">
          <div>
            <label className="text-sm text-muted-foreground block mb-1">بازتاب قرمز (B04)</label>
            <input
              type="number" step="0.01" min="0" max="1" value={red}
              onChange={e => setRed(Number(e.target.value))}
              className="w-full border rounded-lg px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="text-sm text-muted-foreground block mb-1">بازتاب NIR (B08)</label>
            <input
              type="number" step="0.01" min="0" max="1" value={nir}
              onChange={e => setNir(Number(e.target.value))}
              className="w-full border rounded-lg px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="text-sm text-muted-foreground block mb-1">NDVI تخمینی</label>
            <div className="border rounded-lg px-3 py-2 text-sm bg-muted/30 font-mono">
              {nir + red > 0 ? ((nir - red) / (nir + red)).toFixed(3) : '—'}
            </div>
          </div>
          <button
            onClick={calculateMrv}
            disabled={mrvLoading}
            className="flex items-center justify-center gap-2 bg-emerald-600 text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-emerald-700 disabled:opacity-50"
          >
            {mrvLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : null}
            محاسبه MRV
          </button>
        </div>
        {mrvResult && (
          <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3">
            {mrvResult.ecocredit_score !== undefined && (
              <div className="bg-emerald-50 rounded-lg p-3 text-center">
                <p className="text-xs text-muted-foreground">EcoCredit Score</p>
                <p className="text-xl font-bold text-emerald-700">{mrvResult.ecocredit_score.toFixed(1)}</p>
              </div>
            )}
            {mrvResult.ndvi !== undefined && (
              <div className="bg-green-50 rounded-lg p-3 text-center">
                <p className="text-xs text-muted-foreground">NDVI</p>
                <p className="text-xl font-bold text-green-700">{mrvResult.ndvi.toFixed(3)}</p>
              </div>
            )}
            {mrvResult.carbon_t_ha !== undefined && (
              <div className="bg-blue-50 rounded-lg p-3 text-center">
                <p className="text-xs text-muted-foreground">کربن (t/ha)</p>
                <p className="text-xl font-bold text-blue-700">{mrvResult.carbon_t_ha.toFixed(2)}</p>
              </div>
            )}
            {mrvResult.evi !== undefined && (
              <div className="bg-teal-50 rounded-lg p-3 text-center">
                <p className="text-xs text-muted-foreground">EVI</p>
                <p className="text-xl font-bold text-teal-700">{mrvResult.evi.toFixed(3)}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
