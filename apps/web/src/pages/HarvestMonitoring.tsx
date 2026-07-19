import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import Header from '../components/Header'
import { harvestRecords, yieldPerHectare, productionByVariety } from '../lib/data'
import { formatCurrency } from '../lib/utils'

export default function HarvestMonitoring() {
  return (
    <div className="flex flex-col h-full overflow-hidden">
      <Header title="Harvest Monitoring" subtitle="Track harvest records and production volume" />
      <div className="flex-1 overflow-y-auto p-6 space-y-6">

        <div className="grid grid-cols-4 gap-4">
          {[
            { label: 'Total Harvest This Season', value: '45,682 ton' },
            { label: 'Avg Yield / Ha', value: '6.2 ton' },
            { label: 'Total Revenue (Est.)', value: 'Rp 228.4B' },
            { label: 'Harvested Fields', value: '1,204' },
          ].map(({ label, value }) => (
            <div key={label} className="card p-4">
              <p className="text-xs text-gray-500 dark:text-gray-400">{label}</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{value}</p>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="card p-5">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">Harvest by Village (ton/ha)</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={yieldPerHectare}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false} />
                <XAxis dataKey="village" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ borderRadius: 12, border: 'none', fontSize: 12 }} />
                <Bar dataKey="yield" fill="#16a34a" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card p-5">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">Production by Variety (ton)</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={productionByVariety}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false} />
                <XAxis dataKey="variety" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => `${v / 1000}k`} />
                <Tooltip contentStyle={{ borderRadius: 12, border: 'none', fontSize: 12 }} />
                <Bar dataKey="ton" fill="#4ade80" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100 dark:border-gray-800">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Harvest Records</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-100 dark:border-gray-800">
                  {['Harvest ID', 'Field ID', 'Owner', 'Village', 'Variety', 'Area (ha)', 'Production (ton)', 'Yield (ton/ha)', 'Harvest Date', 'Revenue (Est.)'].map(h => (
                    <th key={h} className="text-left text-xs font-semibold text-gray-500 dark:text-gray-400 px-5 py-3 uppercase tracking-wide whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {harvestRecords.map(r => (
                  <tr key={r.id} className="border-b border-gray-50 dark:border-gray-800/50 hover:bg-gray-50/50 dark:hover:bg-gray-800/30">
                    <td className="px-5 py-3 text-sm font-medium text-green-700 dark:text-green-400">{r.id}</td>
                    <td className="px-5 py-3 text-sm text-gray-600 dark:text-gray-400">{r.fieldId}</td>
                    <td className="px-5 py-3 text-sm text-gray-700 dark:text-gray-300">{r.owner}</td>
                    <td className="px-5 py-3 text-sm text-gray-600 dark:text-gray-400">{r.village}</td>
                    <td className="px-5 py-3 text-sm text-gray-700 dark:text-gray-300">{r.variety}</td>
                    <td className="px-5 py-3 text-sm text-gray-700 dark:text-gray-300">{r.area}</td>
                    <td className="px-5 py-3 text-sm font-medium text-gray-800 dark:text-gray-200">{r.production}</td>
                    <td className="px-5 py-3 text-sm text-gray-700 dark:text-gray-300">{r.yield}</td>
                    <td className="px-5 py-3 text-sm text-gray-600 dark:text-gray-400">{r.date}</td>
                    <td className="px-5 py-3 text-sm font-medium text-green-700 dark:text-green-400">{formatCurrency(r.revenue)}</td>
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
