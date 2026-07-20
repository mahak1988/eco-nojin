'use client'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Brain, Sparkles, TrendingUp, Lightbulb, AlertCircle, Zap, Stars } from 'lucide-react'
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
    <div className='relative min-h-screen overflow-hidden bg-gradient-to-br from-background via-background to-purple-500/5'>
      {/* Background Effects */}
      <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:32px]" />
      <div className="absolute top-0 right-0 h-96 w-96 rounded-full bg-purple-500/10 blur-3xl" />
      <div className="absolute bottom-0 left-0 h-96 w-96 rounded-full bg-indigo-500/10 blur-3xl" />
      
      <div className='relative container mx-auto px-4 py-8'>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className='mb-8'
        >
          <PageHeader title='تحلیل هوش مصنوعی' description='پیش‌بینی و تشخیص با ماشین لرنینگ پیشرفته' icon={Brain} color='text-purple-500' />
        </motion.div>
        
        <div className='grid lg:grid-cols-2 gap-6 mb-8'>
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className='bg-card/50 backdrop-blur-xl border-border/50 h-full'>
              <CardHeader><CardTitle className='flex items-center gap-2'><Sparkles className='w-5 h-5 text-purple-500' /> مدل‌های AI</CardTitle></CardHeader>
              <CardContent className='space-y-3'>
                {models.map((m: any, i) => (
                  <motion.div 
                    key={m.id} 
                    initial={{ opacity: 0, x: -20 }} 
                    animate={{ opacity: 1, x: 0 }} 
                    transition={{ delay: i * 0.1 }} 
                    className='flex items-center justify-between p-4 rounded-xl border border-border/50 hover:bg-purple-500/5 hover:border-purple-500/30 transition-all cursor-pointer group'
                  >
                    <div>
                      <div className='font-medium text-sm group-hover:text-purple-600 transition-colors'>{m.name}</div>
                      <div className='text-xs text-muted-foreground mt-1'>{m.description || 'مدل پیشرفته یادگیری ماشین'}</div>
                    </div>
                    <Badge variant='outline' className='text-green-600 bg-green-500/10 border-green-500/30 group-hover:scale-105 transition-transform'>{(m.accuracy * 100).toFixed(0)}٪ دقت</Badge>
                  </motion.div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className='bg-card/50 backdrop-blur-xl border-border/50 h-full'>
              <CardHeader><CardTitle className='flex items-center gap-2'><Zap className='w-5 h-5 text-yellow-500' /> اجرای تحلیل</CardTitle></CardHeader>
              <CardContent>
                <Button className='w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 shadow-lg shadow-purple-500/20 mb-6' onClick={analyze} disabled={loading}>
                  <Brain className='w-4 h-4 ml-2' />
                  {loading ? 'در حال تحلیل...' : 'تحلیل با AI'}
                </Button>
                {result && (
                  <motion.div 
                    initial={{ opacity: 0, scale: 0.95 }} 
                    animate={{ opacity: 1, scale: 1 }} 
                    className='space-y-4'
                  >
                    <div className='p-5 rounded-xl bg-gradient-to-br from-purple-500/10 to-indigo-500/10 border border-purple-500/20 backdrop-blur-xl'>
                      <div className='flex items-start gap-3'>
                        <Stars className='w-5 h-5 text-purple-500 mt-0.5' />
                        <p className='text-sm leading-relaxed'>{result.summary}</p>
                      </div>
                    </div>
                    {result.insights?.map((ins: any, i: number) => (
                      <motion.div 
                        key={i} 
                        initial={{ opacity: 0, y: 10 }} 
                        animate={{ opacity: 1, y: 0 }} 
                        transition={{ delay: i * 0.1 }}
                        className='flex items-start gap-3 p-4 rounded-xl border border-border/50 hover:bg-muted/30 transition-colors'
                      >
                        <Badge variant='outline' className={ins.type === 'positive' ? 'text-green-600 bg-green-500/10 border-green-500/30' : ins.type === 'warning' ? 'text-yellow-600 bg-yellow-500/10 border-yellow-500/30' : 'text-blue-600 bg-blue-500/10 border-blue-500/30'}>{ins.type}</Badge>
                        <span className='flex-1 text-sm'>{ins.message}</span>
                        <span className='text-xs text-muted-foreground font-medium'>{(ins.confidence * 100).toFixed(0)}٪</span>
                      </motion.div>
                    ))}
                    {result.recommendations?.map((rec: string, i: number) => (
                      <motion.div 
                        key={i} 
                        initial={{ opacity: 0, x: -10 }} 
                        animate={{ opacity: 1, x: 0 }} 
                        transition={{ delay: i * 0.1 }}
                        className='text-sm p-4 rounded-xl bg-gradient-to-r from-purple-500/5 to-transparent border-l-2 border-purple-500 mb-2'
                      >
                        <div className='flex items-start gap-2'>
                          <Lightbulb className='w-4 h-4 text-purple-500 mt-0.5 shrink-0' />
                          <span>{rec}</span>
                        </div>
                      </motion.div>
                    ))}
                  </motion.div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
