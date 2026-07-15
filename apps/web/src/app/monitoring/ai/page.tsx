'use client'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Brain, Sparkles, TrendingUp, Lightbulb, AlertCircle } from 'lucide-react'
import { PageHeader } from '@/components/shared/PageHeader'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

export default function AIAnalysisPage() {
  const [models, setModels] = useState([])
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => { fetch('/api/monitoring/ai/models').then(r => r.json()).then(setModels) }, [])

  const analyze = async () => {
    setLoading(true)
    try { const res = await fetch('/api/monitoring/ai/analyze', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ project_id: 'amazon-north', data_type: 'ndvi', timeframe: '30d' }) }); setResult(await res.json()) } finally { setLoading(false) }
  }

  return (
    <div className='container mx-auto px-4 py-8'>
      <PageHeader title='تحلیل هوش مصنوعی' description='پیش‌بینی و تشخیص با ماشین لرنینگ' icon={Brain} color='text-purple-500' />
      <div className='grid lg:grid-cols-2 gap-6 mb-8'>
        <Card>
          <CardHeader><CardTitle className='flex items-center gap-2'><Sparkles className='w-5 h-5 text-purple-500' /> مدل‌های AI</CardTitle></CardHeader>
          <CardContent className='space-y-3'>
            {models.map((m: any, i) => (
              <motion.div key={m.id} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }} className='flex items-center justify-between p-3 rounded-lg border border-border'>
                <div><div className='font-medium text-sm'>{m.name}</div></div>
                <Badge variant='outline' className='text-green-600'>{(m.accuracy * 100).toFixed(0)}٪ دقت</Badge>
              </motion.div>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>اجرای تحلیل</CardTitle></CardHeader>
          <CardContent>
            <Button className='w-full bg-purple-600 hover:bg-purple-700 mb-4' onClick={analyze} disabled={loading}><Brain className='w-4 h-4 ml-2' />{loading ? 'در حال تحلیل...' : 'تحلیل با AI'}</Button>
            {result && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className='space-y-4'>
                <div className='p-4 rounded-lg bg-purple-500/10 border border-purple-500/20'><p className='text-sm'>{result.summary}</p></div>
                {result.insights?.map((ins: any, i: number) => (
                  <div key={i} className='flex items-start gap-2 p-2 text-sm'>
                    <Badge variant='outline' className={ins.type === 'positive' ? 'text-green-600' : ins.type === 'warning' ? 'text-yellow-600' : 'text-blue-600'}>{ins.type}</Badge>
                    <span className='flex-1'>{ins.message}</span><span className='text-xs text-muted-foreground'>{(ins.confidence * 100).toFixed(0)}٪</span>
                  </div>
                ))}
                {result.recommendations?.map((rec: string, i: number) => (
                  <div key={i} className='text-sm p-2 rounded bg-muted/30 mb-1'>• {rec}</div>
                ))}
              </motion.div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
