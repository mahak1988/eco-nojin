// apps/web/src/app/ecocoin/dashboard/page.tsx
'use client'

import { useAccount, useReadContract } from 'wagmi'
import { EcoCoin_ADDRESS, ECOCOIN_ABI } from '@/lib/contracts'
import { formatEther } from 'viem'
import { Leaf, TrendingUp, Users, Globe, Zap, Award } from 'lucide-react'
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
      <div className="min-h-[60vh] flex items-center justify-center">
        <Card className="p-12 max-w-md text-center">
          <Leaf className="w-16 h-16 mx-auto mb-4 text-green-500" />
          <h2 className="text-2xl font-bold mb-2">به EcoCoin خوش آمدید</h2>
          <p className="text-muted-foreground mb-6">
            برای مشاهده‌ی داشبورد، کیف پول خود را متصل کنید
          </p>
        </Card>
      </div>
    )
  }

  const stats = [
    {
      label: 'موجودی شما',
      value: balance ? `${formatEther(balance as bigint)} ECO` : '—',
      icon: Leaf,
      color: 'text-green-500',
      bg: 'bg-green-500/10',
    },
    {
      label: 'عرضه‌ی کل',
      value: totalSupply ? `${Number(formatEther(totalSupply as bigint)).toLocaleString()} ECO` : '—',
      icon: TrendingUp,
      color: 'text-blue-500',
      bg: 'bg-blue-500/10',
    },
    {
      label: 'مراقبان فعال',
      value: '۱۲,۸۴۷',
      icon: Users,
      color: 'text-purple-500',
      bg: 'bg-purple-500/10',
    },
    {
      label: 'هکتار تحت مراقبت',
      value: '۱۴۲,۵۰۰',
      icon: Globe,
      color: 'text-emerald-500',
      bg: 'bg-emerald-500/10',
    },
  ]

  const recentActivities = [
    { type: 'مراقبت روزانه', amount: '+45.5 ECO', project: 'آمازون شمالی', time: '۲ دقیقه پیش', color: 'green' },
    { type: 'چالش تکمیل شد', amount: '+127.3 ECO', project: 'مراتع کنیا', time: '۱ ساعت پیش', color: 'blue' },
    { type: 'پاداش دانش', amount: '+23.1 ECO', project: 'جنگل‌های حرا', time: '۳ ساعت پیش', color: 'purple' },
  ]

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Leaf className="w-8 h-8 text-green-500" />
            داشبورد EcoCoin
          </h1>
          <p className="text-muted-foreground mt-1">مراقبت بوم‌شناختی شما</p>
        </div>
        <Badge variant="outline" className="text-green-600 border-green-500/30">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse ml-2" />
          فعال
        </Badge>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, i) => {
          const Icon = stat.icon
          return (
            <Card key={i} className="overflow-hidden">
              <CardContent className="p-6">
                <div className={`w-12 h-12 rounded-xl ${stat.bg} flex items-center justify-center mb-4`}>
                  <Icon className={`w-6 h-6 ${stat.color}`} />
                </div>
                <div className="text-2xl font-bold">{stat.value}</div>
                <div className="text-sm text-muted-foreground mt-1">{stat.label}</div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* دو ستون: فعالیت‌ها + پیشرفت */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* فعالیت‌های اخیر */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-yellow-500" />
              فعالیت‌های اخیر
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {recentActivities.map((activity, i) => (
              <div
                key={i}
                className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-accent/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-full bg-${activity.color}-500`} />
                  <div>
                    <div className="font-medium text-sm">{activity.type}</div>
                    <div className="text-xs text-muted-foreground">{activity.project}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-green-600">{activity.amount}</div>
                  <div className="text-xs text-muted-foreground">{activity.time}</div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* پیشرفت مراقبت */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="w-5 h-5 text-purple-500" />
              پیشرفت مراقبت
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span>سطح کارما</span>
                <span className="font-bold">۳,۰۰۰ / ۵,۰۰۰</span>
              </div>
              <Progress value={60} className="h-2" />
              <p className="text-xs text-muted-foreground mt-1">۱,۰۰۰ کارما تا سطح Silver</p>
            </div>

            <div>
              <div className="flex justify-between text-sm mb-2">
                <span>تعهد زمانی</span>
                <span className="font-bold">سال پنجم</span>
              </div>
              <Progress value={50} className="h-2" />
              <p className="text-xs text-muted-foreground mt-1">ضریب فعلی: ۲.۰×</p>
            </div>

            <div>
              <div className="flex justify-between text-sm mb-2">
                <span>CO₂ جذب‌شده (تن)</span>
                <span className="font-bold">۴۵۲ / ۱,۰۰۰</span>
              </div>
              <Progress value={45} className="h-2" />
              <p className="text-xs text-muted-foreground mt-1">هدف سالانه</p>
            </div>

            <div className="pt-4 border-t border-border">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">بازده روزانه تخمینی</span>
                <span className="text-2xl font-bold text-green-600">۲۷۶.۸ ECO</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
