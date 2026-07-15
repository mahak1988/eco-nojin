'use client'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { LucideIcon } from 'lucide-react'
import { ReactNode } from 'react'

export function ChartCard({ title, icon: Icon, iconColor = 'text-green-500', children, delay = 0, action }: {
  title: string; icon: LucideIcon; iconColor?: string; children: ReactNode; delay?: number; action?: ReactNode
}) {
  return (
    <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.4, delay }}>
      <Card>
        <CardHeader className='flex flex-row items-center justify-between'>
          <CardTitle className='flex items-center gap-2 text-lg'>
            <Icon className={`w-5 h-5 ${iconColor}`} />
            {title}
          </CardTitle>
          {action}
        </CardHeader>
        <CardContent>{children}</CardContent>
      </Card>
    </motion.div>
  )
}
