import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, Legend } from 'recharts'
import Header from '../components/Header'
import { fertilizerRecords, fertilizerTrend } from '../lib/data'
import { formatCurrency } from '../lib/utils'

export default function FertilizerManagement() {
  return (
    <div className="flex flex-col h-full overflow-hidden">
      <Header title="Fertilizer Management" subtitle="Track fertilizer usage, planning, and cost analysis" />
      <div className="flex-1 overflow-y-auto p-6 space-y-6">

        <div className="grid grid-cols-4 gap-4">
          {[
            { label: 'Total Fertilizer Used', value: '2,345 ton', sub: 'This season' },
            { label: 'Urea', value: '1,180 ton', sub: '50.3% of total' },
            { label: 'NPK', value: '720 ton', sub: '30.7% of total' },
            { label: 'Avg. Cost / Ha', value: 'Rp 1,250,000', sub: 'Per hectare' },
          ].map(({ label, value, sub }) => (
            <div key={label} className="card p-4">
              <p className="text-xs text-gray-500 dark:text-gray-400">{label}</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{value}</p>
              <p className="text-xs text-gray-400 mt-0.5">{sub}</p>
            </div>
          ))}
        </div>

        <div className="card p-5">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">Monthly Fertilizer Consumption (ton)</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={fertilizerTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false} />
              <XAxis dataKey="month" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ borderRadius: 12, border: 'none', fontSize: 12 }} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey="urea" name="Urea" fill="#16a34a" radius={[4, 4, 0, 0]} stackId="a" />
              <Bar dataKey="npk" name="NPK" fill="#4ade80" radius={[0, 0, 0, 0]} stackId="a" />
              <Bar dataKey="organic" name="Organic" fill="#bbf7d0" radius={[4, 4, 0, 0]} stackId="a" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100 dark:border-gray-800">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Fertilizer Usage Records</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-100 dark:border-gray-800">
                  {['Field ID', 'Owner', 'Village', 'Urea (kg)', 'NPK (kg)', 'Organic (kg)', 'Total Cost', 'Cost/Ha', 'Efficiency'].map(h => (
                    <th key={h} className="text-left text-xs font-semibold text-gray-500 dark:text-gray-400 px-5 py-3 uppercase tracking-wide whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {fertilizerRecords.map(r => (
                  <tr key={r.id} className="border-b border-gray-50 dark:border-gray-800/50 hover:bg-gray-50/50 dark:hover:bg-gray-800/30">
                    <td className="px-5 py-3 text-sm font-medium text-green-700 dark:text-green-400">{r.fieldId}</td>
                    <td className="px-5 py-3 text-sm text-gray-700 dark:text-gray-300">{r.owner}</td>
                    <td className="px-5 py-3 text-sm text-gray-600 dark:text-gray-400">{r.village}</td>
                    <td className="px-5 py-3 text-sm text-gray-700 dark:text-gray-300">{r.urea}</td>
                    <td className="px-5 py-3 text-sm text-gray-700 dark:text-gray-300">{r.npk}</td>
                    <td className="px-5 py-3 text-sm text-gray-700 dark:text-gray-300">{r.organic}</td>
                    <td className="px-5 py-3 text-sm font-medium text-gray-800 dark:text-gray-200">{formatCurrency(r.totalCost)}</td>
                    <td className="px-5 py-3 text-sm text-gray-700 dark:text-gray-300">{formatCurrency(r.costPerHa)}</td>
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full">
                          <div className="h-full bg-green-500 rounded-full" style={{ width: `${r.efficiency}%` }} />
                        </div>
                        <span className="text-xs font-medium text-gray-700 dark:text-gray-300">{r.efficiency}%</span>
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
