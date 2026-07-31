import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@econojin/ui/card';
import { Label } from '@econojin/ui/label';
import { Switch } from '@econojin/ui/switch';
import { Slider } from '@econojin/ui/slider';
import { Input } from '@econojin/ui/input';
import { Button } from '@econojin/ui/button';
import { useTheme } from '../contexts/ThemeContext';
import ThemeSelector from '../components/ThemeSelector';
import { Palette, Languages, Type, Monitor } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function Settings() {
  const { 
    theme, 
    themeColors, 
    setTheme, 
    setCustomColors, 
    toggleRTL, 
    isRTL 
  } = useTheme();
  
  const [fontSize, setFontSize] = useState<number>(() => {
    const savedSize = localStorage.getItem('font-size');
    return savedSize ? parseInt(savedSize) : 16;
  });
  
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(() => {
    const saved = localStorage.getItem('sidebar-collapsed');
    return saved === 'true';
  });
  
  const [customPrimaryColor, setCustomPrimaryColor] = useState<string>(themeColors.primary || '#15803d');
  const [customSecondaryColor, setCustomSecondaryColor] = useState<string>(themeColors.secondary || '#bbf7d0');
  const [customAccentColor, setCustomAccentColor] = useState<string>(themeColors.accent || '#22c55e');

  // Apply font size to document
  useEffect(() => {
    document.documentElement.style.fontSize = `${fontSize}px`;
    localStorage.setItem('font-size', fontSize.toString());
  }, [fontSize]);

  // Apply sidebar collapsed state
  useEffect(() => {
    localStorage.setItem('sidebar-collapsed', sidebarCollapsed.toString());
    if (sidebarCollapsed) {
      document.body.classList.add('sidebar-collapsed');
    } else {
      document.body.classList.remove('sidebar-collapsed');
    }
  }, [sidebarCollapsed]);

  const handleSaveCustomColors = () => {
    setCustomColors({
      primary: customPrimaryColor,
      secondary: customSecondaryColor,
      accent: customAccentColor
    });
  };

  const resetToDefault = () => {
    setCustomColors({});
    setCustomPrimaryColor('#15803d');
    setCustomSecondaryColor('#bbf7d0');
    setCustomAccentColor('#22c55e');
    setFontSize(16);
    setSidebarCollapsed(false);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">تنظیمات ظاهر</h1>
        <p className="text-muted-foreground">
          تنظیم تم، زبان و سایر تنظیمات رابط کاربری
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Appearance Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Palette className="w-5 h-5" />
              تنظیمات ظاهر
            </CardTitle>
            <CardDescription>
              تنظیم تم، رنگ‌ها و سایر ویژگی‌های ظاهری
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label>انتخاب تم</Label>
              <ThemeSelector />
            </div>
            
            <div className="space-y-4">
              <Label>رنگ‌های سفارشی</Label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="primary-color">رنگ اصلی</Label>
                  <div className="flex items-center gap-2">
                    <Input
                      id="primary-color"
                      type="color"
                      value={customPrimaryColor}
                      onChange={(e) => setCustomPrimaryColor(e.target.value)}
                      className="w-12 h-10 p-1"
                    />
                    <Input
                      type="text"
                      value={customPrimaryColor}
                      onChange={(e) => setCustomPrimaryColor(e.target.value)}
                      className="flex-1"
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="secondary-color">رنگ ثانویه</Label>
                  <div className="flex items-center gap-2">
                    <Input
                      id="secondary-color"
                      type="color"
                      value={customSecondaryColor}
                      onChange={(e) => setCustomSecondaryColor(e.target.value)}
                      className="w-12 h-10 p-1"
                    />
                    <Input
                      type="text"
                      value={customSecondaryColor}
                      onChange={(e) => setCustomSecondaryColor(e.target.value)}
                      className="flex-1"
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="accent-color">رنگ لهجه</Label>
                  <div className="flex items-center gap-2">
                    <Input
                      id="accent-color"
                      type="color"
                      value={customAccentColor}
                      onChange={(e) => setCustomAccentColor(e.target.value)}
                      className="w-12 h-10 p-1"
                    />
                    <Input
                      type="text"
                      value={customAccentColor}
                      onChange={(e) => setCustomAccentColor(e.target.value)}
                      className="flex-1"
                    />
                  </div>
                </div>
              </div>
              
              <Button onClick={handleSaveCustomColors} className="w-full">
                ذخیره رنگ‌های سفارشی
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Accessibility Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Monitor className="w-5 h-5" />
              تنظیمات دسترسی‌پذیری
            </CardTitle>
            <CardDescription>
              تنظیمات مربوط به دسترسی‌پذیری و کاربرپذیری
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-base">چینش راست به چپ</Label>
                <p className="text-sm text-muted-foreground">
                  فعال‌سازی چینش راست به چپ برای زبان‌های فارسی/عربی
                </p>
              </div>
              <Switch
                checked={isRTL}
                onCheckedChange={toggleRTL}
                aria-label="تغییر وضعیت چینش راست به چپ"
              />
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-base">اندازه فونت</Label>
                  <p className="text-sm text-muted-foreground">
                    تغییر اندازه فونت پایه سیستم ({fontSize}px)
                  </p>
                </div>
              </div>
              <Slider
                defaultValue={[fontSize]}
                max={24}
                min={12}
                step={1}
                onValueChange={([value]) => setFontSize(value)}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>کوچک</span>
                <span>متوسط</span>
                <span>بزرگ</span>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-base">جمع شدن نوار کناری</Label>
                <p className="text-sm text-muted-foreground">
                  جمع کردن نوار کناری برای فضای بیشتر
                </p>
              </div>
              <Switch
                checked={sidebarCollapsed}
                onCheckedChange={setSidebarCollapsed}
                aria-label="تغییر وضعیت جمع شدن نوار کناری"
              />
            </div>
          </CardContent>
        </Card>

        {/* Reset Settings */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>بازنشانی تنظیمات</CardTitle>
            <CardDescription>
              بازنشانی تمام تنظیمات ظاهر به مقادیر پیش‌فرض
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              variant="destructive"
              onClick={resetToDefault}
            >
              بازنشانی همه تنظیمات
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
</content>

<write_to_file>
<path>apps/admin_panel/frontend/src/pages/AuditLogsPage.tsx</path>
<content>import { useState, useEffect } from 'react'
import { Search, Filter, Loader2, AlertCircle, RefreshCw, Calendar } from 'lucide-react'
import { fetchAuditLogs, AuditLog } from '../api/adminApi'

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [eventType, setEventType] = useState('')
  const [actorEmail, setActorEmail] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')

  const loadLogs = () => {
    setLoading(true)
    setError(null)
    const params: any = { limit: 100 }
    if (eventType) params.event_type = eventType
    if (actorEmail) params.actor_email = actorEmail
    if (dateFrom) params.date_from = new Date(dateFrom).toISOString()
    if (dateTo) params.date_to = new Date(dateTo).toISOString()

    fetchAuditLogs(params)
      .then(setLogs)
      .catch(err => setError(err?.message || 'Failed to load audit logs'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { loadLogs() }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Audit Logs</h1>
          <p className="text-muted-foreground">System audit trail &bull; {logs.length} entries</p>
        </div>
        <button onClick={loadLogs} className="flex items-center gap-2 px-3 py-2 border rounded-lg hover:bg-accent text-sm">
          <RefreshCw className="w-4 h-4" /> Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="rounded-xl border bg-card p-4 shadow-sm">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
          <div className="relative">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input value={eventType} onChange={e => setEventType(e.target.value)} placeholder="Event type (e.g. login)" className="w-full pr-10 pl-4 py-2 border rounded-lg text-sm" />
          </div>
          <div>
            <input value={actorEmail} onChange={e => setActorEmail(e.target.value)} placeholder="Actor email" className="w-full px-4 py-2 border rounded-lg text-sm" />
          </div>
          <div className="relative">
            <Calendar className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)} className="w-full pr-10 pl-4 py-2 border rounded-lg text-sm" />
          </div>
          <div className="relative">
            <Calendar className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input type="date" value={dateTo} onChange={e => setDateTo(e.target.value)} className="w-full pr-10 pl-4 py-2 border rounded-lg text-sm" />
          </div>
          <button onClick={loadLogs} className="flex items-center justify-center gap-2 px-4 py-2 bg-eco-600 text-white rounded-lg hover:bg-eco-700 text-sm">
            <Filter className="w-4 h-4" /> Filter
          </button>
        </div>
      </div>

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
                  <th className="text-right p-4">Event Type</th>
                  <th className="text-right p-4">Actor</th>
                  <th className="text-right p-4">Data</th>
                  <th className="text-right p-4">Created At</th>
                </tr>
              </thead>
              <tbody>
                {logs.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-muted-foreground">No audit logs found</td>
                  </tr>
                ) : (
                  logs.map((log) => (
                    <tr key={log.id} className="border-b last:border-0 hover:bg-muted/30">
                      <td className="p-4 font-mono text-xs">{log.id}</td>
                      <td className="p-4">
                        <span className="px-2 py-1 rounded-full bg-blue-100 text-blue-800 text-xs capitalize">
                          {log.event_type}
                        </span>
                      </td>
                      <td className="p-4">
                        <span className="text-sm">{log.actor_email || 'system'}</span>
                      </td>
                      <td className="p-4 max-w-[200px] truncate text-muted-foreground text-xs font-mono">
                        {log.event_data || '—'}
                      </td>
                      <td className="p-4 text-muted-foreground text-xs">
                        {new Date(log.created_at).toLocaleString()}
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
</content>

<write_to_file>
<path>apps/admin_panel/frontend/src/pages/ReportsPage.tsx</path>
<content>import { useState, useEffect } from 'react'
import { Plus, Loader2, AlertCircle, RefreshCw, Download, CheckCircle2, Clock, XCircle } from 'lucide-react'
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