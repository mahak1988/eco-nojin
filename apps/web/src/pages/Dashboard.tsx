import {
  Area, AreaChart, CartesianGrid, Cell, Pie, PieChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import { ArrowUpRight } from 'lucide-react'
import Header from '../components/Header'
import { productionTrend, cropVariety, fieldStatus } from '../lib/data'
import { formatNumber } from '../lib/utils'
import DashboardMap from '../components/DashboardMap'

/* ── Sparkline data ──────────────────────────────────────── */
const waterSpark  = [{v:98},{v:105},{v:112},{v:118},{v:109},{v:115},{v:125},{v:132}]
const fertSpark   = [{v:38},{v:42},{v:46},{v:50},{v:48},{v:43},{v:46},{v:50}]
const scoreSpark  = [{v:79},{v:82},{v:80},{v:83},{v:84},{v:85},{v:86},{v:87}]

/* ── Donut slice label ───────────────────────────────────── */
const R = Math.PI / 180
const sliceLabel = ({ cx,cy,midAngle,innerRadius,outerRadius,percent }: any) => {
  if (percent < 0.07) return null
  const r = innerRadius + (outerRadius - innerRadius) * 0.55
  return (
    <text x={cx + r*Math.cos(-midAngle*R)} y={cy + r*Math.sin(-midAngle*R)}
      fill="white" textAnchor="middle" dominantBaseline="central" fontSize={9} fontWeight={700}>
      {(percent*100).toFixed(0)}%
    </text>
  )
}

/* ── Recent activities ───────────────────────────────────── */
const ACTIVITIES = [
  { title:'Field ID F-2025-0012', desc:'Planting recorded',              time:'2 hours ago', bg:'bg-green-500',  emoji:'🌱' },
  { title:'Field ID F-2025-0456', desc:'Harvest recorded',               time:'5 hours ago', bg:'bg-amber-500',  emoji:'🌾' },
  { title:'Fertilizer distribution', desc:'Urea 5 ton to Desa Karangampel', time:'1 day ago', bg:'bg-blue-500',   emoji:'🧪' },
  { title:'Water usage updated',  desc:'Irrigation Pump 03',             time:'1 day ago',   bg:'bg-cyan-500',   emoji:'💧' },
]

export default function Dashboard() {
  return (
    /* Full-height flex column — NO scroll on outer container */
    <div className="flex flex-col h-full overflow-hidden bg-gray-50 dark:bg-gray-900">
      <Header title="Dashboard" subtitle="Overview of agricultural activities and key metrics" />

      {/* ── Body: fixed flex-col, no scroll ────────────────── */}
      <div className="flex-1 flex flex-col overflow-hidden p-3 gap-3 min-h-0">

        {/* ── ROW 1: 5 KPI cards ── */}
        <div className="grid grid-cols-5 gap-3 shrink-0">
          {[
            { label:'Total Area',           value:'12,543', unit:'ha',  sub:'+2.35% from last season', icon:'🌳', bg:'bg-green-900/30'   },
            { label:'Active Fields',         value:'8,921',  unit:'ha',  sub:'71.1% of total area',     icon:'🌿', bg:'bg-emerald-900/30' },
            { label:'Registered Farmers',    value:'4,782',  unit:'',    sub:'+120 new this season',    icon:'👨‍🌾',bg:'bg-blue-900/30'    },
            { label:'Estimated Production',  value:'45,682', unit:'ton', sub:'+8.45% from last season', icon:'🌾', bg:'bg-amber-900/30'   },
            { label:'Season Progress',       value:'63',     unit:'%',   sub:'Growing Period',          icon:'📊', bg:'bg-violet-900/30'  },
          ].map(({ label, value, unit, sub, icon, bg }) => (
            <div key={label} className="card p-3.5 flex items-start justify-between hover:shadow-card-hover transition-shadow">
              <div className="min-w-0">
                <p className="text-[10px] font-medium text-gray-400 dark:text-gray-500">{label}</p>
                <p className="text-xl font-bold text-gray-900 dark:text-white mt-0.5 tracking-tight leading-none">
                  {value}<span className="text-xs font-normal text-gray-400 ml-1">{unit}</span>
                </p>
                <p className="text-[10px] text-green-600 dark:text-green-400 font-medium mt-1 flex items-center gap-0.5">
                  <ArrowUpRight className="w-2.5 h-2.5" />{sub}
                </p>
              </div>
              <div className={`w-9 h-9 rounded-xl flex items-center justify-center text-lg shrink-0 ${bg}`}>
                {icon}
              </div>
            </div>
          ))}
        </div>

        {/* ── ROW 2: 3 Sparkline cards ── */}
        <div className="grid grid-cols-3 gap-3 shrink-0">
          {[
            { label:'Water Usage',        value:'1,250,000', unit:'m³',  sub:'+5.2% from last season', data:waterSpark },
            { label:'Fertilizer Usage',   value:'2,345',     unit:'ton', sub:'+6.1% from last season', data:fertSpark  },
            { label:'Productivity Score', value:'87',        unit:'/100',sub:'Very Good',              data:scoreSpark },
          ].map(({ label, value, unit, sub, data }) => (
            <div key={label} className="card px-4 py-3 flex items-center gap-2">
              <div className="flex-1 min-w-0">
                <p className="text-[10px] font-medium text-gray-400 dark:text-gray-500">{label}</p>
                <p className="text-lg font-bold text-gray-900 dark:text-white mt-0.5 tracking-tight leading-none">
                  {value}<span className="text-xs font-normal text-gray-400 ml-1">{unit}</span>
                </p>
                <p className="text-[10px] text-green-600 dark:text-green-400 font-medium mt-1 flex items-center gap-0.5">
                  <ArrowUpRight className="w-2.5 h-2.5"/>{sub}
                </p>
              </div>
              <div className="w-24 h-10 shrink-0">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={data} margin={{top:2,right:2,left:2,bottom:2}}>
                    <defs>
                      <linearGradient id={`sg${label}`} x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%"  stopColor="#16a34a" stopOpacity={0.2}/>
                        <stop offset="95%" stopColor="#16a34a" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <Area type="monotone" dataKey="v" stroke="#16a34a" strokeWidth={1.5}
                      fill={`url(#sg${label})`} dot={false}/>
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          ))}
        </div>

        {/* ── ROW 3: Charts (flex-1 so they grow) ── */}
        <div className="grid grid-cols-3 gap-3 flex-1 min-h-0">

          {/* Production Trend */}
          <div className="card p-4 flex flex-col min-h-0">
            <div className="flex items-center justify-between mb-2 shrink-0">
              <h3 className="text-xs font-semibold text-gray-900 dark:text-white">
                Production Trend <span className="text-gray-400 font-normal">(Ton)</span>
              </h3>
              <div className="flex items-center gap-3 text-[10px] text-gray-400">
                <span className="flex items-center gap-1">
                  <svg width="14" height="2"><line x1="0" y1="1" x2="14" y2="1" stroke="#9ca3af" strokeWidth="2" strokeDasharray="3 2"/></svg>2024
                </span>
                <span className="flex items-center gap-1">
                  <svg width="14" height="2"><line x1="0" y1="1" x2="14" y2="1" stroke="#16a34a" strokeWidth="2"/></svg>2025
                </span>
              </div>
            </div>
            <div className="flex-1 min-h-0">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={productionTrend} margin={{top:4,right:4,left:-24,bottom:0}}>
                  <defs>
                    <linearGradient id="g25" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#16a34a" stopOpacity={0.12}/>
                      <stop offset="95%" stopColor="#16a34a" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" vertical={false}/>
                  <XAxis dataKey="month" tick={{fontSize:9,fill:'#9ca3af'}} axisLine={false} tickLine={false}/>
                  <YAxis tick={{fontSize:9,fill:'#9ca3af'}} axisLine={false} tickLine={false}
                    tickFormatter={(v:number)=>`${v/1000}k`}/>
                  <Tooltip formatter={(v)=>formatNumber(Number(v))+' ton'}
                    contentStyle={{borderRadius:8,border:'none',fontSize:10,boxShadow:'0 4px 12px rgba(0,0,0,0.1)'}}/>
                  <Area type="monotone" dataKey="2024" stroke="#e5e7eb" strokeWidth={1.5}
                    strokeDasharray="4 2" fill="none" dot={false}/>
                  <Area type="monotone" dataKey="2025" stroke="#16a34a" strokeWidth={2}
                    fill="url(#g25)" dot={{r:2.5,fill:'#16a34a',stroke:'white',strokeWidth:1.5}} activeDot={{r:4}}/>
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Crop Variety Distribution */}
          <div className="card p-4 flex flex-col min-h-0">
            <h3 className="text-xs font-semibold text-gray-900 dark:text-white mb-2 shrink-0">Crop Variety Distribution</h3>
            <div className="flex-1 flex items-center gap-2 min-h-0">
              <div className="shrink-0" style={{width:110,height:110}}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={cropVariety} cx="50%" cy="50%" innerRadius={32} outerRadius={50}
                      dataKey="value" paddingAngle={2} labelLine={false} label={sliceLabel}>
                      {cropVariety.map((e,i)=><Cell key={i} fill={e.color}/>)}
                    </Pie>
                    <text x="50%" y="47%" textAnchor="middle" dominantBaseline="middle"
                      fill="#111827" fontSize={11} fontWeight={700}>45,682</text>
                    <text x="50%" y="60%" textAnchor="middle" dominantBaseline="middle"
                      fill="#9ca3af" fontSize={8}>ton</text>
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex-1 space-y-1.5 min-w-0">
                {cropVariety.map(({name,value,color})=>(
                  <div key={name} className="flex items-center justify-between">
                    <span className="flex items-center gap-1.5 text-[11px] text-gray-500 dark:text-gray-400 min-w-0">
                      <span className="w-2 h-2 rounded-full shrink-0" style={{background:color}}/>
                      <span className="truncate">{name}</span>
                    </span>
                    <span className="text-[11px] font-bold text-gray-700 dark:text-gray-300 ml-1 shrink-0">{value}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Fields Status */}
          <div className="card p-4 flex flex-col min-h-0">
            <h3 className="text-xs font-semibold text-gray-900 dark:text-white mb-2 shrink-0">Fields Status</h3>
            <div className="flex-1 flex items-center gap-2 min-h-0">
              <div className="shrink-0" style={{width:110,height:110}}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={fieldStatus} cx="50%" cy="50%" innerRadius={32} outerRadius={50}
                      dataKey="value" paddingAngle={2} labelLine={false} label={sliceLabel}>
                      {fieldStatus.map((e,i)=><Cell key={i} fill={e.color}/>)}
                    </Pie>
                    <text x="50%" y="47%" textAnchor="middle" dominantBaseline="middle"
                      fill="#111827" fontSize={11} fontWeight={700}>12,543</text>
                    <text x="50%" y="60%" textAnchor="middle" dominantBaseline="middle"
                      fill="#9ca3af" fontSize={8}>ha</text>
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex-1 space-y-1.5 min-w-0">
                {fieldStatus.map(({name,value,pct,color})=>(
                  <div key={name} className="flex items-start gap-1.5">
                    <span className="w-2 h-2 rounded-full shrink-0 mt-0.5" style={{background:color}}/>
                    <div className="min-w-0">
                      <p className="text-[11px] font-semibold text-gray-700 dark:text-gray-300 leading-tight truncate">{name}</p>
                      <p className="text-[10px] text-gray-400">{formatNumber(value)} ha ({pct}%)</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* ── ROW 4: Map + Recent Activities (flex-1, fills rest) ── */}
        <div className="grid grid-cols-3 gap-3 flex-1 min-h-0">

          {/* Map card */}
          <div className="card col-span-2 flex flex-col overflow-hidden min-h-0">
            <div className="flex items-center justify-between px-4 py-2.5 border-b border-gray-100 dark:border-gray-800 shrink-0">
              <h3 className="text-xs font-semibold text-gray-900 dark:text-white">Field Map Overview</h3>
              <div className="flex items-center gap-2">
                <div className="relative">
                  <svg className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3 h-3 text-gray-400"
                    fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <circle cx="11" cy="11" r="8"/><path strokeLinecap="round" d="M21 21l-4.35-4.35"/>
                  </svg>
                  <input placeholder="Search location…"
                    className="pl-7 pr-3 py-1 text-[11px] bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg w-36 focus:outline-none text-gray-600 placeholder-gray-400"/>
                </div>
                <button className="w-6 h-6 flex items-center justify-center rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-100 transition-colors">
                  <svg className="w-3 h-3 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"/>
                  </svg>
                </button>
              </div>
            </div>
            {/* Map fills remaining height */}
            <div className="flex-1 min-h-0 relative">
              <div style={{position:'absolute',inset:0}}>
                <DashboardMap />
              </div>
            </div>
          </div>

          {/* Recent Activities */}
          <div className="card p-4 flex flex-col min-h-0 overflow-hidden">
            <h3 className="text-xs font-semibold text-gray-900 dark:text-white mb-3 shrink-0">Recent Activities</h3>
            <div className="flex-1 overflow-y-auto space-y-3">
              {ACTIVITIES.map(({title,desc,time,emoji,bg})=>(
                <div key={title} className="flex gap-2.5 items-start">
                  <div className={`w-8 h-8 rounded-xl ${bg} flex items-center justify-center text-sm shrink-0`}>
                    {emoji}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-semibold text-gray-800 dark:text-gray-200 truncate">{title}</p>
                    <p className="text-[10px] text-gray-400 mt-0.5 truncate">{desc}</p>
                    <p className="text-[9px] text-gray-300 dark:text-gray-600 mt-0.5">{time}</p>
                  </div>
                </div>
              ))}
            </div>
            <button className="mt-3 text-[11px] text-green-600 dark:text-green-400 font-semibold hover:underline shrink-0">
              View all activities →
            </button>
          </div>
        </div>

      </div>
    </div>
  )
}
