import { useState } from 'react'
import { Plus, Search, Filter, Download, MoreVertical } from 'lucide-react'

type AccountType = 'asset' | 'liability' | 'equity' | 'revenue' | 'expense'

interface Account {
  id: string
  code: string
  name: string
  type: AccountType
  balance: number
  currency: string
  is_active: boolean
  created_at: string
}

const mockAccounts: Account[] = [
  { id: '1', code: '1000', name: 'Cash', type: 'asset', balance: 125000, currency: 'USD', is_active: true, created_at: '2024-01-01' },
  { id: '2', code: '2000', name: 'Accounts Payable', type: 'liability', balance: 45000, currency: 'USD', is_active: true, created_at: '2024-01-01' },
  { id: '3', code: '3000', name: 'Owner Equity', type: 'equity', balance: 80000, currency: 'USD', is_active: true, created_at: '2024-01-01' },
  { id: '4', code: '4000', name: 'Sales Revenue', type: 'revenue', balance: 350000, currency: 'USD', is_active: true, created_at: '2024-01-01' },
  { id: '5', code: '5000', name: 'Operating Expenses', type: 'expense', balance: 180000, currency: 'USD', is_active: true, created_at: '2024-01-01' },
]

const typeColors: Record<AccountType, string> = {
  asset: 'bg-green-100 text-green-800',
  liability: 'bg-red-100 text-red-800',
  equity: 'bg-purple-100 text-purple-800',
  revenue: 'bg-blue-100 text-blue-800',
  expense: 'bg-amber-100 text-amber-800',
}

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<Account[]>(mockAccounts)
  const [search, setSearch] = useState('')
  const [filterType, setFilterType] = useState<AccountType | 'all'>('all')
  const [showModal, setShowModal] = useState(false)
  const [newAccount, setNewAccount] = useState({ code: '', name: '', type: 'asset' as AccountType })

  const filtered = accounts.filter(a => {
    const matchSearch = a.name.toLowerCase().includes(search.toLowerCase()) || a.code.includes(search)
    const matchType = filterType === 'all' || a.type === filterType
    return matchSearch && matchType
  })

  const handleCreate = () => {
    if (!newAccount.code || !newAccount.name) return
    setAccounts([...accounts, { ...newAccount, id: Date.now().toString(), balance: 0, currency: 'USD', is_active: true, created_at: new Date().toISOString().split('T')[0] }])
    setNewAccount({ code: '', name: '', type: 'asset' })
    setShowModal(false)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold"> accounts </h1>
          <p className="text-muted-foreground">Manage chart of accounts </p>
        </div>
        <button onClick={() => setShowModal(true)} className="flex items-center gap-2 px-4 py-2 bg-eco-600 text-white rounded-lg hover:bg-eco-700">
          <Plus className="w-4 h-4" />
          New Account
        </button>
      </div>

      <div className="rounded-xl border bg-card shadow-sm">
        <div className="p-4 border-b flex items-center gap-3">
          <div className="relative flex-1">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search accounts..." className="w-full pr-10 pl-4 py-2 border rounded-lg text-sm" />
          </div>
          <select value={filterType} onChange={e => setFilterType(e.target.value as any)} className="px-4 py-2 border rounded-lg text-sm">
            <option value="all">All Types</option>
            <option value="asset">Asset</option>
            <option value="liability">Liability</option>
            <option value="equity">Equity</option>
            <option value="revenue">Revenue</option>
            <option value="expense">Expense</option>
          </select>
          <button className="p-2 border rounded-lg hover:bg-accent">
            <Download className="w-4 h-4" />
          </button>
        </div>

        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-muted/50">
              <th className="text-right p-4">Code</th>
              <th className="text-right p-4">Name</th>
              <th className="text-right p-4">Type</th>
              <th className="text-right p-4">Balance</th>
              <th className="text-right p-4">Status</th>
              <th className="text-right p-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(account => (
              <tr key={account.id} className="border-b last:border-0 hover:bg-muted/30">
                <td className="p-4 font-mono">{account.code}</td>
                <td className="p-4 font-medium">{account.name}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded-full text-xs ${typeColors[account.type]}`}>
                    {account.type}
                  </span>
                </td>
                <td className="p-4 font-medium">{account.balance.toLocaleString()} {account.currency}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded-full text-xs ${account.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                    {account.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="p-4">
                  <button className="p-1 hover:bg-accent rounded">
                    <MoreVertical className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card border rounded-xl p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Create Account</h2>
            <div className="space-y-4">
              <input value={newAccount.code} onChange={e => setNewAccount({ ...newAccount, code: e.target.value })} placeholder="Account Code (e.g., 6000)" className="w-full px-4 py-2 border rounded-lg" />
              <input value={newAccount.name} onChange={e => setNewAccount({ ...newAccount, name: e.target.value })} placeholder="Account Name" className="w-full px-4 py-2 border rounded-lg" />
              <select value={newAccount.type} onChange={e => setNewAccount({ ...newAccount, type: e.target.value as AccountType })} className="w-full px-4 py-2 border rounded-lg">
                <option value="asset">Asset</option>
                <option value="liability">Liability</option>
                <option value="equity">Equity</option>
                <option value="revenue">Revenue</option>
                <option value="expense">Expense</option>
              </select>
            </div>
            <div className="flex gap-3 mt-6">
              <button onClick={handleCreate} className="flex-1 px-4 py-2 bg-eco-600 text-white rounded-lg hover:bg-eco-700">Create</button>
              <button onClick={() => setShowModal(false)} className="flex-1 px-4 py-2 border rounded-lg">Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}