import { useState } from 'react'
import { Plus, Search, Download, Eye, Send } from 'lucide-react'

type InvoiceStatus = 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled'

interface Invoice {
  id: string
  invoice_number: string
  client_name: string
  status: InvoiceStatus
  amount: number
  currency: string
  issue_date: string
  due_date: string
}

const mockInvoices: Invoice[] = [
  { id: '1', invoice_number: 'INV-001', client_name: 'Acme Corp', status: 'paid', amount: 15000, currency: 'USD', issue_date: '2024-01-01', due_date: '2024-01-31' },
  { id: '2', invoice_number: 'INV-002', client_name: 'Globex Inc', status: 'sent', amount: 8200, currency: 'USD', issue_date: '2024-01-05', due_date: '2024-02-05' },
  { id: '3', invoice_number: 'INV-003', client_name: 'Stark Industries', status: 'overdue', amount: 45000, currency: 'USD', issue_date: '2023-12-01', due_date: '2023-12-31' },
  { id: '4', invoice_number: 'INV-004', client_name: 'Wayne Enterprises', status: 'draft', amount: 22000, currency: 'USD', issue_date: '2024-01-15', due_date: '2024-02-15' },
]

const statusColors: Record<InvoiceStatus, string> = {
  draft: 'bg-gray-100 text-gray-800',
  sent: 'bg-blue-100 text-blue-800',
  paid: 'bg-green-100 text-green-800',
  overdue: 'bg-red-100 text-red-800',
  cancelled: 'bg-red-50 text-red-600',
}

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState<Invoice[]>(mockInvoices)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<InvoiceStatus | 'all'>('all')
  const [showForm, setShowForm] = useState(false)

  const filtered = invoices.filter(inv => {
    const matchSearch = inv.client_name.toLowerCase().includes(search.toLowerCase()) || inv.invoice_number.toLowerCase().includes(search.toLowerCase())
    const matchStatus = statusFilter === 'all' || inv.status === statusFilter
    return matchSearch && matchStatus
  })

  const totalAmount = filtered.reduce((sum, inv) => sum + inv.amount, 0)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Invoices</h1>
          <p className="text-muted-foreground">Total: {filtered.length} invoices • {totalAmount.toLocaleString()} USD</p>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-2 px-4 py-2 bg-eco-600 text-white rounded-lg hover:bg-eco-700">
          <Plus className="w-4 h-4" />
          New Invoice
        </button>
      </div>

      <div className="rounded-xl border bg-card shadow-sm">
        <div className="p-4 border-b flex items-center gap-3">
          <div className="relative flex-1">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search invoices..." className="w-full pr-10 pl-4 py-2 border rounded-lg text-sm" />
          </div>
          <select value={statusFilter} onChange={e => setStatusFilter(e.target.value as any)} className="px-4 py-2 border rounded-lg text-sm">
            <option value="all">All Status</option>
            <option value="draft">Draft</option>
            <option value="sent">Sent</option>
            <option value="paid">Paid</option>
            <option value="overdue">Overdue</option>
            <option value="cancelled">Cancelled</option>
          </select>
          <button className="p-2 border rounded-lg hover:bg-accent">
            <Download className="w-4 h-4" />
          </button>
        </div>

        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-muted/50">
              <th className="text-right p-4">Invoice #</th>
              <th className="text-right p-4">Client</th>
              <th className="text-right p-4">Status</th>
              <th className="text-right p-4">Amount</th>
              <th className="text-right p-4">Issue Date</th>
              <th className="text-right p-4">Due Date</th>
              <th className="text-right p-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(invoice => (
              <tr key={invoice.id} className="border-b last:border-0 hover:bg-muted/30">
                <td className="p-4 font-mono">{invoice.invoice_number}</td>
                <td className="p-4 font-medium">{invoice.client_name}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded-full text-xs capitalize ${statusColors[invoice.status]}`}>
                    {invoice.status}
                  </span>
                </td>
                <td className="p-4 font-medium">{invoice.amount.toLocaleString()} {invoice.currency}</td>
                <td className="p-4 text-muted-foreground">{invoice.issue_date}</td>
                <td className="p-4 text-muted-foreground">{invoice.due_date}</td>
                <td className="p-4 flex gap-1">
                  <button className="p-1 hover:bg-accent rounded"><Eye className="w-4 h-4" /></button>
                  <button className="p-1 hover:bg-accent rounded"><Send className="w-4 h-4" /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}