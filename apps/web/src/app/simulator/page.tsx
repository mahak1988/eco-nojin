'use client'
import { motion } from 'framer-motion'
import { Leaf, Droplets, Bird, Satellite, Brain } from 'lucide-react'
import { PageHeader } from '@/components/shared/PageHeader'
import { Card, CardContent } from '@/components/ui/card'

const sims = [
  { title: 'شبیه‌ساز کربن', desc: 'محاسبه جذب CO₂ و پاداش ECO', icon: Leaf, color: 'from-green-500 to-emerald-600', href: '/simulator/carbon' },
  { title: 'شبیه‌ساز آب', desc: 'محاسبه ذخیره و کیفیت آب', icon: Droplets, color: 'from-blue-500 to-cyan-600', href: '/simulator/water' },
  { title: 'شبیه‌ساز تنوع زیستی', desc: 'برآورد گونه‌ها و شاخص تنوع', icon: Bird, color: 'from-purple-500 to-pink-600', href: '/simulator/biodiversity' },
  { title: 'پایش ماهواره‌ای', desc: 'تحلیل NDVI/NDWI از Sentinel-2', icon: Satellite, color: 'from-orange-500 to-red-600', href: '/monitoring/satellite' },
  { title: 'تحلیل هوش مصنوعی', desc: 'پیش‌بینی و تشخیص با ML', icon: Brain, color: 'from-indigo-500 to-purple-600', href: '/monitoring/ai' },
]

export default function SimulatorDashboard() {
  return (
    <div className='container mx-auto px-4 py-8'>
      <PageHeader title='شبیه‌سازها' description='ابزارهای شبیه‌سازی و پایش بوم‌شناختی' icon={Leaf} />
      <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'>
        {sims.map((sim, i) => {
          const Icon = sim.icon
          return (
            <motion.div key={i} initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }} whileHover={{ y: -8, scale: 1.02 }}>
              <a href={sim.href}>
                <Card className='overflow-hidden cursor-pointer h-full'>
                  <div className={`h-32 bg-gradient-to-br ${sim.color} flex items-center justify-center'><Icon className='w-16 h-16 text-white' /></div>
                  <CardContent className='p-6'>
                    <h3 className='text-xl font-bold mb-2'>{sim.title}</h3>
                    <p className='text-sm text-muted-foreground'>{sim.desc}</p>
                    <div className='mt-4 text-green-600 text-sm font-medium'>شروع شبیه‌سازی ←</div>
                  </CardContent>
                </Card>
              </a>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
