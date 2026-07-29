import { useState } from 'react'
import { Plus, Search, CheckCircle2 } from 'lucide-react'

interface JournalEntry {
  id: string
  entry_date: string
  description: string
  is_posted: boolean
  lines_count: number
  total_debit: number
  total_credit: number
}

const mockEntries: JournalEntry[] = [
  { id: '1', entry_date: '2024-01-15', description: 'Opening balance', is_posted: true, lines_count: 5, total_debit: 530000, total_credit: 530000 },
  { id: '2', entry_date: '2024-01-16', description: 'Invoice payment received', is_posted: true, lines_count: 2, total_debit: 15000, total_credit: 15000 },
]

export default function JournalEntriesPage() {
  const [entries, setEntries] = useState<JournalEntry[]>(mockEntries)
  const [search, setSearch] = useState('')
  const filtered = entries.filter(e => e.description.toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Journal Entries</h1>
          <p className="text-muted-foreground">Double-entry bookkeeping</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-eco-600 text-white rounded-lg hover:bg-eco-700">
          <Plus className="w-4 h-4" /> New Entry
        </button>
      </div>
      <div className="rounded-xl border bg-card shadow-sm p-4">
        <div className="relative mb-4">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search entries..." className="w-full md:w-96 pr-10 pl-4 py-2 border rounded-lg text-sm" />
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-muted/50">
              <th className="text-right p-4">Date</th>
              <th className="text-right p-4">Description</th>
              <th className="text-right p-4">Lines</th>
              <th className="text-right p-4">Debit</th>
              <th className="text-right p-4">Credit</th>
              <th className="text-right p-4">Status</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(entry => (
              <tr key={entry.id} className="border-b last:border-0 hover:bg-muted/30">
                <td className="p-4 font-mono">{entry.entry_date}</td>
                <td className="p-4 font-medium">{entry.description}</td>
                <td className="p-4 text-center">{entry.lines_count}</td>
                <td className="p-4 font-medium">{entry.total_debit.toLocaleString()}</td>
                <td className="p-4 font-medium">{entry.total_credit.toLocaleString()}</td>
                <td className="p-4">
                  <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs ${entry.is_posted ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-800'}`}>
                    {entry.is_posted && <CheckCircle2 className="w-3 h-3" />}
                    {entry.is_posted ? 'Posted' : 'Draft'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}