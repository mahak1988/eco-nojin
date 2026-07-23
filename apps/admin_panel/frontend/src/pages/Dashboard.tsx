import { useTranslation } from 'react-i18next'
import { Users, FolderOpen, TrendingUp, Activity } from 'lucide-react'

export default function Dashboard() {
  const { t } = useTranslation()

  const stats = [
    { label: 'Total Users', value: '4,256', icon: Users, color: 'text-eco-600' },
    { label: 'Active Projects', value: '124', icon: FolderOpen, color: 'text-water-600' },
    { label: 'Growth', value: '+23%', icon: TrendingUp, color: 'text-green-600' },
    { label: 'System Status', value: 'Healthy', icon: Activity, color: 'text-amber-600' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Admin Dashboard</h1>
        <p className="text-muted-foreground">Welcome to the admin control panel</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div key={stat.label} className="rounded-xl border bg-card p-5 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-muted-foreground">{stat.label}</p>
              <stat.icon className={`w-5 h-5 ${stat.color}`} />
            </div>
            <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="rounded-xl border bg-card p-6 shadow-sm">
        <h2 className="font-semibold mb-4">Recent Activity</h2>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
              <div className="w-2 h-2 rounded-full bg-eco-500" />
              <div className="flex-1">
                <p className="text-sm font-medium">System update #{i}</p>
                <p className="text-xs text-muted-foreground">2 hours ago</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}