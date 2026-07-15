'use client'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Receipt, Search, Filter, Download, Plus } from 'lucide-react'
import { PageHeader } from '@/components/shared/PageHeader'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'

export default function TransactionsPage() {
  const [txs, setTxs] = useState([])
  const [search, setSearch] = useState('')

  useEffect(() => {
    fetch('/api/accounting/transactions?limit=50').then(r => r.json()).then(d => setTxs(d.transactions || []))
  }, [])

  const filtered = txs.filter((t: any) => t.description.includes(search) || t.id.includes(search))

  return (
    <div className='container mx-auto px-4 py-8'>
      <PageHeader title='تراکنش‌ها' description='مدیریت کامل تراکنش‌های مالی' icon={Receipt} />
      <Card className='mb-6'><CardContent className='p-4'>
        <div className='flex flex-wrap gap-3'>
          <div className='relative flex-1 min-w-[200px]'>
            <Search className='absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground' />
            <Input placeholder='جستجو...' value={search} onChange={e => setSearch(e.target.value)} className='pr-10' />
          </div>
          <Button variant='outline'><Filter className='w-4 h-4 ml-2' /> فیلتر</Button>
          <Button variant='outline'><Download className='w-4 h-4 ml-2' /> خروجی</Button>
          <Button className='bg-green-600 hover:bg-green-700'><Plus className='w-4 h-4 ml-2' /> تراکنش جدید</Button>
        </div>
      </CardContent></Card>
      <Card><CardContent className='p-0'>
        <div className='overflow-x-auto'>
          <table className='w-full text-sm'>
            <thead className='bg-muted/50 text-xs text-muted-foreground'>
              <tr><th className='p-3 text-right'>شناسه</th><th className='p-3 text-right'>نوع</th><th className='p-3 text-right'>توضیحات</th><th className='p-3 text-right'>مبلغ</th><th className='p-3 text-right'>تاریخ</th><th className='p-3 text-right'>وضعیت</th></tr>
            </thead>
            <tbody>
              {filtered.map((tx: any, i: number) => (
                <motion.tr key={tx.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.03 }} className='border-t border-border hover:bg-muted/20'>
                  <td className='p-3 font-mono text-xs'>{tx.id}</td>
                  <td className='p-3'><Badge variant='outline'>{tx.type}</Badge></td>
                  <td className='p-3'>{tx.description}</td>
                  <td className={`p-3 font-bold ${tx.type === 'expense' ? 'text-red-600' : 'text-green-600'}`}>{tx.type === 'expense' ? '-' : '+'}{tx.amount.toLocaleString()} {tx.currency}</td>
                  <td className='p-3 text-xs text-muted-foreground'>{new Date(tx.date).toLocaleDateString('fa-IR')}</td>
                  <td className='p-3'><Badge variant='outline' className='text-green-600'>{tx.status}</Badge></td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent></Card>
    </div>
  )
}
