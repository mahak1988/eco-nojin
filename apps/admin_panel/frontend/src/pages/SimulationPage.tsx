/**
 * SimulationPage — مدل‌های شبیه‌سازی کشاورزی/آب‌وهوا/کربن
 * پشتیبانی از: AquaCrop, RothC, SWAT+, Climate, AquaCrop-MRV, ...
 */
import { useState, useEffect } from 'react'
import {
  FlaskConical, Play, RefreshCw, AlertCircle, ChevronDown, ChevronUp,
  CheckCircle, XCircle, BarChart3, Layers
} from 'lucide-react'

const API = import.meta.env.VITE_API_BASE_URL ?? ''

interface SimulatorMeta {
  id: string
  name: string
  description?: string
  category?: string
  parameters?: ParameterDef[]
}

interface ParameterDef {
  name: string
  type: string
  default?: unknown
  description?: string
  min?: number
  max?: number
  options?: string[]
}

interface SimRunResult {
  run_id: string
  simulator_id: string
  simulator_name: string
  status: string
  outputs: Record<string, unknown>
  metrics: Record<string, number>
  charts?: Record<string, unknown[]>
  error?: string
  execution_time_ms: number
}

function ParamInput({
  param,
  value,
  onChange,
}: {
  param: ParameterDef
  value: unknown
  onChange: (v: unknown) => void
}) {
  if (param.options && param.options.length > 0) {
    return (
      <select
        value={String(value ?? param.default ?? '')}
        onChange={e => onChange(e.target.value)}
        className="w-full border rounded-lg px-3 py-2 text-sm"
      >
        {param.options.map(o => (
          <option key={o} value={o}>{o}</option>
        ))}
      </select>
    )
  }
  if (param.type === 'boolean') {
    return (
      <select
        value={value ? 'true' : 'false'}
        onChange={e => onChange(e.target.value === 'true')}
        className="w-full border rounded-lg px-3 py-2 text-sm"
      >
        <option value="true">بله</option>
        <option value="false">خیر</option>
      </select>
    )
  }
  return (
    <input
      type={param.type === 'integer' || param.type === 'number' ? 'number' : 'text'}
      step={param.type === 'number' ? '0.1' : undefined}
      min={param.min}
      max={param.max}
      value={String(value ?? param.default ?? '')}
      onChange={e =>
        onChange(param.type === 'integer' ? parseInt(e.target.value) :
          param.type === 'number' ? parseFloat(e.target.value) : e.target.value)
      }
      className="w-full border rounded-lg px-3 py-2 text-sm"
    />
  )
}

function MetricsPanel({ metrics }: { metrics: Record<string, number> }) {
  const entries = Object.entries(metrics)
  if (entries.length === 0) return null
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-4">
      {entries.map(([k, v]) => (
        <div key={k} className="bg-muted/40 rounded-lg p-3 text-center">
          <p className="text-xs text-muted-foreground mb-1 font-mono">{k}</p>
          <p className="text-lg font-bold">{typeof v === 'number' ? v.toFixed(3) : String(v)}</p>
        </div>
      ))}
    </div>
  )
}

function OutputsPanel({ outputs }: { outputs: Record<string, unknown> }) {
  const [open, setOpen] = useState(false)
  const entries = Object.entries(outputs)
  if (entries.length === 0) return null
  return (
    <div className="mt-4">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
      >
        {open ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        مشاهده خروجی‌های کامل ({entries.length} فیلد)
      </button>
      {open && (
        <pre className="mt-2 bg-muted/30 rounded-lg p-4 text-xs overflow-auto max-h-64 font-mono text-left" dir="ltr">
          {JSON.stringify(outputs, null, 2)}
        </pre>
      )}
    </div>
  )
}

export default function SimulationPage() {
  const [simulators, setSimulators] = useState<SimulatorMeta[]>([])
  const [selected, setSelected] = useState<SimulatorMeta | null>(null)
  const [params, setParams] = useState<Record<string, unknown>>({})
  const [result, setResult] = useState<SimRunResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [loadingSims, setLoadingSims] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState('')

  useEffect(() => {
    fetchSimulators()
  }, [])

  async function fetchSimulators() {
    setLoadingSims(true)
    try {
      const r = await fetch(`${API}/api/v1/simulators?lang=fa`)
      if (r.ok) {
        const data = await r.json()
        setSimulators(data.simulators ?? [])
      }
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoadingSims(false)
    }
  }

  async function loadSimulatorDetail(id: string) {
    try {
      const r = await fetch(`${API}/api/v1/simulators/${id}?lang=fa`)
      if (r.ok) {
        const data = await r.json()
        setSelected(data)
        // Initialize params with defaults
        const defaults: Record<string, unknown> = {}
        for (const p of data.parameters ?? []) {
          defaults[p.name] = p.default ?? ''
        }
        setParams(defaults)
        setResult(null)
        setError(null)
      }
    } catch (e: any) {
      setError(e.message)
    }
  }

  async function runSimulation() {
    if (!selected) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const resp = await fetch(`${API}/api/v1/simulators/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ simulator_id: selected.id, parameters: params }),
      })
      const data = await resp.json()
      if (!resp.ok) throw new Error(data.detail ?? JSON.stringify(data))
      setResult(data)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const filteredSims = simulators.filter(
    s =>
      s.id.includes(filter.toLowerCase()) ||
      (s.name ?? '').includes(filter) ||
      (s.category ?? '').includes(filter.toLowerCase()),
  )

  const categories = [...new Set(simulators.map(s => s.category ?? 'سایر'))]

  return (
    <div className="space-y-6" dir="rtl">
      {/* Header */}
      <div className="flex items-center gap-3">
        <FlaskConical className="w-7 h-7 text-violet-600" />
        <div>
          <h1 className="text-2xl font-bold">مدل‌های شبیه‌سازی</h1>
          <p className="text-muted-foreground text-sm">
            AquaCrop · RothC · SWAT+ · Climate · ARIES · InVEST · مدل‌های کربن و آب
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Simulator list */}
        <div className="lg:col-span-1 space-y-3">
          <div className="bg-card border rounded-xl p-4">
            <input
              placeholder="جستجوی مدل..."
              value={filter}
              onChange={e => setFilter(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm mb-3"
            />
            {loadingSims ? (
              <div className="flex items-center justify-center py-8">
                <RefreshCw className="w-5 h-5 animate-spin text-muted-foreground" />
              </div>
            ) : (
              <div className="space-y-4 max-h-[60vh] overflow-y-auto">
                {categories.map(cat => {
                  const inCat = filteredSims.filter(s => (s.category ?? 'سایر') === cat)
                  if (inCat.length === 0) return null
                  return (
                    <div key={cat}>
                      <p className="text-xs font-semibold text-muted-foreground uppercase mb-2 flex items-center gap-1">
                        <Layers className="w-3 h-3" /> {cat}
                      </p>
                      {inCat.map(sim => (
                        <button
                          key={sim.id}
                          onClick={() => loadSimulatorDetail(sim.id)}
                          className={`w-full text-right rounded-lg px-3 py-2 text-sm mb-1 transition-colors ${
                            selected?.id === sim.id
                              ? 'bg-violet-100 text-violet-800 font-medium'
                              : 'hover:bg-muted/40 text-foreground'
                          }`}
                        >
                          {sim.name ?? sim.id}
                        </button>
                      ))}
                    </div>
                  )
                })}
                {filteredSims.length === 0 && (
                  <p className="text-center text-muted-foreground text-sm py-4">
                    مدلی یافت نشد
                  </p>
                )}
              </div>
            )}
          </div>
          <div className="bg-muted/30 rounded-xl p-3 text-center">
            <p className="text-xs text-muted-foreground">{simulators.length} مدل شبیه‌سازی</p>
          </div>
        </div>

        {/* Simulator runner */}
        <div className="lg:col-span-2 space-y-4">
          {!selected ? (
            <div className="bg-card border rounded-xl flex items-center justify-center min-h-64">
              <div className="text-center text-muted-foreground">
                <FlaskConical className="w-10 h-10 mx-auto mb-2 opacity-30" />
                <p className="text-sm">یک مدل از سمت چپ انتخاب کنید</p>
              </div>
            </div>
          ) : (
            <div className="bg-card border rounded-xl p-5">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-lg font-bold">{selected.name ?? selected.id}</h2>
                  {selected.description && (
                    <p className="text-muted-foreground text-sm mt-1">{selected.description}</p>
                  )}
                </div>
                <span className="text-xs bg-violet-100 text-violet-700 px-2 py-1 rounded-full">
                  {selected.category ?? 'simulation'}
                </span>
              </div>

              {/* Parameters */}
              {(selected.parameters ?? []).length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
                  {(selected.parameters ?? []).map(p => (
                    <div key={p.name}>
                      <label className="text-xs text-muted-foreground block mb-1">
                        {p.description ?? p.name}
                        {p.min !== undefined && p.max !== undefined && (
                          <span className="mr-1 text-gray-400">({p.min}–{p.max})</span>
                        )}
                      </label>
                      <ParamInput
                        param={p}
                        value={params[p.name]}
                        onChange={v => setParams(prev => ({ ...prev, [p.name]: v }))}
                      />
                    </div>
                  ))}
                </div>
              )}

              <button
                onClick={runSimulation}
                disabled={loading}
                className="flex items-center gap-2 bg-violet-600 text-white rounded-lg px-5 py-2.5 text-sm font-medium hover:bg-violet-700 disabled:opacity-50"
              >
                {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                اجرای شبیه‌سازی
              </button>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm flex items-center gap-2">
              <AlertCircle className="w-4 h-4" /> {error}
            </div>
          )}

          {/* Result */}
          {result && (
            <div className="bg-card border rounded-xl p-5">
              <div className="flex items-center gap-2 mb-2">
                {result.status === 'completed' || result.status === 'COMPLETED' ? (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-500" />
                )}
                <h3 className="font-semibold">نتیجه: {result.simulator_name}</h3>
                <span className="text-xs text-muted-foreground mr-auto">
                  {result.execution_time_ms?.toFixed(0)} ms
                </span>
              </div>
              {result.error && (
                <p className="text-red-600 text-sm mb-2">{result.error}</p>
              )}
              <MetricsPanel metrics={result.metrics ?? {}} />
              <OutputsPanel outputs={result.outputs ?? {}} />
              {/* Chart data hint */}
              {result.charts && Object.keys(result.charts).length > 0 && (
                <div className="mt-3 flex items-center gap-2 text-sm text-muted-foreground">
                  <BarChart3 className="w-4 h-4" />
                  {Object.keys(result.charts).length} نمودار در خروجی موجود است
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
