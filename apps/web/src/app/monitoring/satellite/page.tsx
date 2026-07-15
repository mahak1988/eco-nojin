'use client'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Satellite, MapPin, Activity, AlertTriangle } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
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
    <div className='container mx-auto px-4 py-8'>
      <PageHeader title='پایش ماهواره‌ای' description='تحلیل داده‌های Sentinel-2 و Landsat' icon={Satellite} color='text-orange-500' />
      {alerts.length > 0 && (
        <Card className='mb-6 border-red-500/30'>
          <CardHeader><CardTitle className='flex items-center gap-2 text-red-600'><AlertTriangle className='w-5 h-5' /> هشدارهای فعال ({alerts.length})</CardTitle></CardHeader>
          <CardContent className='space-y-2'>
            {alerts.map((a, i) => (
              <motion.div key={i} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }} className='flex items-center justify-between p-3 rounded-lg border border-border'>
                <div className='flex items-center gap-3'>
                  <Badge variant='outline' className={a.severity === 'high' ? 'text-red-600 border-red-500/30' : 'text-yellow-600 border-yellow-500/30'}>{a.severity === 'high' ? '🔴 بحرانی' : '🟡 متوسط'}</Badge>
                  <div><div className='text-sm font-medium'>{a.message}</div><div className='text-xs text-muted-foreground'>{a.type}</div></div>
                </div>
              </motion.div>
            ))}
          </CardContent>
        </Card>
      )}
      <div className='grid lg:grid-cols-3 gap-6'>
        <Card>
          <CardHeader><CardTitle className='flex items-center gap-2'><MapPin className='w-5 h-5' /> پارامترها</CardTitle></CardHeader>
          <CardContent className='space-y-4'>
            <div className='space-y-2'><Label>شناسه پروژه</Label><Input value={params.project_id} onChange={e => setParams({ ...params, project_id: e.target.value })} /></div>
            <div className='grid grid-cols-2 gap-2'>
              <div className='space-y-2'><Label>عرض جغرافیایی</Label><Input type='number' step='0.0001' value={params.lat} onChange={e => setParams({ ...params, lat: +e.target.value })} /></div>
              <div className='space-y-2'><Label>طول جغرافیایی</Label><Input type='number' step='0.0001' value={params.lng} onChange={e => setParams({ ...params, lng: +e.target.value })} /></div>
            </div>
            <div className='space-y-2'><Label>مساحت (هکتار)</Label><Input type='number' value={params.area_hectares} onChange={e => setParams({ ...params, area_hectares: +e.target.value })} /></div>
            <Button className='w-full bg-orange-600 hover:bg-orange-700' onClick={analyze} disabled={loading}><Satellite className='w-4 h-4 ml-2' />{loading ? 'در حال تحلیل...' : 'تحلیل ماهواره‌ای'}</Button>
          </CardContent>
        </Card>
        <div className='lg:col-span-2 space-y-6'>
          {result && (
            <>
              <div className='grid grid-cols-2 md:grid-cols-4 gap-4'>
                <StatCard label='NDVI' value={result.indices.ndvi.avg} icon={Activity} color='text-green-500' bgColor='bg-green-500/10' delay={0} />
                <StatCard label='NDWI' value={result.indices.ndwi.avg} icon={Activity} color='text-blue-500' bgColor='bg-blue-500/10' delay={0.1} />
                <StatCard label='زیست‌توده (تن)' value={result.biomass_estimate.total_tons.toLocaleString()} icon={Activity} color='text-purple-500' bgColor='bg-purple-500/10' delay={0.2} />
                <StatCard label='امتیاز سلامت' value={`${result.health_score}/100`} icon={Activity} color='text-emerald-500' bgColor='bg-emerald-500/10' delay={0.3} />
              </div>
              <ChartCard title='روند شاخص‌های بوم‌شناختی' icon={Activity}>
                <ResponsiveContainer width='100%' height={300}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray='3 3' stroke='#e5e7eb' />
                    <XAxis dataKey='name' tick={{ fontSize: 10 }} /><YAxis tick={{ fontSize: 10 }} />
                    <Tooltip contentStyle={{ fontSize: '12px', borderRadius: '8px' }} /><Legend wrapperStyle={{ fontSize: '12px' }} />
                    <Line type='monotone' dataKey='NDVI' stroke='#22c55e' strokeWidth={2} />
                    <Line type='monotone' dataKey='NDWI' stroke='#3b82f6' strokeWidth={2} />
                    <Line type='monotone' dataKey='زیست‌توده' stroke='#a855f7' strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </ChartCard>
            </>
          )}
        </div>
      </div>
      <Card className='mt-6'>
        <CardHeader><CardTitle>آپلود تصویر ماهواره‌ای</CardTitle></CardHeader>
        <CardContent><FileUpload accept='image/*' onUpload={async (file) => { const fd = new FormData(); fd.append('file', file); await fetch('/api/monitoring/satellite/upload', { method: 'POST', body: fd }) }} label='تصویر ماهواره‌ای را آپلود کنید' /></CardContent>
      </Card>
    </div>
  )
}
