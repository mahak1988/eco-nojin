import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, Users, Settings, Activity, FileText, Shield,
  BookOpen, Receipt, CreditCard, Menu, Tractor, CloudSun, TrendingUp, AlertTriangle,
  Satellite, FlaskConical, Brain,
} from 'lucide-react'
import { Button } from '@econojin/ui/button'
import { useMemo, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'

type NavChild = { to: string; label: string; icon: typeof Users; roles?: string[] }
type NavItem =
  | { to: string; label: string; icon: typeof Users; end?: boolean; roles?: string[] }
  | { label: string; icon: typeof Users; children: NavChild[]; roles?: string[] }

const ALL_NAV: NavItem[] = [
  { to: '/', label: 'داشبورد', icon: LayoutDashboard, end: true },
  { to: '/users', label: 'کاربران', icon: Users, roles: ['admin', 'superuser'] },
  { to: '/settings', label: 'تنظیمات', icon: Settings },
  { to: '/audit-logs', label: 'لاگ‌های حسابرسی', icon: Activity, roles: ['admin', 'superuser'] },
  { to: '/reports', label: 'گزارش‌ها', icon: FileText },
  { to: '/monitoring', label: 'نظارت', icon: Shield, roles: ['admin', 'superuser'] },
  { to: '/insights', label: 'بینش هوشمند', icon: Brain, roles: ['admin', 'superuser'] },
  {
    label: 'حسابداری',
    icon: BookOpen,
    roles: ['admin', 'superuser', 'manager'],
    children: [
      { to: '/accounting/accounts', label: 'حساب‌ها', icon: Receipt },
      { to: '/accounting/journal-entries', label: 'دفتر روزنامه', icon: BookOpen },
      { to: '/accounting/invoices', label: 'صورتحساب‌ها', icon: FileText },
      { to: '/accounting/payments', label: 'پرداخت‌ها', icon: CreditCard },
    ],
  },
  {
    label: 'کشاورزی هوشمند',
    icon: Tractor,
    children: [
      { to: '/farms', label: 'مزارع', icon: Tractor },
      { to: '/weather', label: 'آب‌وهوا', icon: CloudSun },
      { to: '/economics', label: 'اقتصاد سبز', icon: TrendingUp },
      { to: '/risks', label: 'پیش‌بینی ریسک', icon: AlertTriangle },
      { to: '/satellite', label: 'داده ماهواره‌ای', icon: Satellite },
      { to: '/simulation', label: 'مدل‌های شبیه‌سازی', icon: FlaskConical },
      { to: '/security', label: 'SpiderGuard', icon: Shield, roles: ['admin', 'superuser'] },
    ],
  },
]

function canAccess(roles: string[] | undefined, userRoles: string[], isSuper: boolean): boolean {
  if (!roles || roles.length === 0) return true
  if (isSuper) return true
  return roles.some((r) => userRoles.includes(r))
}

export default function AdminSidebar() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const { user } = useAuth()

  const isSuper = !!user?.is_superuser
  const userRoles = useMemo(() => {
    const roles: string[] = []
    if (user?.role) roles.push(user.role)
    if (isSuper) roles.push('superuser', 'admin')
    if (!user) roles.push('viewer')
    return roles
  }, [user, isSuper])

  const navItems = useMemo(() => {
    return ALL_NAV.map((item) => {
      if ('children' in item && item.children) {
        if (!canAccess(item.roles, userRoles, isSuper)) return null
        const children = item.children.filter((c) => canAccess(c.roles, userRoles, isSuper))
        if (children.length === 0) return null
        return { ...item, children }
      }
      if (!canAccess(item.roles, userRoles, isSuper)) return null
      return item
    }).filter(Boolean) as NavItem[]
  }, [userRoles, isSuper])

  const toggleMobileMenu = () => setIsMobileMenuOpen(!isMobileMenuOpen)

  return (
    <>
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
                            isActive ? 'bg-eco-100 text-eco-800' : 'text-muted-foreground hover:bg-accent'
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
                    isActive ? 'bg-eco-100 text-eco-800' : 'text-muted-foreground hover:bg-accent'
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

      {isMobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30 md:hidden"
          onClick={toggleMobileMenu}
          aria-hidden="true"
        />
      )}
    </>
  )
}
