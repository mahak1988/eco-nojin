'use client'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Leaf, Play, Download, TrendingUp, Zap, Droplets, Wind, Sun } from 'lucide-react'
import { AreaChart, Area, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, ComposedChart, Bar } from 'recharts'
import { PageHeader } from '@/components/shared/PageHeader'
import { StatCard } from '@/components/shared/StatCard'
import { ChartCard } from '@/components/shared/ChartCard'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { Badge } from '@/components/ui/badge'

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

  const forestTypes = [
    { value: 'rainforest', label: '🌴 جنگل بارانی', rate: 'بالا', color: 'from-green-500 to-emerald-600' },
    { value: 'temperate', label: '🌳 جنگل معتدل', rate: 'متوسط', color: 'from-emerald-500 to-teal-600' },
    { value: 'mangrove', label: '🌊 جنگل حرا', rate: 'خیلی بالا', color: 'from-blue-500 to-cyan-600' },
    { value: 'grassland', label: '🌾 مرتع', rate: 'پایین', color: 'from-yellow-500 to-orange-600' },
    { value: 'boreal', label: '🌲 جنگل شمالی', rate: 'متوسط', color: 'from-indigo-500 to-purple-600' },
    { value: 'agroforestry', label: '🌱 آگروفارستری', rate: 'متوسط رو به بالا', color: 'from-lime-500 to-green-600' },
  ]

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 100 } }
  }

  return (
    <motion.div 
      className="container mx-auto px-4 py-8"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <motion.div variants={itemVariants}>
        <PageHeader title='شبیه‌ساز کربن' description='محاسبه جذب CO₂ و پاداش ECO' icon={Leaf} color='text-green-500' />
      </motion.div>

      <div className='grid lg:grid-cols-3 gap-6 mb-8'>
        {/* پنل پارامترها */}
        <motion.div variants={itemVariants}>
          <Card className='glass-card border-white/20 backdrop-blur-xl h-full'>
            <CardHeader>
              <CardTitle className='flex items-center gap-3'>
                <div className='p-2 rounded-lg bg-green-500/10'>
                  <Zap className='w-6 h-6 text-green-500' />
                </div>
                <span>پارامترهای شبیه‌سازی</span>
              </CardTitle>
            </CardHeader>
            <CardContent className='space-y-6'>
              <div className='space-y-3'>
                <Label className='font-semibold'>مساحت (هکتار)</Label>
                <div className='relative'>
                  <Input 
                    type='number' 
                    value={params.area_hectares} 
                    onChange={e => setParams({ ...params, area_hectares: +e.target.value })}
                    className='text-lg font-bold'
                  />
                  <Badge className='absolute left-3 top-1/2 -translate-y-1/2 bg-green-500/10 text-green-600 border-green-500/30'>
                    {params.area_hectares} هکتار
                  </Badge>
                </div>
                <Slider
                  value={[params.area_hectares]}
                  min={1}
                  max={10000}
                  step={1}
                  onValueChange={(v) => setParams({ ...params, area_hectares: v[0] })}
                  className='mt-2'
                />
              </div>

              <div className='space-y-3'>
                <Label className='font-semibold'>نوع جنگل</Label>
                <Select value={params.forest_type} onValueChange={v => setParams({ ...params, forest_type: v })}>
                  <SelectTrigger className='h-12'>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {forestTypes.map(type => (
                      <SelectItem key={type.value} value={type.value}>
                        <div className='flex items-center gap-2'>
                          <span>{type.label}</span>
                          <Badge variant='outline' className='ml-auto text-xs'>{type.rate}</Badge>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <div className='flex flex-wrap gap-2 mt-2'>
                  {forestTypes.map(type => (
                    <motion.button
                      key={type.value}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setParams({ ...params, forest_type: type.value })}
                      className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                        params.forest_type === type.value 
                          ? `bg-gradient-to-r ${type.color} text-white shadow-lg` 
                          : 'bg-muted hover:bg-muted/80'
                      }`}
                    >
                      {type.label.split(' ')[0]}
                    </motion.button>
                  ))}
                </div>
              </div>

              <div className='space-y-3'>
                <Label className='font-semibold'>مدت زمان (سال)</Label>
                <div className='flex items-center gap-4'>
                  <Input 
                    type='number' 
                    value={params.years} 
                    onChange={e => setParams({ ...params, years: +e.target.value })}
                    className='text-lg font-bold w-24'
                  />
                  <Slider
                    value={[params.years]}
                    min={1}
                    max={50}
                    step={1}
                    onValueChange={(v) => setParams({ ...params, years: v[0] })}
                    className='flex-1'
                  />
                </div>
              </div>

              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Button 
                  className='w-full h-14 text-lg bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 shadow-lg hover:shadow-green-500/25' 
                  onClick={run} 
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                        className='w-5 h-5 border-2 border-white border-t-transparent rounded-full mr-2'
                      />
                      در حال اجرا...
                    </>
                  ) : (
                    <>
                      <Play className='w-5 h-5 ml-2' />
                      اجرای شبیه‌سازی
                    </>
                  )}
                </Button>
              </motion.div>
            </CardContent>
          </Card>
        </motion.div>

        {/* نتایج */}
        <motion.div className='lg:col-span-2 space-y-6' variants={containerVariants}>
          <AnimatePresence mode='wait'>
            {result ? (
              <motion.div
                key='results'
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.3 }}
                className='space-y-6'
              >
                {/* کارت‌های آمار */}
                <motion.div 
                  className='grid grid-cols-1 md:grid-cols-3 gap-4'
                  variants={containerVariants}
                >
                  {[
                    { label: 'کل جذب CO₂', value: `${result.total_sequestration.toLocaleString()} تن`, icon: Leaf, color: 'text-green-500', bgColor: 'bg-green-500/10', delay: 0 },
                    { label: 'پاداش ECO', value: `${result.total_eco_reward.toLocaleString()} ECO`, icon: TrendingUp, color: 'text-purple-500', bgColor: 'bg-purple-500/10', delay: 0.1 },
                    { label: 'ارزش USD', value: `$${result.total_value_usd.toLocaleString()}`, icon: Download, color: 'text-blue-500', bgColor: 'bg-blue-500/10', delay: 0.2 },
                  ].map((stat, i) => (
                    <motion.div key={i} variants={itemVariants}>
                      <StatCard 
                        label={stat.label} 
                        value={stat.value} 
                        icon={stat.icon} 
                        color={stat.color} 
                        bgColor={stat.bgColor} 
                        delay={stat.delay} 
                      />
                    </motion.div>
                  ))}
                </motion.div>

                {/* نمودار */}
                <motion.div variants={itemVariants}>
                  <ChartCard title='جذب کربن در طول زمان' icon={TrendingUp}>
                    <ResponsiveContainer width='100%' height={350}>
                      <AreaChart data={chartData}>
                        <defs>
                          <linearGradient id='cg' x1='0' y1='0' x2='0' y2='1'>
                            <stop offset='5%' stopColor='#22c55e' stopOpacity={0.8} />
                            <stop offset='95%' stopColor='#22c55e' stopOpacity={0} />
                          </linearGradient>
                          <linearGradient id='cg2' x1='0' y1='0' x2='0' y2='1'>
                            <stop offset='5%' stopColor='#3b82f6' stopOpacity={0.8} />
                            <stop offset='95%' stopColor='#3b82f6' stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray='3 3' stroke='#e5e7eb' />
                        <XAxis dataKey='name' tick={{ fontSize: 11 }} />
                        <YAxis tick={{ fontSize: 11 }} />
                        <Tooltip contentStyle={{ fontSize: '12px', borderRadius: '8px', backdropFilter: 'blur(8px)' }} />
                        <Legend wrapperStyle={{ fontSize: '12px' }} />
                        <Area type='monotone' dataKey='جذب سالانه' stroke='#22c55e' fill='url(#cg)' strokeWidth={2} />
                        <Line type='monotone' dataKey='تجمعی' stroke='#3b82f6' strokeWidth={2} dot={false} />
                      </AreaChart>
                    </ResponsiveContainer>
                  </ChartCard>
                </motion.div>

                {/* جدول جزئیات */}
                <motion.div variants={itemVariants}>
                  <Card className='glass-card border-white/20 backdrop-blur-xl'>
                    <CardHeader>
                      <CardTitle className='flex items-center gap-3'>
                        <div className='p-2 rounded-lg bg-blue-500/10'>
                          <Download className='w-6 h-6 text-blue-500' />
                        </div>
                        <span>جزئیات سالانه</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className='overflow-x-auto max-h-96 overflow-y-auto scrollbar-thin'>
                        <table className='w-full text-sm'>
                          <thead className='bg-gradient-to-r from-green-500/10 to-emerald-500/10 text-xs text-muted-foreground sticky top-0 backdrop-blur-sm'>
                            <tr>
                              <th className='p-3 text-right rounded-r-lg'>سال</th>
                              <th className='p-3 text-right'>جذب سالانه</th>
                              <th className='p-3 text-right'>تجمعی</th>
                              <th className='p-3 text-right'>پاداش</th>
                              <th className='p-3 text-right rounded-l-lg'>USD</th>
                            </tr>
                          </thead>
                          <tbody>
                            {result.yearly_data.map((y: any, i: number) => (
                              <motion.tr 
                                key={i} 
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: i * 0.03 }}
                                className='border-t border-border hover:bg-accent/50 transition-colors'
                              >
                                <td className='p-3 font-medium'>{y.year}</td>
                                <td className='p-3 font-bold text-green-600'>{y.annual_sequestration.toLocaleString()} تن</td>
                                <td className='p-3'>{y.cumulative.toLocaleString()} تن</td>
                                <td className='p-3 text-purple-600 font-semibold'>{y.eco_reward.toLocaleString()}</td>
                                <td className='p-3 text-blue-600 font-semibold'>${y.carbon_value_usd.toLocaleString()}</td>
                              </motion.tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              </motion.div>
            ) : (
              <motion.div
                key='placeholder'
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                variants={itemVariants}
              >
                <Card className='glass-card border-white/20 backdrop-blur-xl flex items-center justify-center min-h-[500px]'>
                  <CardContent className='text-center'>
                    <motion.div
                      animate={{ 
                        y: [0, -10, 0],
                        rotate: [0, 5, -5, 0]
                      }}
                      transition={{ repeat: Infinity, duration: 3 }}
                    >
                      <Leaf className='w-24 h-24 mx-auto mb-6 text-green-500 opacity-30 drop-shadow-lg' />
                    </motion.div>
                    <p className='text-muted-foreground text-lg'>پارامترها را تنظیم و شبیه‌سازی را اجرا کنید</p>
                    <div className='flex justify-center gap-4 mt-6'>
                      {[
                        { icon: Droplets, label: 'آب', color: 'text-blue-500' },
                        { icon: Wind, label: 'کربن', color: 'text-green-500' },
                        { icon: Sun, label: 'انرژی', color: 'text-yellow-500' },
                      ].map((item, i) => (
                        <motion.div
                          key={i}
                          animate={{ y: [0, -5, 0] }}
                          transition={{ repeat: Infinity, duration: 2, delay: i * 0.3 }}
                          className={`p-3 rounded-xl bg-muted/50 ${item.color}`}
                        >
                          <item.icon className='w-6 h-6' />
                        </motion.div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </motion.div>
  )
}
