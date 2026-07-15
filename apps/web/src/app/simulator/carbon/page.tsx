'use client'
import { useState } from 'react'
import { motion } from 'framer-motion'
import { Leaf, Play, Download, TrendingUp } from 'lucide-react'
import { AreaChart, Area, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { PageHeader } from '@/components/shared/PageHeader'
import { StatCard } from '@/components/shared/StatCard'
import { ChartCard } from '@/components/shared/ChartCard'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

export default function CarbonSimulator() {
  const [params, setParams] = useState({ area_hectares: 100, forest_type: 'rainforest', years: 10 })
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const run = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/simulator/carbon/run', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(params) })
      setResult(await res.json())
    } finally { setLoading(false) }
  }

  const chartData = result?.chart_data?.labels?.map((label: string, i: number) => ({
    name: label, 'جذب سالانه': result.chart_data.annual[i], 'تجمعی': result.chart_data.cumulative[i]
  })) || []

  return (
    <div className='container mx-auto px-4 py-8'>
      <PageHeader title='شبیه‌ساز کربن' description='محاسبه جذب CO₂ و پاداش ECO' icon={Leaf} color='text-green-500' />
      <div className='grid lg:grid-cols-3 gap-6 mb-8'>
        <Card className='lg:col-span-1'>
          <CardHeader><CardTitle>پارامترها</CardTitle></CardHeader>
          <CardContent className='space-y-4'>
            <div className='space-y-2'><Label>مساحت (هکتار)</Label><Input type='number' value={params.area_hectares} onChange={e => setParams({ ...params, area_hectares: +e.target.value })} /></div>
            <div className='space-y-2'><Label>نوع جنگل</Label>
              <Select value={params.forest_type} onValueChange={v => setParams({ ...params, forest_type: v })}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value='rainforest'>🌴 جنگل بارانی</SelectItem>
                  <SelectItem value='temperate'>🌳 جنگل معتدل</SelectItem>
                  <SelectItem value='mangrove'>🌊 جنگل حرا</SelectItem>
                  <SelectItem value='grassland'>🌾 مرتع</SelectItem>
                  <SelectItem value='boreal'>🌲 جنگل شمالی</SelectItem>
                  <SelectItem value='agroforestry'>🌱 آگروفارستری</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className='space-y-2'><Label>مدت زمان (سال)</Label><Input type='number' value={params.years} onChange={e => setParams({ ...params, years: +e.target.value })} /></div>
            <Button className='w-full bg-green-600 hover:bg-green-700' onClick={run} disabled={loading}><Play className='w-4 h-4 ml-2' />{loading ? 'در حال اجرا...' : 'اجرای شبیه‌سازی'}</Button>
          </CardContent>
        </Card>
        <div className='lg:col-span-2 space-y-6'>
          {result ? (
            <>
              <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
                <StatCard label='کل جذب CO₂' value={`${result.total_sequestration.toLocaleString()} تن`} icon={Leaf} color='text-green-500' bgColor='bg-green-500/10' delay={0} />
                <StatCard label='پاداش ECO' value={`${result.total_eco_reward.toLocaleString()} ECO`} icon={TrendingUp} color='text-purple-500' bgColor='bg-purple-500/10' delay={0.1} />
                <StatCard label='ارزش USD' value={`$${result.total_value_usd.toLocaleString()}`} icon={Download} color='text-blue-500' bgColor='bg-blue-500/10' delay={0.2} />
              </div>
              <ChartCard title='جذب کربن در طول زمان' icon={TrendingUp}>
                <ResponsiveContainer width='100%' height={350}>
                  <AreaChart data={chartData}>
                    <defs><linearGradient id='cg' x1='0' y1='0' x2='0' y2='1'><stop offset='5%' stopColor='#22c55e' stopOpacity={0.8} /><stop offset='95%' stopColor='#22c55e' stopOpacity={0} /></linearGradient></defs>
                    <CartesianGrid strokeDasharray='3 3' stroke='#e5e7eb' />
                    <XAxis dataKey='name' tick={{ fontSize: 11 }} /><YAxis tick={{ fontSize: 11 }} />
                    <Tooltip contentStyle={{ fontSize: '12px', borderRadius: '8px' }} /><Legend wrapperStyle={{ fontSize: '12px' }} />
                    <Area type='monotone' dataKey='جذب سالانه' stroke='#22c55e' fill='url(#cg)' strokeWidth={2} />
                    <Line type='monotone' dataKey='تجمعی' stroke='#3b82f6' strokeWidth={2} dot={false} />
                  </AreaChart>
                </ResponsiveContainer>
              </ChartCard>
              <Card>
                <CardHeader><CardTitle>جزئیات سالانه</CardTitle></CardHeader>
                <CardContent>
                  <div className='overflow-x-auto max-h-80 overflow-y-auto'>
                    <table className='w-full text-sm'>
                      <thead className='bg-muted/50 text-xs text-muted-foreground sticky top-0'>
                        <tr><th className='p-2 text-right'>سال</th><th className='p-2 text-right'>جذب سالانه</th><th className='p-2 text-right'>تجمعی</th><th className='p-2 text-right'>پاداش</th><th className='p-2 text-right'>USD</th></tr>
                      </thead>
                      <tbody>
                        {result.yearly_data.map((y: any, i: number) => (
                          <motion.tr key={i} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.03 }} className='border-t border-border'>
                            <td className='p-2'>{y.year}</td><td className='p-2 font-bold text-green-600'>{y.annual_sequestration.toLocaleString()} تن</td>
                            <td className='p-2'>{y.cumulative.toLocaleString()} تن</td><td className='p-2 text-purple-600'>{y.eco_reward.toLocaleString()}</td><td className='p-2 text-blue-600'>${y.carbon_value_usd.toLocaleString()}</td>
                          </motion.tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card className='flex items-center justify-center min-h-[400px]'><CardContent className='text-center'><Leaf className='w-16 h-16 mx-auto mb-4 text-green-500 opacity-50' /><p className='text-muted-foreground'>پارامترها را تنظیم و شبیه‌سازی را اجرا کنید</p></CardContent></Card>
          )}
        </div>
      </div>
    </div>
  )
}
