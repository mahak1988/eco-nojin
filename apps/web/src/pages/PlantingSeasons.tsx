import { useState } from 'react'
import { Plus, ChevronDown } from 'lucide-react'
import Header from '../components/Header'
import { plantingSeasons } from '../lib/data'

const STATUS_COLORS: Record<string, string> = {
  Growing: 'badge-green',
  'Harvest Ready': 'badge-yellow',
  Planted: 'badge-blue',
  Harvested: 'badge-gray',
  Planned: 'badge-gray',
}

// Gantt bar config: each phase occupies certain month columns
// Month columns: Feb(0), Mar(1), Apr(2), May(3), Jun(4), Jul(5), Aug(6), Sep(7)
const MONTHS = ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']

type Phase = { label: string; color: string; start: number; span: number }

function getPhases(status: string, plantDate: string): Phase[] {
  const plantMonth = plantDate.includes('Mar') ? 1 : plantDate.includes('Feb') ? 0 : 1
  const phases: Phase[] = [
    { label: 'Planting', color: '#3b82f6', start: plantMonth, span: 1 },
    { label: 'Growing', color: '#22c55e', start: plantMonth + 1, span: 3 },
  ]
  if (status === 'Harvest Ready' || status === 'Harvested') {
    phases.push({ label: status === 'Harvested' ? 'Harvested' : 'Harvest Ready', color: status === 'Harvested' ? '#9ca3af' : '#eab308', start: plantMonth + 4, span: 1 })
  }
  return phases
}

export default function PlantingSeasons() {
  const [view, setView] = useState<'gantt' | 'table'>('gantt')

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <Header title="Planting Seasons" subtitle="Track planting schedules and crop growth" />
      <div className="flex-1 overflow-y-auto p-5 space-y-4">

        {/* Stats */}
        <div className="grid grid-cols-4 gap-3">
          {[
            { label: 'Total Plots This Season', value: '4,782' },
            { label: 'Currently Growing', value: '3,201' },
            { label: 'Harvest Ready', value: '892' },
            { label: 'Avg. Growth Duration', value: '128 days' },
          ].map(({ label, value }) => (
            <div key={label} className="card p-4">
              <p className="text-xs text-gray-500 dark:text-gray-400">{label}</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{value}</p>
            </div>
          ))}
        </div>

        {/* Gantt Card */}
        <div className="card overflow-hidden">
          {/* Toolbar */}
          <div className="flex items-center justify-between px-5 py-3 border-b border-gray-100 dark:border-gray-800">
            <div className="flex items-center gap-2">
              <button className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                Season A 2025 <ChevronDown className="w-3 h-3" />
              </button>
              <div className="flex gap-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-0.5">
                {(['gantt', 'table'] as const).map(v => (
                  <button key={v} onClick={() => setView(v)} className={`px-3 py-1 rounded-md text-xs font-medium capitalize transition-colors ${view === v ? 'bg-white dark:bg-gray-900 text-gray-900 dark:text-white shadow-sm' : 'text-gray-500 dark:text-gray-400'}`}>{v}</button>
                ))}
              </div>
            </div>
            <button className="btn-primary flex items-center gap-1.5 text-xs py-1.5">
              <Plus className="w-3.5 h-3.5" /> Add Season Record
            </button>
          </div>

          {view === 'gantt' ? (
            <div className="overflow-x-auto">
              <div style={{ minWidth: 860 }}>
                {/* Month header */}
                <div className="flex border-b border-gray-100 dark:border-gray-800 bg-gray-50/60 dark:bg-gray-800/40">
                  <div className="w-64 shrink-0 px-5 py-2.5 text-xs font-semibold text-gray-400 uppercase tracking-wide">Field / Owner</div>
                  <div className="flex-1 grid" style={{ gridTemplateColumns: `repeat(${MONTHS.length}, 1fr)` }}>
                    {MONTHS.map(m => (
                      <div key={m} className="text-center py-2.5 text-xs font-semibold text-gray-400 uppercase tracking-wide border-l border-gray-100 dark:border-gray-800 first:border-l-0">{m}</div>
                    ))}
                  </div>
                </div>

                {plantingSeasons.map(ps => {
                  const phases = getPhases(ps.status, ps.plantDate)
                  return (
                    <div key={ps.id} className="flex border-b border-gray-50 dark:border-gray-800/50 hover:bg-gray-50/40 dark:hover:bg-gray-800/20 transition-colors items-center">
                      {/* Left info */}
                      <div className="w-64 shrink-0 px-5 py-3">
                        <p className="text-xs font-semibold text-green-700 dark:text-green-400">{ps.fieldId}</p>
                        <p className="text-sm font-medium text-gray-800 dark:text-gray-200">{ps.owner}</p>
                        <p className="text-[11px] text-gray-400">{ps.village} &middot; {ps.variety} &middot; {ps.area} ha</p>
                      </div>

                      {/* Gantt bars */}
                      <div className="flex-1 relative py-3 pr-4" style={{ height: 52 }}>
                        <div className="relative h-full flex items-center">
                          {/* grid lines */}
                          <div className="absolute inset-0 grid" style={{ gridTemplateColumns: `repeat(${MONTHS.length}, 1fr)` }}>
                            {MONTHS.map((_, i) => <div key={i} className={`border-l border-gray-100 dark:border-gray-800 h-full ${i === 0 ? 'border-l-0' : ''}`} />)}
                          </div>
                          {/* bars */}
                          <div className="absolute inset-x-0 h-7" style={{ display: 'grid', gridTemplateColumns: `repeat(${MONTHS.length}, 1fr)` }}>
                            {phases.map((ph, pi) => {
                              const left = (ph.start / MONTHS.length) * 100
                              const width = (ph.span / MONTHS.length) * 100
                              return (
                                <div
                                  key={pi}
                                  className="absolute h-full rounded-md flex items-center justify-center text-white text-[10px] font-semibold overflow-hidden"
                                  style={{
                                    left: `${left}%`,
                                    width: `${width}%`,
                                    background: ph.color,
                                    opacity: 0.9,
                                  }}
                                >
                                  {ph.span > 0.5 && <span className="px-1 truncate">{ph.label}</span>}
                                </div>
                              )
                            })}
                          </div>
                        </div>
                      </div>

                      {/* Status badge */}
                      <div className="w-28 shrink-0 px-3 py-3 text-right">
                        <span className={`badge text-[10px] ${STATUS_COLORS[ps.status] || 'badge-gray'}`}>{ps.status}</span>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-100 dark:border-gray-800 bg-gray-50/60 dark:bg-gray-800/30">
                    {['Field ID', 'Owner', 'Village', 'Variety', 'Area', 'Plant Date', 'Harvest Date', 'Progress', 'Status'].map(h => (
                      <th key={h} className="text-left text-xs font-semibold text-gray-400 px-5 py-3 uppercase tracking-wide">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {plantingSeasons.map(ps => (
                    <tr key={ps.id} className="border-b border-gray-50 dark:border-gray-800/50 hover:bg-gray-50/50 dark:hover:bg-gray-800/30">
                      <td className="px-5 py-3 text-xs font-semibold text-green-700 dark:text-green-400">{ps.fieldId}</td>
                      <td className="px-5 py-3 text-sm text-gray-700 dark:text-gray-300">{ps.owner}</td>
                      <td className="px-5 py-3 text-xs text-gray-500 dark:text-gray-400">{ps.village}</td>
                      <td className="px-5 py-3 text-sm text-gray-700 dark:text-gray-300">{ps.variety}</td>
                      <td className="px-5 py-3 text-sm text-gray-700 dark:text-gray-300">{ps.area} ha</td>
                      <td className="px-5 py-3 text-xs text-gray-500 dark:text-gray-400">{ps.plantDate}</td>
                      <td className="px-5 py-3 text-xs text-gray-500 dark:text-gray-400">{ps.harvestDate}</td>
                      <td className="px-5 py-3">
                        <div className="flex items-center gap-2">
                          <div className="w-20 h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                            <div className="h-full bg-green-500 rounded-full" style={{ width: `${ps.progress}%` }} />
                          </div>
                          <span className="text-xs text-gray-500 dark:text-gray-400">{ps.progress}%</span>
                        </div>
                      </td>
                      <td className="px-5 py-3">
                        <span className={`badge ${STATUS_COLORS[ps.status] || 'badge-gray'}`}>{ps.status}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
