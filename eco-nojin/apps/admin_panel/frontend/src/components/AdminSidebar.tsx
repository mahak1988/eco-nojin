import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/', label: 'Dashboard', icon: '📊', end: true },
  { to: '/users', label: 'Users', icon: '👥' },
  { to: '/settings', label: 'Settings', icon: '⚙️' },
]

export default function AdminSidebar() {
  return (
    <aside className="w-64 border-r bg-card">
      <div className="h-16 flex items-center px-6 border-b">
        <span className="text-lg font-bold text-eco-700">Admin Panel</span>
      </div>
      <nav className="p-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-eco-100 text-eco-800'
                  : 'text-muted-foreground hover:bg-accent'
              }`
            }
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}