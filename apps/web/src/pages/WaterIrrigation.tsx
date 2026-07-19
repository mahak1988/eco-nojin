import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import Header from '../components/Header'
import { irrigationData, waterUsageTrend } from '../lib/data'
import { formatNumber, formatCurrency } from '../lib/utils'

export default function WaterIrrigation() {
  return (
    <div className="flex flex-col h-full overflow-hidden">
      <Header title="Water & Irrigation" subtitle="Track water consumption, irrigation sources, and costs" />
      <div className="flex-1 overflow-y-auto p-6 space-y-6">

        <div className="grid grid-cols-4 gap-4">
          {[
            { label: 'Total Water Usage', value: '1,250,000 m³', sub: '+5.2% from last season' },
            { label: 'Active Pumps', value: '24', sub: '3 under maintenance' },
            { label: 'Electricity Cost', value: 'Rp 62.5M', sub: 'This season' },
            { label: 'Water Efficiency', value: '94.2%', sub: 'Excellent' },
          ].map(({ label, value, sub }) => (
            <div key={label} className="card p-4">
              <p className="text-xs text-gray-500 dark:text-gray-400">{label}</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{value}</p>
              <p className="text-xs text-gray-400 mt-0.5">{sub}</p>
            </div>
          ))}
        </div>

        <div className="card p-5">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">Monthly Water Usage (m³)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={waterUsageTrend}>
              <defs>
                <linearGradient id="gwater" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false} />
              <XAxis dataKey="month" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v: number) => `${(v / 1000000).toFixed(1)}M`} />
              <Tooltip formatter={(v) => formatNumber(Number(v)) + ' m³'} contentStyle={{ borderRadius: 12, border: 'none', fontSize: 12 }} />
              <Area type="monotone" dataKey="usage" stroke="#0ea5e9" strokeWidth={2} fill="url(#gwater)" dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="card overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100 dark:border-gray-800">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Irrigation Records</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-100 dark:border-gray-800">
                  {['Field ID', 'Irrigation Source', 'Pump', 'Water Req. (m³)', 'Water Used (m³)', 'Electric Cost', 'Efficiency'].map(h => (
                    <th key={h} className="text-left text-xs font-semibold text-gray-500 dark:text-gray-400 px-5 py-3 uppercase tracking-wide whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {irrigationData.map(r => (
                  <tr key={r.id} className="border-b border-gray-50 dark:border-gray-800/50 hover:bg-gray-50/50 dark:hover:bg-gray-800/30">
                    <td className="px-5 py-3 text-sm font-medium text-green-700 dark:text-green-400">{r.fieldId}</td>
                    <td className="px-5 py-3 text-sm text-gray-700 dark:text-gray-300">{r.source}</td>
                    <td className="px-5 py-3 text-sm text-gray-600 dark:text-gray-400">{r.pump}</td>
                    <td className="px-5 py-3 text-sm text-gray-700 dark:text-gray-300">{formatNumber(r.waterReq)}</td>
                    <td className="px-5 py-3 text-sm text-gray-700 dark:text-gray-300">{formatNumber(r.waterUsed)}</td>
                    <td className="px-5 py-3 text-sm font-medium text-gray-800 dark:text-gray-200">{formatCurrency(r.electricCost)}</td>
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full">
                          <div className="h-full bg-cyan-500 rounded-full" style={{ width: `${r.efficiency}%` }} />
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
