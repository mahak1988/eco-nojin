import {
  Bar, BarChart, CartesianGrid, Cell, Pie, PieChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis
} from 'recharts'
import { Download, ChevronDown, Users } from 'lucide-react'
import Header from '../components/Header'
import { yieldPerHectare, productionByVariety } from '../lib/data'
import { formatNumber } from '../lib/utils'

const donutColors = ['#16a34a', '#4ade80', '#86efac', '#bbf7d0', '#d1fae5']

const RADIAN = Math.PI / 180
const renderLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }: any) => {
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5
  const x = cx + radius * Math.cos(-midAngle * RADIAN)
  const y = cy + radius * Math.sin(-midAngle * RADIAN)
  if (percent < 0.06) return null
  return <text x={x} y={y} fill="white" textAnchor="middle" dominantBaseline="central" fontSize={10} fontWeight={600}>{(percent * 100).toFixed(0)}%</text>
}

const villageRanking = [
  { village: 'Karangampel', yield: 7.2, production: 12480, roi: 32.1 },
  { village: 'Leles', yield: 6.8, production: 10920, roi: 28.7 },
  { village: 'Patrol', yield: 6.1, production: 8540, roi: 26.3 },
  { village: 'Bonges', yield: 5.6, production: 7280, roi: 24.1 },
  { village: 'Kandanghaur', yield: 4.9, production: 6460, roi: 20.8 },
]

export default function ProductionAnalytics() {
  return (
    <div className="flex flex-col h-full overflow-hidden">
      <Header title="Production Analytics" subtitle="Analyze production and productivity performance" />
      <div className="flex-1 overflow-y-auto p-5 space-y-4">

        {/* KPI Row */}
        <div className="grid grid-cols-4 gap-3">
          {[
            { label: 'Total Production', value: '45,682 ton', delta: '+8.45%', up: true },
            { label: 'Avg Yield / Ha', value: '6.2 ton', delta: '+0.8', up: true },
            { label: 'Total Cost / Ha', value: 'Rp 5.4M', delta: '-2.1%', up: false },
            { label: 'ROI', value: '28.7%', delta: '+3.2%', up: true },
          ].map(({ label, value, delta, up }) => (
            <div key={label} className="card p-4">
              <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">{label}</p>
              <div className="flex items-end justify-between mt-1">
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-lg ${up ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400'}`}>{delta}</span>
              </div>
              <p className="text-[10px] text-gray-400 mt-1">vs last season</p>
            </div>
          ))}
        </div>

        {/* Charts */}
        <div className="grid grid-cols-5 gap-3">
          {/* Yield per Hectare Bar */}
          <div className="card p-4 col-span-3">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Yield per Hectare (ton)</h3>
              <div className="flex items-center gap-2">
                <button className="flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-600 dark:text-gray-300">
                  All Villages <ChevronDown className="w-3 h-3" />
                </button>
                <button className="flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-600 dark:text-gray-300">
                  <Users className="w-3 h-3" /> Export <ChevronDown className="w-3 h-3" />
                </button>
              </div>
            </div>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={yieldPerHectare} margin={{ top: 0, right: 4, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false} />
                <XAxis dataKey="village" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11 }} axisLine={false} tickLine={false} domain={[0, 8]} />
                <Tooltip contentStyle={{ borderRadius: 10, border: 'none', fontSize: 11, boxShadow: '0 4px 12px rgba(0,0,0,0.08)' }} />
                <Bar dataKey="yield" radius={[6, 6, 0, 0]}>
                  {yieldPerHectare.map((_, i) => (
                    <Cell key={i} fill={`hsl(${140 - i * 12}, 65%, ${40 + i * 5}%)`} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Production by Variety Donut */}
          <div className="card p-4 col-span-2">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">Production by Variety (ton)</h3>
            <ResponsiveContainer width="100%" height={150}>
              <PieChart>
                <Pie data={productionByVariety} cx="50%" cy="50%" innerRadius={44} outerRadius={65} dataKey="ton" paddingAngle={2} labelLine={false} label={renderLabel}>
                  {productionByVariety.map((_, i) => <Cell key={i} fill={donutColors[i % donutColors.length]} />)}
                </Pie>
                <g>
                  <text x="50%" y="46%" textAnchor="middle" dominantBaseline="middle" fill="#111827" fontSize={13} fontWeight={700}>45,682</text>
                  <text x="50%" y="57%" textAnchor="middle" dominantBaseline="middle" fill="#9ca3af" fontSize={9}>ton</text>
                </g>
                <Tooltip formatter={(v) => formatNumber(Number(v)) + ' ton'} contentStyle={{ borderRadius: 10, border: 'none', fontSize: 11 }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-2 space-y-1.5">
              {productionByVariety.map(({ variety, ton }, i) => (
                <div key={variety} className="flex items-center justify-between text-xs">
                  <span className="flex items-center gap-1.5 text-gray-500 dark:text-gray-400">
                    <span className="w-2 h-2 rounded-sm shrink-0" style={{ background: donutColors[i] }} />{variety}
                  </span>
                  <span className="font-semibold text-gray-700 dark:text-gray-300">{formatNumber(ton)} <span className="font-normal text-gray-400 text-[10px]">({((ton / 45682) * 100).toFixed(1)}%)</span></span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Village Ranking */}
        <div className="card overflow-hidden">
          <div className="flex items-center justify-between px-5 py-3.5 border-b border-gray-100 dark:border-gray-800">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Village Productivity Ranking</h3>
            <button className="flex items-center gap-1.5 text-xs font-medium text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors">
              <Download className="w-3.5 h-3.5" /> Export
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-800/30">
                  {['Rank', 'Village', 'Yield (ton/ha)', 'Total Production (ton)', 'ROI (%)', 'Performance'].map(h => (
                    <th key={h} className="text-left text-xs font-semibold text-gray-400 px-5 py-3 uppercase tracking-wide">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {villageRanking.map((v, i) => (
                  <tr key={v.village} className="border-b border-gray-50 dark:border-gray-800/50 hover:bg-gray-50/50 dark:hover:bg-gray-800/30 transition-colors">
                    <td className="px-5 py-3">
                      <span className={`w-6 h-6 rounded-full inline-flex items-center justify-center text-xs font-bold ${i === 0 ? 'bg-amber-100 text-amber-700' : i === 1 ? 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400' : i === 2 ? 'bg-orange-50 text-orange-600' : 'bg-gray-50 dark:bg-gray-800 text-gray-500'}`}>{i + 1}</span>
                    </td>
                    <td className="px-5 py-3 text-sm font-medium text-gray-800 dark:text-gray-200">{v.village}</td>
                    <td className="px-5 py-3 text-sm font-bold text-green-700 dark:text-green-400">{v.yield}</td>
                    <td className="px-5 py-3 text-sm text-gray-700 dark:text-gray-300">{formatNumber(v.production)}</td>
                    <td className="px-5 py-3 text-sm text-gray-700 dark:text-gray-300">{v.roi}%</td>
                    <td className="px-5 py-3 w-40">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                          <div className="h-full rounded-full bg-green-500" style={{ width: `${(v.yield / 8) * 100}%` }} />
                        </div>
                        <span className="text-xs text-gray-400 w-8 text-right">{((v.yield / 8) * 100).toFixed(0)}%</span>
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
