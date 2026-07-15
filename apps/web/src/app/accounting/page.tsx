'use client'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Wallet, TrendingUp, TrendingDown, Receipt, DollarSign, FileText, Download } from 'lucide-react'
import { AreaChart, Area, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { PageHeader } from '@/components/shared/PageHeader'
import { StatCard } from '@/components/shared/StatCard'
import { ChartCard } from '@/components/shared/ChartCard'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

export default function AccountingDashboard() {
  const [summary, setSummary] = useState<any>(null)
  const [chart, setChart] = useState<any>(null)
  const [cats, setCats] = useState<any[]>([])
  const [txs, setTxs] = useState<any[]>([])

  useEffect(() => {
    fetch('/api/accounting/summary').then(r => r.json()).then(setSummary)
    fetch('/api/accounting/charts/income-expense').then(r => r.json()).then(setChart)
    fetch('/api/accounting/charts/category-distribution').then(r => r.json()).then(setCats)
    fetch('/api/accounting/transactions?limit=5').then(r => r.json()).then(d => setTxs(d.transactions || []))
  }, [])

  const data = chart ? chart.labels.map((l: string, i: number) => ({
    name: l, 'درآمد': chart.income[i], 'هزینه': chart.expense[i], 'سود': chart.profit[i]
  })) : []

  const typeColors: Record<string, string> = { income: 'text-green-600', expense: 'text-red-600', transfer: 'text-blue-600', eco_reward: 'text-purple-600', carbon_credit: 'text-orange-600' }
  const typeLabels: Record<string, string> = { income: 'درآمد', expense: 'هزینه', transfer: 'انتقال', eco_reward: 'پاداش ECO', carbon_credit: 'اعتبار کربن' }

  return (
    <div className='container mx-auto px-4 py-8'>
      <PageHeader title='حسابداری' description='مدیریت مالی و گزارش‌گیری Econojin' icon={Wallet} />
      <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8'>
        <StatCard label='کل درآمد' value={summary ? `$${summary.total_income.toLocaleString()}` : '...'} icon={TrendingUp} color='text-green-500' bgColor='bg-green-500/10' trend={12.5} delay={0} />
        <StatCard label='کل هزینه' value={summary ? `$${summary.total_expense.toLocaleString()}` : '...'} icon={TrendingDown} color='text-red-500' bgColor='bg-red-500/10' trend={-5.2} delay={0.1} />
        <StatCard label='سود خالص' value={summary ? `$${summary.net_profit.toLocaleString()}` : '...'} icon={DollarSign} color='text-blue-500' bgColor='bg-blue-500/10' trend={18.3} delay={0.2} />
        <StatCard label='پاداش ECO' value={summary ? `${summary.eco_rewards_distributed} ECO` : '...'} icon={Receipt} color='text-purple-500' bgColor='bg-purple-500/10' trend={8.7} delay={0.3} />
      </div>
      <div className='grid lg:grid-cols-2 gap-6 mb-8'>
        <ChartCard title='درآمد و هزینه' icon={TrendingUp} delay={0.4}>
          <ResponsiveContainer width='100%' height={300}>
            <AreaChart data={data}>
              <defs>
                <linearGradient id='g1' x1='0' y1='0' x2='0' y2='1'><stop offset='5%' stopColor='#22c55e' stopOpacity={0.8} /><stop offset='95%' stopColor='#22c55e' stopOpacity={0} /></linearGradient>
                <linearGradient id='g2' x1='0' y1='0' x2='0' y2='1'><stop offset='5%' stopColor='#ef4444' stopOpacity={0.6} /><stop offset='95%' stopColor='#ef4444' stopOpacity={0} /></linearGradient>
              </defs>
              <CartesianGrid strokeDasharray='3 3' stroke='#e5e7eb' />
              <XAxis dataKey='name' tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ fontSize: '12px', borderRadius: '8px' }} />
              <Legend wrapperStyle={{ fontSize: '12px' }} />
              <Area type='monotone' dataKey='درآمد' stroke='#22c55e' fill='url(#g1)' strokeWidth={2} />
              <Area type='monotone' dataKey='هزینه' stroke='#ef4444' fill='url(#g2)' strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title='توزیع دسته‌بندی' icon={FileText} delay={0.5}>
          <ResponsiveContainer width='100%' height={300}>
            <PieChart>
              <Pie data={cats} dataKey='value' nameKey='name' cx='50%' cy='50%' outerRadius={100} innerRadius={60} label={(e) => `${e.value}%`}>
                {cats.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Pie>
              <Tooltip contentStyle={{ fontSize: '12px', borderRadius: '8px' }} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
      <Card>
        <CardHeader className='flex flex-row items-center justify-between'>
          <CardTitle className='flex items-center gap-2'><Receipt className='w-5 h-5 text-green-500' /> تراکنش‌های اخیر</CardTitle>
          <Button variant='outline' size='sm'><Download className='w-4 h-4 ml-2' /> خروجی</Button>
        </CardHeader>
        <CardContent>
          <div className='overflow-x-auto'>
            <table className='w-full text-sm'>
              <thead className='bg-muted/50 text-xs text-muted-foreground'>
                <tr><th className='p-3 text-right'>شناسه</th><th className='p-3 text-right'>نوع</th><th className='p-3 text-right'>توضیحات</th><th className='p-3 text-right'>مبلغ</th><th className='p-3 text-right'>تاریخ</th></tr>
              </thead>
              <tbody>
                {txs.map((tx, i) => (
                  <motion.tr key={tx.id} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }} className='border-t border-border hover:bg-muted/20'>
                    <td className='p-3 font-mono text-xs'>{tx.id}</td>
                    <td className='p-3'><Badge variant='outline' className={typeColors[tx.type] || ''}>{typeLabels[tx.type] || tx.type}</Badge></td>
                    <td className='p-3'>{tx.description}</td>
                    <td className={`p-3 font-bold ${tx.type === 'expense' ? 'text-red-600' : 'text-green-600'}`}>{tx.type === 'expense' ? '-' : '+'}{tx.amount.toLocaleString()} {tx.currency}</td>
                    <td className='p-3 text-xs text-muted-foreground'>{new Date(tx.date).toLocaleDateString('fa-IR')}</td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
