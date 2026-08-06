import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, Users, Settings, Activity, FileText, Shield,
  BookOpen, Receipt, CreditCard, Menu, Tractor, CloudSun, TrendingUp, AlertTriangle,
  Satellite, FlaskConical,
} from 'lucide-react'
import { Button } from '@econojin/ui/button'
import { useState } from 'react'

const navItems = [
  { to: '/', label: 'داشبورد', icon: LayoutDashboard, end: true },
  { to: '/users', label: 'کاربران', icon: Users },
  { to: '/settings', label: 'تنظیمات', icon: Settings },
  { to: '/audit-logs', label: 'لاگ‌های حسابرسی', icon: Activity },
  { to: '/reports', label: 'گزارش‌ها', icon: FileText },
  { to: '/monitoring', label: 'نظارت', icon: Shield },
  { label: 'حسابداری', icon: BookOpen, children: [
    { to: '/accounting/accounts', label: 'حساب‌ها', icon: Receipt },
    { to: '/accounting/journal-entries', label: 'مطالب مجله', icon: BookOpen },
    { to: '/accounting/invoices', label: 'صورتحساب‌ها', icon: FileText },
    { to: '/accounting/payments', label: 'پرداخت‌ها', icon: CreditCard },
  ]},
  { label: 'کشاورزی هوشمند', icon: Tractor, children: [
    { to: '/farms', label: 'مزارع', icon: Tractor },
    { to: '/weather', label: 'آب‌وهوا', icon: CloudSun },
    { to: '/economics', label: 'اقتصاد سبز', icon: TrendingUp },
    { to: '/risks', label: 'پیش‌بینی ریسک', icon: AlertTriangle },
    { to: '/satellite', label: 'داده ماهواره‌ای', icon: Satellite },
    { to: '/simulation', label: 'مدل‌های شبیه‌سازی', icon: FlaskConical },
    { to: '/security', label: 'SpiderGuard', icon: Shield },
  ]},
]

export default function AdminSidebar() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen)
  }

  return (
    <>
      {/* Mobile menu button */}
      <div className="md:hidden fixed top-4 left-4 z-50">
        <Button 
          variant="outline" 
          size="icon"
          onClick={toggleMobileMenu}
          aria-label={isMobileMenuOpen ? 'بستن منو' : 'باز کردن منو'}
        >
          <Menu className="h-4 w-4" />
        </Button>
      </div>

      {/* Sidebar */}
      <aside 
        className={`fixed md:relative z-40 inset-y-0 right-0 w-64 bg-card border-l transform transition-transform duration-300 ease-in-out ${
          isMobileMenuOpen ? 'translate-x-0' : 'translate-x-full md:translate-x-0'
        }`}
        aria-label="نوار کناری ناوبری"
      >
        <div className="h-16 flex items-center px-6 border-b flex-shrink-0">
          <span className="text-lg font-bold text-eco-700">پنل مدیریت</span>
        </div>
        <nav className="p-4 space-y-1 overflow-y-auto flex-1 h-[calc(100%-4rem)]">
          {navItems.map((item) => {
            if ('children' in item && item.children) {
              return (
                <div key={item.label} className="space-y-1" role="group" aria-labelledby={`section-${item.label}`}>
                  <div 
                    id={`section-${item.label}`}
                    className="flex items-center gap-3 px-3 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider"
                  >
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
                        onClick={() => setIsMobileMenuOpen(false)}
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
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <item.icon className="w-4 h-4" />
                <span>{item.label}</span>
              </NavLink>
            )
          })}
        </nav>
      </aside>

      {/* Overlay for mobile */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-30 md:hidden"
          onClick={toggleMobileMenu}
          aria-hidden="true"
        ></div>
      )}
    </>
  )
}
</content>

<write_to_file>
<path>apps/admin_panel/frontend/src/App.tsx</path>
<content>import { Routes, Route } from 'react-router-dom'
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
  )
}