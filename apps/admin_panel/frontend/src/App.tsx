import { Routes, Route, useLocation } from 'react-router-dom'
import { ThemeProvider } from './contexts/ThemeContext'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { ToastProvider } from './components/Toast'
import AuthGuard from './components/AuthGuard'
import PermissionGuard, { requiredPermissionsForPath } from './components/PermissionGuard'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import NotFoundPage from './pages/NotFoundPage'
import ForbiddenPage from './pages/ForbiddenPage'
import Dashboard from './pages/Dashboard'
import Users from './pages/Users'
import Settings from './pages/Settings'
import AuditLogsPage from './pages/AuditLogsPage'
import ReportsPage from './pages/ReportsPage'
import MonitoringPage from './pages/MonitoringPage'
import IntelligentInsightsPage from './pages/IntelligentInsightsPage'
import AccountsPage from './pages/accounting/AccountsPage'
import JournalEntriesPage from './pages/accounting/JournalEntriesPage'
import InvoicesPage from './pages/accounting/InvoicesPage'
import PaymentsPage from './pages/accounting/PaymentsPage'
import FarmsPage from './pages/FarmsPage'
import WeatherPage from './pages/WeatherPage'
import EconomicsPage from './pages/EconomicsPage'
import RisksPage from './pages/RisksPage'
import SatellitePage from './pages/SatellitePage'
import SimulationPage from './pages/SimulationPage'
import SecurityPage from './pages/SecurityPage'

function ProtectedOutlet({ children }: { children: React.ReactNode }) {
  const location = useLocation()
  const perms = requiredPermissionsForPath(location.pathname)
  if (!perms) return <>{children}</>
  return <PermissionGuard anyOf={perms}>{children}</PermissionGuard>
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <ToastProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/"
              element={
                <AuthGuard>
                  <Layout />
                </AuthGuard>
              }
            >
              <Route index element={<Dashboard />} />
              <Route path="users" element={<ProtectedOutlet><Users /></ProtectedOutlet>} />
              <Route path="settings" element={<ProtectedOutlet><Settings /></ProtectedOutlet>} />
              <Route path="audit-logs" element={<ProtectedOutlet><AuditLogsPage /></ProtectedOutlet>} />
              <Route path="reports" element={<ProtectedOutlet><ReportsPage /></ProtectedOutlet>} />
              <Route path="monitoring" element={<ProtectedOutlet><MonitoringPage /></ProtectedOutlet>} />
              <Route path="insights" element={<ProtectedOutlet><IntelligentInsightsPage /></ProtectedOutlet>} />
              <Route path="forbidden" element={<ForbiddenPage />} />
              <Route path="accounting/accounts" element={<ProtectedOutlet><AccountsPage /></ProtectedOutlet>} />
              <Route path="accounting/journal-entries" element={<ProtectedOutlet><JournalEntriesPage /></ProtectedOutlet>} />
              <Route path="accounting/invoices" element={<ProtectedOutlet><InvoicesPage /></ProtectedOutlet>} />
              <Route path="accounting/payments" element={<ProtectedOutlet><PaymentsPage /></ProtectedOutlet>} />
              <Route path="farms" element={<FarmsPage />} />
              <Route path="weather" element={<WeatherPage />} />
              <Route path="economics" element={<EconomicsPage />} />
              <Route path="risks" element={<RisksPage />} />
              <Route path="satellite" element={<SatellitePage />} />
              <Route path="simulation" element={<SimulationPage />} />
              <Route path="security" element={<ProtectedOutlet><SecurityPage /></ProtectedOutlet>} />
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
        </ToastProvider>
      </AuthProvider>
    </ThemeProvider>
  )
}
