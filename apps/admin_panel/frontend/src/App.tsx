import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Users from './pages/Users'
import Settings from './pages/Settings'
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
