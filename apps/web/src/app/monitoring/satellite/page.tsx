'use client'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Satellite, MapPin, Activity, AlertTriangle, Sparkles, Zap } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, AreaChart, Area } from 'recharts'
import { PageHeader } from '@/components/shared/PageHeader'
import { StatCard } from '@/components/shared/StatCard'
import { ChartCard } from '@/components/shared/ChartCard'
import { FileUpload } from '@/components/shared/FileUpload'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

export default function SatelliteMonitoring() {
  const [params, setParams] = useState({ project_id: 'amazon-north', lat: -3.4653, lng: -62.2159, area_hectares: 1000, start_date: '2026-06-01', end_date: '2026-07-14' })
  const [result, setResult] = useState<any>(null)
  const [alerts, setAlerts] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  const analyze = async () => {
    setLoading(true)
    try { const res = await fetch('/api/monitoring/satellite/analyze', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(params) }); setResult(await res.json()) } finally { setLoading(false) }
  }

  useEffect(() => { fetch('/api/monitoring/alerts').then(r => r.json()).then(d => setAlerts(d.alerts || [])) }, [])

  const chartData = result?.chart_data?.labels?.map((label: string, i: number) => ({
    name: label, NDVI: result.chart_data.ndvi[i], NDWI: result.chart_data.ndwi[i], 'زیست‌توده': result.chart_data.biomass[i]
  })) || []

  return (
    <div className='relative min-h-screen overflow-hidden bg-gradient-to-br from-background via-background to-orange-500/5'>
      {/* Background Effects */}
      <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:32px]" />
      <div className="absolute top-0 right-0 h-96 w-96 rounded-full bg-orange-500/10 blur-3xl" />
      <div className="absolute bottom-0 left-0 h-96 w-96 rounded-full bg-red-500/10 blur-3xl" />
      
      <div className='relative container mx-auto px-4 py-8'>
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className='mb-8'
        >
          <PageHeader title='پایش ماهواره‌ای' description='تحلیل داده‌های Sentinel-2 و Landsat با هوش مصنوعی' icon={Satellite} color='text-orange-500' />
        </motion.div>
        
        {alerts.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className='mb-6'
          >
            <Card className='border-red-500/30 bg-gradient-to-br from-red-500/5 to-orange-500/5 backdrop-blur-xl'>
              <CardHeader><CardTitle className='flex items-center gap-2 text-red-600'><AlertTriangle className='w-5 h-5' /> هشدارهای فعال ({alerts.length})</CardTitle></CardHeader>
              <CardContent className='space-y-2'>
                {alerts.map((a, i) => (
                  <motion.div key={i} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }} className='flex items-center justify-between p-4 rounded-xl border border-border/50 hover:bg-red-500/5 transition-colors'>
                    <div className='flex items-center gap-3'>
                      <Badge variant='outline' className={a.severity === 'high' ? 'text-red-600 border-red-500/30 bg-red-500/10' : 'text-yellow-600 border-yellow-500/30 bg-yellow-500/10'}>{a.severity === 'high' ? '🔴 بحرانی' : '🟡 متوسط'}</Badge>
                      <div><div className='text-sm font-medium'>{a.message}</div><div className='text-xs text-muted-foreground'>{a.type}</div></div>
                    </div>
                  </motion.div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        )}
        
        <div className='grid lg:grid-cols-3 gap-6'>
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className='bg-card/50 backdrop-blur-xl border-border/50'>
              <CardHeader><CardTitle className='flex items-center gap-2'><MapPin className='w-5 h-5 text-orange-500' /> پارامترها</CardTitle></CardHeader>
              <CardContent className='space-y-4'>
                <div className='space-y-2'><Label>شناسه پروژه</Label><Input value={params.project_id} onChange={e => setParams({ ...params, project_id: e.target.value })} className='bg-background/50' /></div>
                <div className='grid grid-cols-2 gap-2'>
                  <div className='space-y-2'><Label>عرض جغرافیایی</Label><Input type='number' step='0.0001' value={params.lat} onChange={e => setParams({ ...params, lat: +e.target.value })} className='bg-background/50' /></div>
                  <div className='space-y-2'><Label>طول جغرافیایی</Label><Input type='number' step='0.0001' value={params.lng} onChange={e => setParams({ ...params, lng: +e.target.value })} className='bg-background/50' /></div>
                </div>
                <div className='space-y-2'><Label>مساحت (هکتار)</Label><Input type='number' value={params.area_hectares} onChange={e => setParams({ ...params, area_hectares: +e.target.value })} className='bg-background/50' /></div>
                <Button className='w-full bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 shadow-lg shadow-orange-500/20' onClick={analyze} disabled={loading}>
                  <Satellite className='w-4 h-4 ml-2' />
                  {loading ? 'در حال تحلیل...' : 'تحلیل ماهواره‌ای'}
                </Button>
              </CardContent>
            </Card>
          </motion.div>
          
          <div className='lg:col-span-2 space-y-6'>
            {result && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.3 }}
              >
                <div className='grid grid-cols-2 md:grid-cols-4 gap-4 mb-6'>
                  <StatCard label='NDVI' value={result.indices.ndvi.avg} icon={Activity} color='text-green-500' bgColor='bg-green-500/10' delay={0} />
                  <StatCard label='NDWI' value={result.indices.ndwi.avg} icon={Activity} color='text-blue-500' bgColor='bg-blue-500/10' delay={0.1} />
                  <StatCard label='زیست‌توده (تن)' value={result.biomass_estimate.total_tons.toLocaleString()} icon={Activity} color='text-purple-500' bgColor='bg-purple-500/10' delay={0.2} />
                  <StatCard label='امتیاز سلامت' value={`${result.health_score}/100`} icon={Sparkles} color='text-emerald-500' bgColor='bg-emerald-500/10' delay={0.3} />
                </div>
                <ChartCard title='روند شاخص‌های بوم‌شناختی' icon={Activity}>
                  <ResponsiveContainer width='100%' height={300}>
                    <AreaChart data={chartData}>
                      <defs>
                        <linearGradient id='g1' x1='0' y1='0' x2='0' y2='1'><stop offset='5%' stopColor='#22c55e' stopOpacity={0.8} /><stop offset='95%' stopColor='#22c55e' stopOpacity={0} /></linearGradient>
                        <linearGradient id='g2' x1='0' y1='0' x2='0' y2='1'><stop offset='5%' stopColor='#3b82f6' stopOpacity={0.6} /><stop offset='95%' stopColor='#3b82f6' stopOpacity={0} /></linearGradient>
                        <linearGradient id='g3' x1='0' y1='0' x2='0' y2='1'><stop offset='5%' stopColor='#a855f7' stopOpacity={0.6} /><stop offset='95%' stopColor='#a855f7' stopOpacity={0} /></linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray='3 3' stroke='#e5e7eb' />
                      <XAxis dataKey='name' tick={{ fontSize: 10 }} /><YAxis tick={{ fontSize: 10 }} />
                      <Tooltip contentStyle={{ fontSize: '12px', borderRadius: '8px', backdropFilter: 'blur(8px)', background: 'rgba(255,255,255,0.9)' }} /><Legend wrapperStyle={{ fontSize: '12px' }} />
                      <Area type='monotone' dataKey='NDVI' stroke='#22c55e' fill='url(#g1)' strokeWidth={2} />
                      <Area type='monotone' dataKey='NDWI' stroke='#3b82f6' fill='url(#g2)' strokeWidth={2} />
                      <Area type='monotone' dataKey='زیست‌توده' stroke='#a855f7' fill='url(#g3)' strokeWidth={2} />
                    </AreaChart>
                  </ResponsiveContainer>
                </ChartCard>
              </motion.div>
            )}
          </div>
        </div>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className='mt-6'
        >
          <Card className='bg-card/50 backdrop-blur-xl border-border/50'>
            <CardHeader><CardTitle className='flex items-center gap-2'><Zap className='w-5 h-5 text-yellow-500' /> آپلود تصویر ماهواره‌ای</CardTitle></CardHeader>
            <CardContent><FileUpload accept='image/*' onUpload={async (file) => { const fd = new FormData(); fd.append('file', file); await fetch('/api/monitoring/satellite/upload', { method: 'POST', body: fd }) }} label='تصویر ماهواره‌ای را آپلود کنید' /></CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}
