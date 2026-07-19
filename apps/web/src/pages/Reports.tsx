import { FileText, Download, Eye } from 'lucide-react'
import Header from '../components/Header'

const templates = [
  { id: 1, name: 'Village Agricultural Report', desc: 'Comprehensive report per village including fields, farmers, production', format: 'PDF', date: '01 Jun 2025' },
  { id: 2, name: 'District Summary Report', desc: 'District-level summary of all agricultural activities', format: 'PDF', date: '01 Jun 2025' },
  { id: 3, name: 'Productivity Report', desc: 'Yield and productivity analysis by field, village, and variety', format: 'Excel', date: '01 Jun 2025' },
  { id: 4, name: 'Fertilizer Usage Report', desc: 'Fertilizer consumption, cost, and efficiency analysis', format: 'Excel', date: '31 May 2025' },
  { id: 5, name: 'Food Security Report', desc: 'Production vs target, surplus/deficit analysis', format: 'PDF', date: '30 May 2025' },
  { id: 6, name: 'Irrigation & Water Report', desc: 'Water consumption, pump usage, and electricity costs', format: 'CSV', date: '30 May 2025' },
]

const formatBadge: Record<string, string> = {
  PDF: 'badge-red',
  Excel: 'badge-green',
  CSV: 'badge-blue',
}

export default function Reports() {
  return (
    <div className="flex flex-col h-full overflow-hidden">
      <Header title="Reports" subtitle="Generate and export agricultural reports" />
      <div className="flex-1 overflow-y-auto p-6 space-y-6">

        <div className="grid grid-cols-3 gap-4">
          {[
            { label: 'Reports Generated', value: '1,248', sub: 'This season' },
            { label: 'Last Generated', value: 'Today, 09:42', sub: 'Village Report' },
            { label: 'Export Formats', value: 'PDF, Excel, CSV', sub: 'Available' },
          ].map(({ label, value, sub }) => (
            <div key={label} className="card p-4">
              <p className="text-xs text-gray-500 dark:text-gray-400">{label}</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white mt-1">{value}</p>
              <p className="text-xs text-gray-400 mt-0.5">{sub}</p>
            </div>
          ))}
        </div>

        <div className="card overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100 dark:border-gray-800">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Report Templates</h3>
          </div>
          <div className="divide-y divide-gray-50 dark:divide-gray-800/50">
            {templates.map(t => (
              <div key={t.id} className="flex items-center gap-4 px-5 py-4 hover:bg-gray-50/50 dark:hover:bg-gray-800/30 transition-colors">
                <div className="w-10 h-10 rounded-xl bg-green-50 dark:bg-green-900/20 flex items-center justify-center shrink-0">
                  <FileText className="w-5 h-5 text-green-700 dark:text-green-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-800 dark:text-gray-200">{t.name}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{t.desc}</p>
                </div>
                <span className={`badge ${formatBadge[t.format]}`}>{t.format}</span>
                <span className="text-xs text-gray-400 w-24 text-right">{t.date}</span>
                <div className="flex items-center gap-1 ml-2">
                  <button className="btn-secondary flex items-center gap-1.5 text-xs py-1.5">
                    <Eye className="w-3.5 h-3.5" /> Preview
                  </button>
                  <button className="btn-primary flex items-center gap-1.5 text-xs py-1.5">
                    <Download className="w-3.5 h-3.5" /> Export
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
