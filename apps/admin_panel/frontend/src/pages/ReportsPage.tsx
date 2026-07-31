import { useState, useEffect } from 'react'
import { Plus, Loader2, AlertCircle, RefreshCw, CheckCircle2, Clock, XCircle } from 'lucide-react'
import { fetchReports, generateReport, SystemReport } from '../api/adminApi'

export default function ReportsPage() {
  const [reports, setReports] = useState<SystemReport[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showGenerate, setShowGenerate] = useState(false)
  const [reportName, setReportName] = useState('')
  const [reportType, setReportType] = useState('csv')
  const [generating, setGenerating] = useState(false)

  const loadReports = () => {
    setLoading(true)
    setError(null)
    fetchReports(200, 0)
      .then(setReports)
      .catch(err => setError(err?.message || 'Failed to load reports'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { loadReports() }, [])

  const handleGenerate = async () => {
    if (!reportName) return
    setGenerating(true)
    try {
      const result = await generateReport(reportName, reportType)
      setReports([...reports, {
        id: result.id,
        report_name: result.report_name,
        status: result.status,
        report_data: null,
        created_at: new Date().toISOString(),
        completed_at: new Date().toISOString(),
      }])
      setShowGenerate(false)
      setReportName('')
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to generate report')
    } finally {
      setGenerating(false)
    }
  }

  const statusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle2 className="w-4 h-4 text-green-600" />;
      case 'running': return <Clock className="w-4 h-4 text-amber-600" />;
      case 'failed': return <XCircle className="w-4 h-4 text-red-600" />;
      default: return <Clock className="w-4 h-4 text-muted-foreground" />;
    }
  }

  const totalCompleted = reports.filter(r => r.status === 'completed').length

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Reports</h1>
          <p className="text-muted-foreground">System reports &bull; {totalCompleted} completed</p>
        </div>
        <div className="flex gap-2">
          <button onClick={loadReports} className="flex items-center gap-2 px-3 py-2 border rounded-lg hover:bg-accent text-sm">
            <RefreshCw className="w-4 h-4" /> Refresh
          </button>
          <button onClick={() => setShowGenerate(!showGenerate)} className="flex items-center gap-2 px-4 py-2 bg-eco-600 text-white rounded-lg hover:bg-eco-700 text-sm">
            <Plus className="w-4 h-4" /> Generate Report
          </button>
        </div>
      </div>

      {/* Generate Form */}
      {showGenerate && (
        <div className="rounded-xl border bg-card p-6 shadow-sm">
          <h3 className="font-semibold mb-4">Generate New Report</h3>
          <div className="flex items-end gap-3">
            <div className="flex-1">
              <label className="text-xs text-muted-foreground mb-1 block">Report Name</label>
              <input value={reportName} onChange={e => setReportName(e.target.value)} placeholder="e.g. Monthly Summary" className="w-full px-4 py-2 border rounded-lg text-sm" />
            </div>
            <div>
              <label className="text-xs text-muted-foreground mb-1 block">Format</label>
              <select value={reportType} onChange={e => setReportType(e.target.value)} className="px-4 py-2 border rounded-lg text-sm">
                <option value="csv">CSV</option>
                <option value="json">JSON</option>
              </select>
            </div>
            <button onClick={handleGenerate} disabled={generating || !reportName} className="px-6 py-2 bg-eco-600 text-white rounded-lg hover:bg-eco-700 text-sm disabled:opacity-50">
              {generating ? 'Generating...' : 'Generate'}
            </button>
            <button onClick={() => setShowGenerate(false)} className="px-4 py-2 border rounded-lg text-sm">Cancel</button>
          </div>
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          {error}
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-eco-600" />
        </div>
      )}

      {!loading && (
        <div className="rounded-xl border bg-card shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="text-right p-4">ID</th>
                  <th className="text-right p-4">Report Name</th>
                  <th className="text-right p-4">Status</th>
                  <th className="text-right p-4">Data</th>
                  <th className="text-right p-4">Created</th>
                  <th className="text-right p-4">Completed</th>
                </tr>
              </thead>
              <tbody>
                {reports.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="p-8 text-center text-muted-foreground">No reports generated yet</td>
                  </tr>
                ) : (
                  reports.map((report) => (
                    <tr key={report.id} className="border-b last:border-0 hover:bg-muted/30">
                      <td className="p-4 font-mono text-xs">{report.id}</td>
                      <td className="p-4 font-medium">{report.report_name}</td>
                      <td className="p-4">
                        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs capitalize"
                          style={{
                            backgroundColor: report.status === 'completed' ? '#dcfce7' : report.status === 'failed' ? '#fee2e2' : '#fef3c7',
                            color: report.status === 'completed' ? '#166534' : report.status === 'failed' ? '#991b1b' : '#92400e',
                          }}
                        >
                          {statusIcon(report.status)}
                          {report.status}
                        </span>
                      </td>
                      <td className="p-4 max-w-[200px] truncate text-muted-foreground text-xs font-mono">
                        {report.report_data || '—'}
                      </td>
                      <td className="p-4 text-muted-foreground text-xs">
                        {new Date(report.created_at).toLocaleString()}
                      </td>
                      <td className="p-4 text-muted-foreground text-xs">
                        {report.completed_at ? new Date(report.completed_at).toLocaleString() : '—'}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}