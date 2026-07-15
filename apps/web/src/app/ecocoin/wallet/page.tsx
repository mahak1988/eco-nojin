// apps/web/src/app/ecocoin/wallet/page.tsx
'use client'

import { useAccount, useReadContract, useWriteContract, useWaitForTransactionReceipt } from 'wagmi'
import { EcoCoin_ADDRESS, ECOCOIN_ABI } from '@/lib/contracts'
import { formatEther, parseEther } from 'viem'
import { useState } from 'react'
import { Wallet, Send, Download, ArrowUpRight, ArrowDownLeft } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useToast } from '@/hooks/use-toast'

export default function EcoCoinWallet() {
  const { address, isConnected } = useAccount()
  const { toast } = useToast()
  const [recipient, setRecipient] = useState('')
  const [amount, setAmount] = useState('')

  const { data: balance } = useReadContract({
    address: EcoCoin_ADDRESS,
    abi: ECOCOIN_ABI,
    functionName: 'balanceOf',
    args: [address!],
    query: { enabled: isConnected },
  })

  const { writeContract, data: txHash, isPending } = useWriteContract()
  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({ hash: txHash })

  const handleTransfer = async () => {
    if (!recipient || !amount) {
      toast({ title: 'خطا', description: 'آدرس و مقدار را وارد کنید', variant: 'destructive' })
      return
    }

    try {
      writeContract({
        address: EcoCoin_ADDRESS,
        abi: ECOCOIN_ABI,
        functionName: 'transfer',
        args: [recipient as `0x${string}`, parseEther(amount)],
      })
    } catch (error) {
      toast({ title: 'خطا در تراکنش', description: String(error), variant: 'destructive' })
    }
  }

  if (isSuccess) {
    toast({ title: '✅ تراکنش موفق', description: `${amount} ECO ارسال شد` })
  }

  if (!isConnected) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <Card className="p-12 max-w-md text-center">
          <Wallet className="w-16 h-16 mx-auto mb-4 text-green-500" />
          <h2 className="text-2xl font-bold mb-2">کیف پول EcoCoin</h2>
          <p className="text-muted-foreground">کیف پول خود را متصل کنید</p>
        </Card>
      </div>
    )
  }

  const transactions = [
    { type: 'دریافت', amount: '+45.5', from: '0x7Ae3...4f2B', time: '۲ ساعت پیش', incoming: true },
    { type: 'ارسال', amount: '-100.0', to: '0x9Bc1...8a3C', time: '۵ ساعت پیش', incoming: false },
    { type: 'دریافت', amount: '+127.3', from: 'Staking Reward', time: '۱ روز پیش', incoming: true },
  ]

  return (
    <div className="container mx-auto px-4 py-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <Wallet className="w-8 h-8 text-green-500" />
          کیف پول EcoCoin
        </h1>
      </div>

      {/* موجودودی */}
      <Card className="overflow-hidden bg-gradient-to-br from-green-500/10 to-emerald-500/10 border-green-500/20">
        <CardContent className="p-8">
          <div className="text-sm text-muted-foreground mb-2">موجودی کلی</div>
          <div className="text-5xl font-bold text-green-600 mb-4">
            {balance ? formatEther(balance as bigint) : '0.0'}
            <span className="text-2xl mr-2">ECO</span>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" className="bg-background/50">
              <Download className="w-4 h-4 ml-2" />
              دریافت
            </Button>
            <Button variant="outline" className="bg-background/50">
              <Send className="w-4 h-4 ml-2" />
              ارسال
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* فرم انتقال */}
        <Card>
          <CardHeader>
            <CardTitle>انتقال EcoCoin</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="recipient">آدرس گیرنده</Label>
              <Input
                id="recipient"
                placeholder="0x..."
                value={recipient}
                onChange={(e) => setRecipient(e.target.value)}
                className="font-mono"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="amount">مقدار (ECO)</Label>
              <Input
                id="amount"
                type="number"
                placeholder="0.0"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
              />
            </div>
            <Button
              onClick={handleTransfer}
              disabled={isPending || isConfirming}
              className="w-full bg-green-600 hover:bg-green-700"
            >
              {isPending ? 'در حال ارسال...' : isConfirming ? 'تأیید تراکنش...' : 'ارسال'}
            </Button>
          </CardContent>
        </Card>

        {/* تاریخچه تراکنش‌ها */}
        <Card>
          <CardHeader>
            <CardTitle>تراکنش‌های اخیر</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {transactions.map((tx, i) => (
              <div
                key={i}
                className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-accent/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  {tx.incoming ? (
                    <ArrowDownLeft className="w-5 h-5 text-green-500" />
                  ) : (
                    <ArrowUpRight className="w-5 h-5 text-red-500" />
                  )}
                  <div>
                    <div className="font-medium text-sm">{tx.type}</div>
                    <div className="text-xs text-muted-foreground font-mono">
                      {tx.incoming ? tx.from : tx.to}
                    </div>
                  </div>
                </div>
                <div className="text-left">
                  <div className={`font-bold ${tx.incoming ? 'text-green-600' : 'text-red-600'}`}>
                    {tx.amount} ECO
                  </div>
                  <div className="text-xs text-muted-foreground">{tx.time}</div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
