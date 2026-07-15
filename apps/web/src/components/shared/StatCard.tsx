'use client'
import { motion } from 'framer-motion'
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react'
import { Card } from '@/components/ui/card'

export function StatCard({ label, value, icon: Icon, color = 'text-green-500', bgColor = 'bg-green-500/10', trend, delay = 0 }: {
  label: string; value: string | number; icon: LucideIcon; color?: string; bgColor?: string; trend?: number; delay?: number
}) {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay }} whileHover={{ y: -4 }}>
      <Card className='overflow-hidden'>
        <div className='p-6'>
          <div className='flex items-start justify-between mb-4'>
            <div className={`w-12 h-12 rounded-xl ${bgColor} flex items-center justify-center`}>
              <Icon className={`w-6 h-6 ${color}`} />
            </div>
            {trend !== undefined && (
              <div className={`flex items-center gap-1 text-sm font-medium ${trend >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                {trend >= 0 ? <TrendingUp className='w-4 h-4' /> : <TrendingDown className='w-4 h-4' />}
                {Math.abs(trend)}%
              </div>
            )}
          </div>
          <div className='text-2xl font-bold'>{value}</div>
          <div className='text-sm text-muted-foreground mt-1'>{label}</div>
        </div>
      </Card>
    </motion.div>
  )
}
