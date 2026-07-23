import { useTranslation } from 'react-i18next'
import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/', key: 'nav.home', icon: '🏠' },
  { to: '/dashboard', key: 'nav.dashboard', icon: '📊' },
  { to: '/dashboard/analytics', key: 'nav.analytics', icon: '📈' },
  { to: '/dashboard/map', key: 'nav.map', icon: '🗺️' },
  { to: '/dashboard/reports', key: 'nav.reports', icon: '📋' },
  { to: '/settings', key: 'nav.settings', icon: '⚙️' },
]

export default function Sidebar() {
  const { t } = useTranslation()

  return (
    <aside className="hidden md:flex w-64 flex-col border-r bg-card min-h-[calc(100vh-4rem)]">
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-eco-100 text-eco-800 dark:bg-eco-900 dark:text-eco-200'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              }`
            }
          >
            <span>{item.icon}</span>
            <span>{t(item.key)}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}