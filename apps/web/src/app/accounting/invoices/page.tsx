'use client'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { FileText, Plus, Download, Eye } from 'lucide-react'
import { PageHeader } from '@/components/shared/PageHeader'
import { StatCard } from '@/components/shared/StatCard'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState([])
  useEffect(() => { fetch('/api/accounting/invoices').then(r => r.json()).then(d => setInvoices(d.invoices || [])) }, [])

  const paid = invoices.filter((i: any) => i.status === 'paid').reduce((s: number, i: any) => s + i.total, 0)
  const pending = invoices.filter((i: any) => i.status === 'pending').reduce((s: number, i: any) => s + i.total, 0)

  return (
    <div className='container mx-auto px-4 py-8'>
      <PageHeader title='فاکتورها' description='مدیریت فاکتورها و پرداخت‌ها' icon={FileText} />
      <div className='grid grid-cols-1 md:grid-cols-3 gap-4 mb-8'>
        <StatCard label='کل فاکتورها' value={invoices.length} icon={FileText} color='text-blue-500' bgColor='bg-blue-500/10' delay={0} />
        <StatCard label='پرداخت‌شده' value={`$${paid.toLocaleString()}`} icon={Download} color='text-green-500' bgColor='bg-green-500/10' delay={0.1} />
        <StatCard label='در انتظار' value={`$${pending.toLocaleString()}`} icon={Eye} color='text-yellow-500' bgColor='bg-yellow-500/10' delay={0.2} />
      </div>
      <div className='flex justify-end mb-4'><Button className='bg-green-600 hover:bg-green-700'><Plus className='w-4 h-4 ml-2' /> فاکتور جدید</Button></div>
      <Card>
        <CardHeader><CardTitle>لیست فاکتورها</CardTitle></CardHeader>
        <CardContent>
          <div className='overflow-x-auto'>
            <table className='w-full text-sm'>
              <thead className='bg-muted/50 text-xs text-muted-foreground'>
                <tr><th className='p-3 text-right'>شماره</th><th className='p-3 text-right'>مشتری</th><th className='p-3 text-right'>کل</th><th className='p-3 text-right'>وضعیت</th><th className='p-3 text-right'>سررسید</th><th className='p-3 text-right'>عملیات</th></tr>
              </thead>
              <tbody>
                {invoices.map((inv: any, i: number) => (
                  <motion.tr key={inv.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.05 }} className='border-t border-border hover:bg-muted/20'>
                    <td className='p-3 font-mono text-xs'>{inv.number}</td>
                    <td className='p-3 font-medium'>{inv.client}</td>
                    <td className='p-3 font-bold'>${inv.total.toLocaleString()}</td>
                    <td className='p-3'><Badge variant='outline' className={inv.status === 'paid' ? 'text-green-600 border-green-500/30' : 'text-yellow-600 border-yellow-500/30'}>{inv.status === 'paid' ? '✓ پرداخت‌شده' : '⏳ در انتظار'}</Badge></td>
                    <td className='p-3 text-xs text-muted-foreground'>{new Date(inv.due_date).toLocaleDateString('fa-IR')}</td>
                    <td className='p-3'><div className='flex gap-1'><Button size='sm' variant='ghost'><Eye className='w-4 h-4' /></Button><Button size='sm' variant='ghost'><Download className='w-4 h-4' /></Button></div></td>
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
