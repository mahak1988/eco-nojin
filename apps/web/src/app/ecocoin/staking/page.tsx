// apps/web/src/app/ecocoin/staking/page.tsx
'use client'

import { useAccount } from 'wagmi'
import { motion } from 'framer-motion'
import { Lock, Unlock, TrendingUp, Calendar, Percent, Sparkles, Zap } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useState } from 'react'

const stakingTiers = [
  {
    duration: '۳ ماه',
    apy: '۸٪',
    multiplier: '۱.۲×',
    minAmount: '۱,۰۰۰ ECO',
    color: 'from-yellow-500/10 to-amber-500/10',
    border: 'border-yellow-500/20',
    badge: 'برنزی',
    icon: '🥉',
  },
  {
    duration: '۶ ماه',
    apy: '۱۵٪',
    multiplier: '۱.۵×',
    minAmount: '۵,۰۰۰ ECO',
    color: 'from-gray-400/10 to-gray-500/10',
    border: 'border-gray-400/20',
    badge: 'نقره‌ای',
    icon: '🥈',
  },
  {
    duration: '۱ سال',
    apy: '۲۵٪',
    multiplier: '۲.۰×',
    minAmount: '۱۰,۰۰۰ ECO',
    color: 'from-yellow-600/10 to-orange-600/10',
    border: 'border-yellow-600/20',
    badge: 'طلایی',
    icon: '🥇',
  },
  {
    duration: '۲ سال',
    apy: '۵۰٪',
    multiplier: '۳.۰×',
    minAmount: '۵۰,۰۰۰ ECO',
    color: 'from-purple-500/10 to-pink-500/10',
    border: 'border-purple-500/20',
    badge: 'پلاتینی',
    icon: '💎',
  },
]

export default function EcoCoinStaking() {
  const { isConnected } = useAccount()
  const [selectedTier, setSelectedTier] = useState<number | null>(null)
  const [stakeAmount, setStakeAmount] = useState('')

  if (!isConnected) {
    return (
      <div className="relative min-h-[60vh] flex items-center justify-center overflow-hidden bg-gradient-to-br from-background via-background to-green-500/5">
        <div className="absolute top-0 right-0 h-96 w-96 rounded-full bg-green-500/10 blur-3xl" />
        <div className="absolute bottom-0 left-0 h-96 w-96 rounded-full bg-emerald-500/10 blur-3xl" />
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="relative p-12 max-w-md text-center rounded-2xl border border-border/50 bg-card/50 backdrop-blur-xl"
        >
          <motion.div
            animate={{ rotate: [0, 10, -10, 0] }}
            transition={{ repeat: Infinity, duration: 2, repeatDelay: 3 }}
          >
            <Lock className="w-20 h-20 mx-auto mb-6 text-green-500" />
          </motion.div>
          <h2 className="text-3xl font-bold mb-3 bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">استیکینگ EcoCoin</h2>
          <p className="text-muted-foreground text-lg">کیف پول خود را متصل کنید و شروع به کسب پاداش کنید</p>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-br from-background via-background to-green-500/5">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:32px]" />
      <div className="absolute top-0 right-0 h-96 w-96 rounded-full bg-green-500/10 blur-3xl" />
      <div className="absolute bottom-0 left-0 h-96 w-96 rounded-full bg-emerald-500/10 blur-3xl" />
      
      <div className="relative container mx-auto px-4 py-8 space-y-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-4xl font-bold flex items-center gap-3 mb-2">
            <Lock className="w-10 h-10 text-green-500" />
            <span className="bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">استیکینگ EcoCoin</span>
          </h1>
          <p className="text-muted-foreground text-lg">EcoCoin خود را قفل کنید و پاداش بگیرید — هرچه طولانی‌تر، ضریب بیشتر</p>
        </motion.div>

        {/* آمار استیکینگ فعلی */}
        <motion.div 
          className="grid grid-cols-1 md:grid-cols-3 gap-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border-purple-500/20 backdrop-blur-xl">
            <CardContent className="p-6">
              <motion.div whileHover={{ scale: 1.1, rotate: 5 }}>
                <Lock className="w-10 h-10 text-purple-500 mb-3" />
              </motion.div>
              <div className="text-3xl font-bold mb-1">۵,۰۰۰ ECO</div>
              <div className="text-sm text-muted-foreground">استیک‌شده</div>
            </CardContent>
          </Card>
          <Card className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 border-green-500/20 backdrop-blur-xl">
            <CardContent className="p-6">
              <motion.div whileHover={{ scale: 1.1, rotate: -5 }}>
                <TrendingUp className="w-10 h-10 text-green-500 mb-3" />
              </motion.div>
              <div className="text-3xl font-bold text-green-600 mb-1">+۱۲۵ ECO</div>
              <div className="text-sm text-muted-foreground">پاداش ماهانه</div>
            </CardContent>
          </Card>
          <Card className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border-blue-500/20 backdrop-blur-xl">
            <CardContent className="p-6">
              <motion.div whileHover={{ scale: 1.1, rotate: 5 }}>
                <Calendar className="w-10 h-10 text-blue-500 mb-3" />
              </motion.div>
              <div className="text-3xl font-bold mb-1">۱۸ روز</div>
              <div className="text-sm text-muted-foreground">تا باز شدن</div>
            </CardContent>
          </Card>
        </motion.div>

        {/* انتخاب tier */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-yellow-500" />
            انتخاب دوره‌ی استیکینگ
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {stakingTiers.map((tier, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                whileHover={{ y: -8, scale: 1.05 }}
              >
                <Card
                  className={`cursor-pointer transition-all bg-gradient-to-br ${tier.color} border-2 ${
                    selectedTier === i ? tier.border : 'border-transparent'
                  } hover:shadow-2xl hover:shadow-green-500/10 backdrop-blur-xl h-full`}
                  onClick={() => setSelectedTier(i)}
                >
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <Badge variant="outline" className="text-xs bg-background/50">{tier.icon} {tier.badge}</Badge>
                      <Percent className="w-4 h-4 text-muted-foreground" />
                    </div>
                    <div className="text-2xl font-bold mb-1">{tier.duration}</div>
                    <div className="text-4xl font-bold text-green-600 mb-2">{tier.apy}</div>
                    <div className="text-sm text-muted-foreground mb-4">APY</div>
                    <div className="mt-4 pt-4 border-t border-border/50 space-y-2">
                      <div className="flex justify-between text-xs">
                        <span className="text-muted-foreground">ضریب:</span>
                        <span className="font-bold text-foreground">{tier.multiplier}</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-muted-foreground">حداقل:</span>
                        <span className="font-bold text-foreground">{tier.minAmount}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* فرم استیک */}
        {selectedTier !== null && (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card className="border-2 border-green-500/30 bg-gradient-to-br from-green-500/5 to-emerald-500/5 backdrop-blur-xl">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="w-5 h-5 text-green-500" />
                  استیک {stakingTiers[selectedTier].badge}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">مقدار استیک</label>
                  <input
                    type="number"
                    placeholder="0.0"
                    value={stakeAmount}
                    onChange={(e) => setStakeAmount(e.target.value)}
                    className="w-full px-4 py-3 rounded-lg border border-border bg-background/50 text-lg focus:ring-2 focus:ring-green-500/50 transition-all"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4 p-4 rounded-xl bg-muted/30 backdrop-blur-xl">
                  <div>
                    <div className="text-xs text-muted-foreground mb-1">پاداش روزانه تخمینی</div>
                    <div className="text-xl font-bold text-green-600">
                      {stakeAmount ? ((parseFloat(stakeAmount) * 0.15) / 365).toFixed(2) : '0.00'} ECO
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-muted-foreground mb-1">پاداش کل ({stakingTiers[selectedTier].duration})</div>
                    <div className="text-xl font-bold text-green-600">
                      {stakeAmount ? (parseFloat(stakeAmount) * 0.15 * 0.5).toFixed(2) : '0.00'} ECO
                    </div>
                  </div>
                </div>

                <Button
                  className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 shadow-lg shadow-green-500/20 py-6 text-lg"
                  size="lg"
                >
                  <Lock className="w-5 h-5 ml-2" />
                  استیک کن
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>
    </div>
  )
}
