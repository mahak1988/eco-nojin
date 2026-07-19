import { useState } from 'react'
import { Plus, Search, Eye, Edit2, Phone, MapPin } from 'lucide-react'
import Header from '../components/Header'
import { farmers } from '../lib/data'

export default function Farmers() {
  const [search, setSearch] = useState('')
  const filtered = farmers.filter(f =>
    f.name.toLowerCase().includes(search.toLowerCase()) ||
    f.village.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <Header title="Farmers" subtitle="Manage farmer profiles and land ownership" />
      <div className="flex-1 overflow-y-auto p-6 space-y-6">

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4">
          {[
            { label: 'Total Farmers', value: '4,782' },
            { label: 'Active Farmers', value: '4,620' },
            { label: 'Avg. Area / Farmer', value: '2.62 ha' },
            { label: 'Farmer Groups', value: '48' },
          ].map(({ label, value }) => (
            <div key={label} className="card p-4">
              <p className="text-xs text-gray-500 dark:text-gray-400">{label}</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{value}</p>
            </div>
          ))}
        </div>

        {/* Farmer Grid */}
        <div className="card overflow-hidden">
          <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100 dark:border-gray-800">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400" />
              <input
                placeholder="Search farmers..."
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="pl-8 pr-3 py-1.5 text-sm bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl w-56 focus:outline-none focus:ring-2 focus:ring-green-500/30 text-gray-700 dark:text-gray-300 placeholder-gray-400"
              />
            </div>
            <button className="btn-primary flex items-center gap-1.5">
              <Plus className="w-3.5 h-3.5" /> Add Farmer
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-100 dark:border-gray-800">
                  {['Farmer ID', 'Name', 'NIK', 'Contact', 'Village', 'Fields', 'Total Area', 'Status', 'Action'].map(h => (
                    <th key={h} className="text-left text-xs font-semibold text-gray-500 dark:text-gray-400 px-5 py-3 uppercase tracking-wide">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filtered.map(f => (
                  <tr key={f.id} className="border-b border-gray-50 dark:border-gray-800/50 hover:bg-gray-50/50 dark:hover:bg-gray-800/30 transition-colors">
                    <td className="px-5 py-3 text-sm font-medium text-green-700 dark:text-green-400">{f.id}</td>
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-2.5">
                        <div className="w-7 h-7 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center text-xs font-semibold text-green-700 dark:text-green-400">
                          {f.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                        </div>
                        <span className="text-sm font-medium text-gray-800 dark:text-gray-200">{f.name}</span>
                      </div>
                    </td>
                    <td className="px-5 py-3 text-sm text-gray-600 dark:text-gray-400 font-mono text-xs">{f.nik}</td>
                    <td className="px-5 py-3 text-sm text-gray-600 dark:text-gray-400">
                      <div className="flex items-center gap-1"><Phone className="w-3 h-3" />{f.phone}</div>
                    </td>
                    <td className="px-5 py-3 text-sm text-gray-600 dark:text-gray-400">
                      <div className="flex items-center gap-1"><MapPin className="w-3 h-3" />{f.village}</div>
                    </td>
                    <td className="px-5 py-3 text-sm text-gray-700 dark:text-gray-300">{f.fields}</td>
                    <td className="px-5 py-3 text-sm text-gray-700 dark:text-gray-300">{f.area} ha</td>
                    <td className="px-5 py-3">
                      <span className={`badge ${f.status === 'Active' ? 'badge-green' : 'badge-gray'}`}>{f.status}</span>
                    </td>
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-1">
                        <button className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500"><Eye className="w-3.5 h-3.5" /></button>
                        <button className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500"><Edit2 className="w-3.5 h-3.5" /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
