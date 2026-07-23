import { useState } from 'react'

const logs = [
  { id: 1, time: '10:23:45', agent: 'Climate Agent', level: 'info', message: 'Data collection completed' },
  { id: 2, time: '10:23:12', agent: 'Agriculture Agent', level: 'success', message: 'Soil analysis finished' },
  { id: 3, time: '10:22:58', agent: 'Energy Agent', level: 'warning', message: 'High CPU usage detected' },
  { id: 4, time: '10:22:30', agent: 'Climate Agent', level: 'info', message: 'Processing satellite data' },
  { id: 5, time: '10:21:15', agent: 'Water Agent', level: 'error', message: 'Connection timeout' },
]

const levelColors = {
  info: 'bg-blue-100 text-blue-800',
  success: 'bg-green-100 text-green-800',
  warning: 'bg-amber-100 text-amber-800',
  error: 'bg-red-100 text-red-800',
}

export default function AgentMonitor() {
  const [filter, setFilter] = useState<string>('all')

  const filteredLogs = filter === 'all' ? logs : logs.filter(l => l.level === filter)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Agent Monitor</h1>
        <p className="text-muted-foreground">Real-time logs and agent orchestration</p>
      </div>

      <div className="flex gap-2">
        {['all', 'info', 'success', 'warning', 'error'].map((level) => (
          <button
            key={level}
            onClick={() => setFilter(level)}
            className={`px-4 py-2 rounded-lg border text-sm capitalize transition-colors ${
              filter === level
                ? 'bg-eco-100 border-eco-300 text-eco-800'
                : 'bg-card hover:bg-accent'
            }`}
          >
            {level}
          </button>
        ))}
      </div>

      <div className="rounded-xl border bg-card shadow-sm overflow-hidden">
        <div className="divide-y">
          {filteredLogs.map((log) => (
            <div key={log.id} className="p-4 flex items-center gap-4 hover:bg-muted/50">
              <span className="text-sm text-muted-foreground font-mono">{log.time}</span>
              <span className="text-sm font-medium min-w-[160px]">{log.agent}</span>
              <span className={`px-2 py-0.5 rounded-full text-xs capitalize ${levelColors[log.level as keyof typeof levelColors]}`}>
                {log.level}
              </span>
              <span className="flex-1 text-sm">{log.message}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}