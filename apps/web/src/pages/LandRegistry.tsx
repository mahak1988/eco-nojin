import { useState } from 'react'
import { Plus, Search, Edit2, Trash2, Eye, ChevronLeft, ChevronRight as ChevronRightIcon } from 'lucide-react'
import { Header } from '../components/Layout/Header'
import { TypographicLogo } from '../components/common/TypographicLogo'
import { fields } from '../lib/data'

const STATUS_BADGE: Record<string, string> = {
  Growing: 'badge-green',
  'Harvest Ready': 'badge-yellow',
  Planted: 'badge-blue',
  Fallow: 'badge-gray',
  Harvested: 'badge-gray',
}

export default function LandRegistry() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('All Status')
  const [villageFilter, setVillageFilter] = useState('All Villages')

  const filtered = fields.filter(f => {
    const matchSearch = f.id.toLowerCase().includes(search.toLowerCase()) ||
      f.location.toLowerCase().includes(search.toLowerCase()) ||
      f.owner.toLowerCase().includes(search.toLowerCase())
    const matchStatus = statusFilter === 'All Status' || f.status === statusFilter
    const matchVillage = villageFilter === 'All Villages' || f.location === villageFilter
    return matchSearch && matchStatus && matchVillage
  })

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <header className="flex items-center justify-between border-b border-gray-100 bg-white/80 px-6 py-4 backdrop-blur-sm dark:border-gray-800 dark:bg-gray-900/80">
        <div className="flex items-center gap-4">
          <TypographicLogo size="md" />
          <div>
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">Land Registry</h1>
            <p className="text-sm text-gray-600 dark:text-gray-400">Manage agricultural land data</p>
          </div>
        </div>
      </header>
      <div className="flex-1 overflow-y-auto p-5">
        <div className="card overflow-hidden">
          {/* Toolbar */}
          <div className="flex items-center justify-between px-5 py-3.5 border-b border-gray-100 dark:border-gray-800">
            <div className="flex items-center gap-2 flex-wrap">
              <div className="relative">
                <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400" />
                <input
                  placeholder="Search fields..."
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  className="pl-8 pr-3 py-2 text-xs bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl w-44 focus:outline-none focus:ring-2 focus:ring-green-500/20 focus:border-green-400 text-gray-700 dark:text-gray-300 placeholder-gray-400 transition-all"
                />
              </div>
              {[
                { value: statusFilter, onChange: setStatusFilter, options: ['All Status', 'Growing', 'Harvest Ready', 'Planted', 'Fallow'] },
                { value: villageFilter, onChange: setVillageFilter, options: ['All Villages', 'Desa Karangampel', 'Desa Leles', 'Desa Patrol', 'Desa Bonges', 'Desa Tarangkerta'] },
                { value: 'All Varieties', onChange: () => {}, options: ['All Varieties', 'Inpari 32', 'Ciherang', 'Mekongga', 'IR64'] },
              ].map((sel, i) => (
                <select key={i} value={sel.value} onChange={e => sel.onChange(e.target.value)}
                  className="py-2 px-3 text-xs bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-600 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-green-500/20 focus:border-green-400 transition-all">
                  {sel.options.map(o => <option key={o}>{o}</option>)}
                </select>
              ))}
            </div>
            <button className="btn-primary flex items-center gap-1.5 text-xs py-2">
              <Plus className="w-3.5 h-3.5" /> Add New Field
            </button>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-100 dark:border-gray-800 bg-gray-50/60 dark:bg-gray-800/30">
                  {['Field ID', 'Location', 'Area (ha)', 'Owner', 'Crop Variety', 'Status', 'Action'].map(h => (
                    <th key={h} className="text-left text-[11px] font-semibold text-gray-400 dark:text-gray-500 px-5 py-3 uppercase tracking-wide whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filtered.map(f => (
                  <tr key={f.id} className="border-b border-gray-50 dark:border-gray-800/50 hover:bg-gray-50/60 dark:hover:bg-gray-800/30 transition-colors">
                    <td className="px-5 py-3.5">
                      <span className="text-xs font-semibold text-green-700 dark:text-green-400">{f.id}</span>
                    </td>
                    <td className="px-5 py-3.5 text-sm text-gray-700 dark:text-gray-300">{f.location}</td>
                    <td className="px-5 py-3.5 text-sm text-gray-700 dark:text-gray-300 font-medium">{f.area}</td>
                    <td className="px-5 py-3.5 text-sm text-gray-700 dark:text-gray-300">{f.owner}</td>
                    <td className="px-5 py-3.5 text-sm text-gray-700 dark:text-gray-300">{f.variety}</td>
                    <td className="px-5 py-3.5">
                      <span className={`badge ${STATUS_BADGE[f.status] || 'badge-gray'}`}>{f.status}</span>
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-0.5">
                        <button className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"><Eye className="w-3.5 h-3.5" /></button>
                        <button className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"><Edit2 className="w-3.5 h-3.5" /></button>
                        <button className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors text-gray-400 hover:text-red-500"><Trash2 className="w-3.5 h-3.5" /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between px-5 py-3 border-t border-gray-100 dark:border-gray-800">
            <p className="text-xs text-gray-400 dark:text-gray-500">Showing 1 to {filtered.length} of 1,248 entries</p>
            <div className="flex items-center gap-1">
              <button className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-400 transition-colors"><ChevronLeft className="w-3.5 h-3.5" /></button>
              {[1, 2, 3, '...', 200].map((p, i) => (
                <button key={i} className={`w-7 h-7 flex items-center justify-center rounded-lg text-xs font-medium transition-colors ${p === 1 ? 'bg-green-700 text-white' : 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'}`}>
                  {p}
                </button>
              ))}
              <button className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-400 transition-colors"><ChevronRightIcon className="w-3.5 h-3.5" /></button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
