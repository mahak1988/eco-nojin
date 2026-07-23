import { useState } from 'react'
import { Activity, Cpu, Zap, Shield } from 'lucide-react'

const agents = [
  { id: 1, name: 'Climate Agent', status: 'running', tasks: 12, cpu: '45%', memory: '128MB' },
  { id: 2, name: 'Agriculture Agent', status: 'running', tasks: 8, cpu: '32%', memory: '96MB' },
  { id: 3, name: 'Water Agent', status: 'idle', tasks: 0, cpu: '5%', memory: '64MB' },
  { id: 4, name: 'Energy Agent', status: 'running', tasks: 15, cpu: '67%', memory: '256MB' },
]

export default function AgentsDashboard() {
  const [selectedAgent, setSelectedAgent] = useState<number | null>(null)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">AI Agents Dashboard</h1>
        <p className="text-muted-foreground">Monitor and manage AI agents</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Active Agents', value: '3', icon: Activity, color: 'text-green-600' },
          { label: 'Total Tasks', value: '35', icon: Cpu, color: 'text-blue-600' },
          { label: 'Avg CPU', value: '37%', icon: Zap, color: 'text-amber-600' },
          { label: 'System Health', value: '98%', icon: Shield, color: 'text-eco-600' },
        ].map((stat) => (
          <div key={stat.label} className="rounded-xl border bg-card p-5 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-muted-foreground">{stat.label}</p>
              <stat.icon className={`w-5 h-5 ${stat.color}`} />
            </div>
            <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="rounded-xl border bg-card shadow-sm overflow-hidden">
        <div className="p-6 border-b">
          <h2 className="font-semibold">Active Agents</h2>
        </div>
        <div className="divide-y">
          {agents.map((agent) => (
            <div
              key={agent.id}
              className={`p-4 flex items-center justify-between cursor-pointer transition-colors ${
                selectedAgent === agent.id ? 'bg-eco-50' : 'hover:bg-muted/50'
              }`}
              onClick={() => setSelectedAgent(agent.id)}
            >
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-eco-100 flex items-center justify-center text-xl">
                  🤖
                </div>
                <div>
                  <p className="font-medium">{agent.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {agent.tasks} tasks • CPU: {agent.cpu} • MEM: {agent.memory}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${
                  agent.status === 'running' ? 'bg-green-500' : 'bg-gray-400'
                }`} />
                <span className="text-sm text-muted-foreground">{agent.status}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}