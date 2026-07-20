// apps/web/src/app/ecocoin/dashboard/page.tsx
'use client'

import { useAccount, useReadContract } from 'wagmi'
import { EcoCoin_ADDRESS, ECOCOIN_ABI } from '@/lib/contracts'
import { formatEther } from 'viem'
import { motion } from 'framer-motion'
import { Leaf, TrendingUp, Users, Globe, Zap, Award, Coins, Activity } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'

export default function EcoCoinDashboard() {
  const { address, isConnected } = useAccount()

  const { data: balance } = useReadContract({
    address: EcoCoin_ADDRESS,
    abi: ECOCOIN_ABI,
    functionName: 'balanceOf',
    args: [address!],
    query: { enabled: isConnected },
  })

  const { data: totalSupply } = useReadContract({
    address: EcoCoin_ADDRESS,
    abi: ECOCOIN_ABI,
    functionName: 'totalSupply',
  })

  if (!isConnected) {
    return (
      <motion.div 
        className="min-h-[60vh] flex items-center justify-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <Card className="p-12 max-w-md text-center glass-card border-white/20 backdrop-blur-xl">
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ type: "spring", stiffness: 200, damping: 15 }}
          >
            <Leaf className="w-20 h-20 mx-auto mb-6 text-green-500 drop-shadow-lg" />
          </motion.div>
          <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-green-500 to-emerald-600 bg-clip-text text-transparent">
            به EcoCoin خوش آمدید
          </h2>
          <p className="text-muted-foreground mb-8 text-lg">
            برای مشاهده‌ی داشبورد، کیف پول خود را متصل کنید
          </p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-8 py-3 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full font-semibold text-white shadow-lg hover:shadow-green-500/25 transition-all"
          >
            اتصال کیف پول
          </motion.button>
        </Card>
      </motion.div>
    )
  }

  const stats = [
    {
      label: 'موجودی شما',
      value: balance ? `${formatEther(balance as bigint)} ECO` : '—',
      icon: Leaf,
      color: 'from-green-500 to-emerald-600',
      bgColor: 'bg-green-500/10',
      textColor: 'text-green-500',
      glowColor: 'shadow-green-500/20',
    },
    {
      label: 'عرضه‌ی کل',
      value: totalSupply ? `${Number(formatEther(totalSupply as bigint)).toLocaleString()} ECO` : '—',
      icon: TrendingUp,
      color: 'from-blue-500 to-cyan-600',
      bgColor: 'bg-blue-500/10',
      textColor: 'text-blue-500',
      glowColor: 'shadow-blue-500/20',
    },
    {
      label: 'مراقبان فعال',
      value: '۱۲,۸۴۷',
      icon: Users,
      color: 'from-purple-500 to-pink-600',
      bgColor: 'bg-purple-500/10',
      textColor: 'text-purple-500',
      glowColor: 'shadow-purple-500/20',
    },
    {
      label: 'هکتار تحت مراقبت',
      value: '۱۴۲,۵۰۰',
      icon: Globe,
      color: 'from-emerald-500 to-teal-600',
      bgColor: 'bg-emerald-500/10',
      textColor: 'text-emerald-500',
      glowColor: 'shadow-emerald-500/20',
    },
  ]

  const recentActivities = [
    { type: 'مراقبت روزانه', amount: '+45.5 ECO', project: 'آمازون شمالی', time: '۲ دقیقه پیش', color: 'from-green-500 to-emerald-600', icon: Leaf },
    { type: 'چالش تکمیل شد', amount: '+127.3 ECO', project: 'مراتع کنیا', time: '۱ ساعت پیش', color: 'from-blue-500 to-cyan-600', icon: Award },
    { type: 'پاداش دانش', amount: '+23.1 ECO', project: 'جنگل‌های حرا', time: '۳ ساعت پیش', color: 'from-purple-500 to-pink-600', icon: Coins },
  ]

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { type: "spring", stiffness: 100 }
    }
  }

  return (
    <motion.div 
      className="container mx-auto px-4 py-8 space-y-8"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Header */}
      <motion.div 
        className="flex items-center justify-between"
        variants={itemVariants}
      >
        <div>
          <motion.h1 
            className="text-4xl font-bold flex items-center gap-4"
            initial={{ x: -50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ type: "spring", stiffness: 100 }}
          >
            <div className="relative">
              <Leaf className="w-10 h-10 text-green-500 drop-shadow-lg" />
              <motion.div
                className="absolute inset-0 bg-green-500 rounded-full"
                animate={{ scale: [1, 1.5, 1], opacity: [0.3, 0, 0] }}
                transition={{ repeat: Infinity, duration: 2 }}
              />
            </div>
            <span className="bg-gradient-to-r from-green-500 via-emerald-600 to-teal-600 bg-clip-text text-transparent">
              داشبورد EcoCoin
            </span>
          </motion.h1>
          <motion.p 
            className="text-muted-foreground mt-2 text-lg"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            مراقبت بوم‌شناختی شما
          </motion.p>
        </div>
        <motion.div
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Badge variant="outline" className="text-green-600 border-green-500/30 px-4 py-2 glass-card backdrop-blur-sm">
            <motion.span 
              className="w-2 h-2 rounded-full bg-green-500 ml-2"
              animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
            />
            فعال
          </Badge>
        </motion.div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div 
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        variants={containerVariants}
      >
        {stats.map((stat, i) => {
          const Icon = stat.icon
          return (
            <motion.div key={i} variants={itemVariants}>
              <Card className="overflow-hidden glass-card border-white/20 backdrop-blur-xl hover:backdrop-blur-2xl transition-all duration-300 group">
                <CardContent className="p-6">
                  <motion.div 
                    className={`w-14 h-14 rounded-2xl ${stat.bgColor} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg ${stat.glowColor}`}
                    whileHover={{ rotate: 5 }}
                  >
                    <Icon className={`w-7 h-7 ${stat.textColor}`} />
                  </motion.div>
                  <motion.div 
                    className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-300 bg-clip-text text-transparent"
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: i * 0.1 + 0.3, type: "spring" }}
                  >
                    {stat.value}
                  </motion.div>
                  <div className="text-sm text-muted-foreground mt-2 font-medium">{stat.label}</div>
                </CardContent>
              </Card>
            </motion.div>
          )
        })}
      </motion.div>

      {/* دو ستون: فعالیت‌ها + پیشرفت */}
      <motion.div 
        className="grid lg:grid-cols-2 gap-6"
        variants={containerVariants}
      >
        {/* فعالیت‌های اخیر */}
        <motion.div variants={itemVariants}>
          <Card className="glass-card border-white/20 backdrop-blur-xl h-full">
            <CardHeader>
              <CardTitle className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-yellow-500/10">
                  <Zap className="w-6 h-6 text-yellow-500" />
                </div>
                <span className="text-xl">فعالیت‌های اخیر</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {recentActivities.map((activity, i) => {
                const ActivityIcon = activity.icon
                return (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.15 }}
                    whileHover={{ scale: 1.02, x: 5 }}
                    className="flex items-center justify-between p-4 rounded-xl border border-border hover:bg-accent/50 transition-all cursor-pointer group"
                  >
                    <div className="flex items-center gap-4">
                      <motion.div 
                        className={`w-10 h-10 rounded-xl bg-gradient-to-br ${activity.color} flex items-center justify-center shadow-lg`}
                        whileHover={{ rotate: 15, scale: 1.1 }}
                      >
                        <ActivityIcon className="w-5 h-5 text-white" />
                      </motion.div>
                      <div>
                        <div className="font-semibold text-sm group-hover:text-green-600 transition-colors">{activity.type}</div>
                        <div className="text-xs text-muted-foreground">{activity.project}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <motion.div 
                        className="font-bold text-green-600 text-lg"
                        initial={{ scale: 0.5 }}
                        animate={{ scale: 1 }}
                        transition={{ delay: i * 0.15 + 0.2, type: "spring" }}
                      >
                        {activity.amount}
                      </motion.div>
                      <div className="text-xs text-muted-foreground">{activity.time}</div>
                    </div>
                  </motion.div>
                )
              })}
            </CardContent>
          </Card>
        </motion.div>

        {/* پیشرفت مراقبت */}
        <motion.div variants={itemVariants}>
          <Card className="glass-card border-white/20 backdrop-blur-xl h-full">
            <CardHeader>
              <CardTitle className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-purple-500/10">
                  <Award className="w-6 h-6 text-purple-500" />
                </div>
                <span className="text-xl">پیشرفت مراقبت</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {[
                { label: 'سطح کارما', current: 3000, total: 5000, percentage: 60, subtext: '۱,۰۰۰ کارما تا سطح Silver', color: 'from-purple-500 to-pink-600' },
                { label: 'تعهد زمانی', current: 5, total: 10, percentage: 50, subtext: 'ضریب فعلی: ۲.۰×', color: 'from-blue-500 to-cyan-600' },
                { label: 'CO₂ جذب‌شده (تن)', current: 452, total: 1000, percentage: 45, subtext: 'هدف سالانه', color: 'from-green-500 to-emerald-600' },
              ].map((progress, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.15 }}
                >
                  <div className="flex justify-between text-sm mb-2">
                    <span className="font-medium">{progress.label}</span>
                    <span className="font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
                      {progress.current.toLocaleString()} / {progress.total.toLocaleString()}
                    </span>
                  </div>
                  <div className="relative h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <motion.div
                      className={`absolute inset-y-0 left-0 bg-gradient-to-r ${progress.color} rounded-full`}
                      initial={{ width: 0 }}
                      animate={{ width: `${progress.percentage}%` }}
                      transition={{ delay: i * 0.15 + 0.3, duration: 1, ease: "easeOut" }}
                    >
                      <motion.div
                        className="absolute inset-0 bg-white/20"
                        animate={{ x: ['-100%', '100%'] }}
                        transition={{ repeat: Infinity, duration: 1.5, delay: i * 0.2 }}
                      />
                    </motion.div>
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">{progress.subtext}</p>
                </motion.div>
              ))}

              <motion.div 
                className="pt-6 border-t border-border"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
              >
                <div className="flex items-center justify-between p-4 rounded-xl bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20">
                  <span className="text-sm font-medium">بازده روزانه تخمینی</span>
                  <motion.span 
                    className="text-3xl font-bold bg-gradient-to-r from-green-500 to-emerald-600 bg-clip-text text-transparent"
                    animate={{ scale: [1, 1.05, 1] }}
                    transition={{ repeat: Infinity, duration: 2 }}
                  >
                    ۲۷۶.۸ ECO
                  </motion.span>
                </div>
              </motion.div>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </motion.div>
  )
}
