// apps/web/src/app/ecocoin/staking/page.tsx
'use client'

import { useAccount } from 'wagmi'
import { Lock, Unlock, TrendingUp, Calendar, Percent } from 'lucide-react'
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
  },
  {
    duration: '۶ ماه',
    apy: '۱۵٪',
    multiplier: '۱.۵×',
    minAmount: '۵,۰۰۰ ECO',
    color: 'from-gray-400/10 to-gray-500/10',
    border: 'border-gray-400/20',
    badge: 'نقره‌ای',
  },
  {
    duration: '۱ سال',
    apy: '۲۵٪',
    multiplier: '۲.۰×',
    minAmount: '۱۰,۰۰۰ ECO',
    color: 'from-yellow-600/10 to-orange-600/10',
    border: 'border-yellow-600/20',
    badge: 'طلایی',
  },
  {
    duration: '۲ سال',
    apy: '۵۰٪',
    multiplier: '۳.۰×',
    minAmount: '۵۰,۰۰۰ ECO',
    color: 'from-purple-500/10 to-pink-500/10',
    border: 'border-purple-500/20',
    badge: 'پلاتینی',
  },
]

export default function EcoCoinStaking() {
  const { isConnected } = useAccount()
  const [selectedTier, setSelectedTier] = useState<number | null>(null)
  const [stakeAmount, setStakeAmount] = useState('')

  if (!isConnected) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <Card className="p-12 max-w-md text-center">
          <Lock className="w-16 h-16 mx-auto mb-4 text-green-500" />
          <h2 className="text-2xl font-bold mb-2">استیکینگ EcoCoin</h2>
          <p className="text-muted-foreground">کیف پول خود را متصل کنید</p>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <Lock className="w-8 h-8 text-green-500" />
          استیکینگ EcoCoin
        </h1>
        <p className="text-muted-foreground mt-1">
          EcoCoin خود را قفل کنید و پاداش بگیرید — هرچه طولانی‌تر، ضریب بیشتر
        </p>
      </div>

      {/* آمار استیکینگ فعلی */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-6">
            <Lock className="w-8 h-8 text-purple-500 mb-2" />
            <div className="text-2xl font-bold">۵,۰۰۰ ECO</div>
            <div className="text-sm text-muted-foreground">استیک‌شده</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <TrendingUp className="w-8 h-8 text-green-500 mb-2" />
            <div className="text-2xl font-bold text-green-600">+۱۲۵ ECO</div>
            <div className="text-sm text-muted-foreground">پاداش ماهانه</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <Calendar className="w-8 h-8 text-blue-500 mb-2" />
            <div className="text-2xl font-bold">۱۸ روز</div>
            <div className="text-sm text-muted-foreground">تا باز شدن</div>
          </CardContent>
        </Card>
      </div>

      {/* انتخاب tier */}
      <div>
        <h2 className="text-xl font-bold mb-4">انتخاب دوره‌ی استیکینگ</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {stakingTiers.map((tier, i) => (
            <Card
              key={i}
              className={`cursor-pointer transition-all bg-gradient-to-br ${tier.color} border-2 ${
                selectedTier === i ? tier.border : 'border-transparent'
              } hover:scale-105`}
              onClick={() => setSelectedTier(i)}
            >
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <Badge variant="outline" className="text-xs">
                    {tier.badge}
                  </Badge>
                  <Percent className="w-4 h-4 text-muted-foreground" />
                </div>
                <div className="text-2xl font-bold mb-1">{tier.duration}</div>
                <div className="text-3xl font-bold text-green-600 mb-2">{tier.apy}</div>
                <div className="text-sm text-muted-foreground">APY</div>
                <div className="mt-4 pt-4 border-t border-border">
                  <div className="flex justify-between text-xs">
                    <span className="text-muted-foreground">ضریب:</span>
                    <span className="font-bold">{tier.multiplier}</span>
                  </div>
                  <div className="flex justify-between text-xs mt-1">
                    <span className="text-muted-foreground">حداقل:</span>
                    <span className="font-bold">{tier.minAmount}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* فرم استیک */}
      {selectedTier !== null && (
        <Card className="border-2 border-green-500/30">
          <CardHeader>
            <CardTitle>استیک {stakingTiers[selectedTier].badge}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">مقدار استیک</label>
              <input
                type="number"
                placeholder="0.0"
                value={stakeAmount}
                onChange={(e) => setStakeAmount(e.target.value)}
                className="w-full px-4 py-3 rounded-lg border border-border bg-background text-lg"
              />
            </div>

            <div className="grid grid-cols-2 gap-4 p-4 rounded-lg bg-muted/30">
              <div>
                <div className="text-xs text-muted-foreground">پاداش روزانه تخمینی</div>
                <div className="text-lg font-bold text-green-600">
                  {stakeAmount ? ((parseFloat(stakeAmount) * 0.15) / 365).toFixed(2) : '0.00'} ECO
                </div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">پاداش کل ({stakingTiers[selectedTier].duration})</div>
                <div className="text-lg font-bold text-green-600">
                  {stakeAmount ? (parseFloat(stakeAmount) * 0.15 * 0.5).toFixed(2) : '0.00'} ECO
                </div>
              </div>
            </div>

            <Button
              className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
              size="lg"
            >
              <Lock className="w-5 h-5 ml-2" />
              استیک کن
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
