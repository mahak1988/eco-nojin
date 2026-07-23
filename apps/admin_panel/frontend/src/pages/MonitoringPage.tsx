import { useState } from 'react'
import { Activity, Cpu, Zap, Shield } from 'lucide-react'

const stats = [
  { label: 'CPU Usage', value: '45%', color: 'text-blue-600' },
  { label: 'Memory', value: '2.4GB / 4GB', color: 'text-amber-600' },
  { label: 'Active Connections', value: '1,234', color: 'text-green-600' },
  { label: 'Uptime', value: '99.98%', color: 'text-eco-600' },
]

const alerts = [
  { id: 1, time: '10:23', level: 'info', message: 'System health check passed' },
  { id: 2, time: '10:15', level: 'warning', message: 'High memory usage detected on node-3' },
  { id: 3, time: '09:45', level: 'error', message: 'Database query timeout on reports service' },
]

const levelColors: Record<string, string> = {
  info: 'bg-blue-100 text-blue-800',
  warning: 'bg-amber-100 text-amber-800',
  error: 'bg-red-100 text-red-800',
}

export default function MonitoringPage() {
  const [filter, setFilter] = useState('all')
  const filtered = filter === 'all' ? alerts : alerts.filter(a => a.level === filter)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">System Monitoring</h1>
        <p className="text-muted-foreground">Real-time system health and alerts</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map(stat => (
          <div key={stat.label} className="rounded-xl border bg-card p-5 shadow-sm">
            <p className="text-sm text-muted-foreground mb-1">{stat.label}</p>
            <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="rounded-xl border bg-card shadow-sm">
        <div className="p-4 border-b flex items-center justify-between">
          <h2 className="font-semibold">Recent Alerts</h2>
          <div className="flex gap-2">
            {['all', 'info', 'warning', 'error'].map(level => (
              <button key={level} onClick={() => setFilter(level)} className={`px-3 py-1 rounded-lg border text-xs capitalize ${filter === level ? 'bg-eco-100 border-eco-300 text-eco-800' : 'hover:bg-accent'}`}>
                {level}
              </button>
            ))}
          </div>
        </div>
        <div className="divide-y">
          {filtered.map(alert => (
            <div key={alert.id} className="p-4 flex items-center gap-4 hover:bg-muted/30">
              <span className={`px-2 py-1 rounded-full text-xs capitalize ${levelColors[alert.level]}`}>{alert.level}</span>
              <span className="text-sm text-muted-foreground font-mono">{alert.time}</span>
              <span className="flex-1 text-sm">{alert.message}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}