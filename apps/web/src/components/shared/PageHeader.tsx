'use client'
import { motion } from 'framer-motion'
import { LucideIcon } from 'lucide-react'

export function PageHeader({ title, description, icon: Icon, color = 'text-green-500' }: {
  title: string; description?: string; icon: LucideIcon; color?: string
}) {
  return (
    <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className='mb-8'>
      <div className='flex items-center gap-4'>
        <motion.div whileHover={{ scale: 1.1, rotate: 5 }} className='w-14 h-14 rounded-2xl bg-gradient-to-br from-green-500/10 to-emerald-500/10 flex items-center justify-center'>
          <Icon className={`w-7 h-7 ${color}`} />
        </motion.div>
        <div>
          <h1 className='text-3xl font-bold'>{title}</h1>
          {description && <p className='text-muted-foreground mt-1'>{description}</p>}
        </div>
      </div>
    </motion.div>
  )
}
