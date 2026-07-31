import { Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './contexts/ThemeContext'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Users from './pages/Users'
import Settings from './pages/Settings'
import AuditLogsPage from './pages/AuditLogsPage'
import ReportsPage from './pages/ReportsPage'
import MonitoringPage from './pages/MonitoringPage'
import AccountsPage from './pages/accounting/AccountsPage'
import JournalEntriesPage from './pages/accounting/JournalEntriesPage'
import InvoicesPage from './pages/accounting/InvoicesPage'
import PaymentsPage from './pages/accounting/PaymentsPage'

export default function App() {
  return (
    <ThemeProvider>
      <Routes>
        <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="users" element={<Users />} />
        <Route path="settings" element={<Settings />} />
        <Route path="audit-logs" element={<AuditLogsPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="monitoring" element={<MonitoringPage />} />
        <Route path="accounting/accounts" element={<AccountsPage />} />
        <Route path="accounting/journal-entries" element={<JournalEntriesPage />} />
        <Route path="accounting/invoices" element={<InvoicesPage />} />
        <Route path="accounting/payments" element={<PaymentsPage />} />
        <Route path="*" element={<div className="p-8 text-center">404 Not Found</div>} />
      </Route>
    </Routes>
    </ThemeProvider>
  )
}
</content>

<write_to_file>
<path>apps/admin_panel/frontend/src/components/AdminSidebar.tsx</path>
<content>import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, Users, Settings, Activity, FileText, Shield,
  BookOpen, Receipt, CreditCard,
} from 'lucide-react'

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/users', label: 'Users', icon: Users },
  { to: '/settings', label: 'Settings', icon: Settings },
  { to: '/audit-logs', label: 'Audit Logs', icon: Activity },
  { to: '/reports', label: 'Reports', icon: FileText },
  { to: '/monitoring', label: 'Monitoring', icon: Shield },
  { label: 'Accounting', icon: BookOpen, children: [
    { to: '/accounting/accounts', label: 'Accounts', icon: Receipt },
    { to: '/accounting/journal-entries', label: 'Journal Entries', icon: BookOpen },
    { to: '/accounting/invoices', label: 'Invoices', icon: FileText },
    { to: '/accounting/payments', label: 'Payments', icon: CreditCard },
  ]},
]

export default function AdminSidebar() {
  return (
    <aside className="w-64 border-r bg-card flex flex-col h-screen sticky top-0">
      <div className="h-16 flex items-center px-6 border-b flex-shrink-0">
        <span className="text-lg font-bold text-eco-700">Admin Panel</span>
      </div>
      <nav className="p-4 space-y-1 overflow-y-auto flex-1">
        {navItems.map((item) => {
          if ('children' in item && item.children) {
            return (
              <div key={item.label} className="space-y-1">
                <div className="flex items-center gap-3 px-3 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  <item.icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </div>
                <div className="mr-3 space-y-1">
                  {item.children.map((child) => (
                    <NavLink
                      key={child.to}
                      to={child.to}
                      className={({ isActive }) =>
                        `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                          isActive
                            ? 'bg-eco-100 text-eco-800'
                            : 'text-muted-foreground hover:bg-accent'
                        }`
                      }
                    >
                      <child.icon className="w-4 h-4" />
                      <span>{child.label}</span>
                    </NavLink>
                  ))}
                </div>
              </div>
            )
          }
          return (
            <NavLink
              key={item.to}
              to={item.to!}
              end={item.end}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-eco-100 text-eco-800'
                    : 'text-muted-foreground hover:bg-accent'
                }`
              }
            >
              <item.icon className="w-4 h-4" />
              <span>{item.label}</span>
            </NavLink>
          )
        })}
      </nav>
    </aside>
  )
}