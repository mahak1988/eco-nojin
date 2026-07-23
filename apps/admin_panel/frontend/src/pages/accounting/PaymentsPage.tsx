import { useState } from 'react'
import { Plus, Search } from 'lucide-react'

interface Payment {
  id: string
  invoice_number: string
  client_name: string
  amount: number
  payment_method: string
  paid_at: string
  currency?: string;
}

const mockPayments: Payment[] = [
  { id: '1', invoice_number: 'INV-001', client_name: 'Acme Corp', amount: 15000, payment_method: 'bank_transfer', paid_at: '2024-01-05' },
  { id: '2', invoice_number: 'INV-002', client_name: 'Globex Inc', amount: 8200, payment_method: 'credit_card', paid_at: '2024-01-10' },
]

export default function PaymentsPage() {
  const [payments, setPayments] = useState<Payment[]>(mockPayments)
  const [search, setSearch] = useState('')
  const filtered = payments.filter(p => p.client_name.toLowerCase().includes(search.toLowerCase()) || p.invoice_number.toLowerCase().includes(search.toLowerCase()))
  const totalReceived = filtered.reduce((sum, p) => sum + p.amount, 0)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Payments</h1>
          <p className="text-muted-foreground">Total received: {totalReceived.toLocaleString()} USD</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-eco-600 text-white rounded-lg hover:bg-eco-700">
          <Plus className="w-4 h-4" /> Record Payment
        </button>
      </div>
      <div className="rounded-xl border bg-card shadow-sm">
        <div className="p-4 border-b">
          <div className="relative">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search payments..." className="w-full md:w-96 pr-10 pl-4 py-2 border rounded-lg text-sm" />
          </div>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-muted/50">
              <th className="text-right p-4">Invoice</th>
              <th className="text-right p-4">Client</th>
              <th className="text-right p-4">Amount</th>
              <th className="text-right p-4">Method</th>
              <th className="text-right p-4">Date</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(payment => (
              <tr key={payment.id} className="border-b last:border-0 hover:bg-muted/30">
                <td className="p-4 font-mono">{payment.invoice_number}</td>
                <td className="p-4 font-medium">{payment.client_name}</td>
                <td className="p-4 font-medium">{payment.amount.toLocaleString()} {payment.currency}</td>
                <td className="p-4 capitalize">{payment.payment_method.replace('_', ' ')}</td>
                <td className="p-4 text-muted-foreground">{payment.paid_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}