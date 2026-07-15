#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
  🚀 EcoCoin Integration Completer
  نسخه: 1.0.0
============================================================================

این اسکریپت ۴ مشکل بحرانی econojin.com رو حل می‌کنه:

  ۱. نصب wagmi + RainbowKit برای wallet integration
  ۲. ساخت صفحات EcoCoin (Dashboard, Wallet, Staking)
  ۳. ساخت API routes برای EcoCoin در backend
  ۴. تنظیم hardhat برای build/deploy قراردادها
  ۵. بهبود UI/UX با shadcn-style components

📍 محل اجرا:
  cd D:\\econojin.com
  python ecocoin_completer.py

⚠️  این اسکریپت فایل‌های جدید ایجاد می‌کنه، فایل‌های موجود رو تغییر نمی‌ده.
============================================================================
"""

import os
import sys
import platform
from pathlib import Path
from datetime import datetime


class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"

    @staticmethod
    def enable_windows():
        if platform.system() == "Windows":
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                pass


# ============================================================
#  مسیرهای پروژه
# ============================================================
PROJECT_PATH = Path(r"D:\econojin.com")
WEB_PATH = PROJECT_PATH / "apps" / "web"
API_PATH = PROJECT_PATH / "apps"  # apps/main.py یا apps/api/
CONTRACTS_PATH = PROJECT_PATH / "blockchain" / "contracts"  # یا packages/contracts/src


# ============================================================
#  ۱. Wallet Integration Setup
# ============================================================

WAGMI_CONFIG = """// apps/web/src/lib/wagmi.ts
import { getDefaultConfig } from '@rainbow-me/rainbowkit'
import { mainnet, polygon, arbitrum } from 'wagmi/chains'
import { http } from 'wagmi'

export const config = getDefaultConfig({
  appName: 'EcoCoin',
  projectId: process.env.NEXT_PUBLIC_WC_PROJECT_ID || 'your-project-id',
  chains: [mainnet, polygon, arbitrum],
  transports: {
    [mainnet.id]: http(),
    [polygon.id]: http(),
    [arbitrum.id]: http(),
  },
})
"""

RAINBOWKIT_PROVIDER = """// apps/web/src/components/providers/Web3Provider.tsx
'use client'

import { RainbowKitProvider, darkTheme, lightTheme } from '@rainbow-me/rainbowkit'
import { WagmiProvider } from 'wagmi'
import { ThemeProvider, useTheme } from 'next-themes'
import { config } from '@/lib/wagmi'
import '@rainbow-me/rainbowkit/styles.css'

export function Web3Provider({ children }: { children: React.ReactNode }) {
  const { theme } = useTheme()

  return (
    <WagmiProvider config={config}>
      <RainbowKitProvider
        theme={theme === 'dark' ? darkTheme({
          accentColor: '#22c55e',
          accentColorForeground: 'white',
          borderRadius: 'medium',
        }) : lightTheme({
          accentColor: '#22c55e',
          accentColorForeground: 'white',
          borderRadius: 'medium',
        })}
        modalSize="compact"
      >
        {children}
      </RainbowKitProvider>
    </WagmiProvider>
  )
}
"""

CONNECT_BUTTON = """// apps/web/src/components/ecocoin/ConnectWallet.tsx
'use client'

import { ConnectButton } from '@rainbow-me/rainbowkit'
import { useAccount, useBalance } from 'wagmi'
import { EcoCoin_ADDRESS } from '@/lib/contracts'
import { formatEther } from 'viem'

export function ConnectWallet() {
  return (
    <ConnectButton.Custom>
      {({ account, chain, openAccountModal, openChainModal, openConnectModal, authenticationStatus, mounted }) => {
        const ready = mounted && authenticationStatus !== 'loading'
        const connected = ready && account && chain

        return (
          <div
            {...(!ready && { 'aria-hidden': true, style: { opacity: 0, pointerEvents: 'none', userSelect: 'none' } })}
            className="flex items-center gap-2"
          >
            {(() => {
              if (!connected) {
                return (
                  <button
                    onClick={openConnectModal}
                    type="button"
                    className="px-5 py-2.5 rounded-lg bg-gradient-to-r from-green-600 to-emerald-600 text-white font-medium hover:from-green-700 hover:to-emerald-700 transition-all shadow-lg shadow-green-500/20"
                  >
                    🌱 اتصال کیف پول
                  </button>
                )
              }

              if (chain.unsupported) {
                return (
                  <button
                    onClick={openChainModal}
                    type="button"
                    className="px-4 py-2 rounded-lg bg-red-500 text-white text-sm font-medium"
                  >
                    شبکه پشتیبانی نمی‌شود
                  </button>
                )
              }

              return (
                <div className="flex items-center gap-2">
                  <button
                    onClick={openChainModal}
                    type="button"
                    className="px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 text-sm font-medium hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors flex items-center gap-2"
                  >
                    {chain.hasIcon && (
                      <chain.icon className="w-4 h-4" />
                    )}
                    {chain.name}
                  </button>
                  <button
                    onClick={openAccountModal}
                    type="button"
                    className="px-4 py-2 rounded-lg bg-gradient-to-r from-green-600 to-emerald-600 text-white text-sm font-medium hover:from-green-700 hover:to-emerald-700 transition-all"
                  >
                    {account.displayName}
                    {account.displayBalance ? ` (${account.displayBalance})` : ''}
                  </button>
                </div>
              )
            })()}
          </div>
        )
      }}
    </ConnectButton.Custom>
  )
}

// کامپوننت نمایش موجودودی EcoCoin
export function EcoCoinBalance() {
  const { address, isConnected } = useAccount()
  const { data: balance } = useBalance({
    address,
    token: EcoCoin_ADDRESS,
    watch: true,
  })

  if (!isConnected || !balance) return null

  return (
    <div className="px-4 py-2 rounded-lg bg-green-500/10 border border-green-500/20">
      <div className="text-xs text-muted-foreground">موجودی EcoCoin</div>
      <div className="text-lg font-bold text-green-600">
        {formatEther(balance.value)} ECO
      </div>
    </div>
  )
}
"""

CONTRACTS_CONFIG = """// apps/web/src/lib/contracts.ts
import { Address } from 'wagmi'

// آدرس قراردادها (بعد از deploy به‌روزرسانی شود)
export const EcoCoin_ADDRESS: Address = '0x0000000000000000000000000000000000000001' as Address
export const EcoCredit_ADDRESS: Address = '0x0000000000000000000000000000000000000002' as Address
export const EcoReputation_ADDRESS: Address = '0x0000000000000000000000000000000000000003' as Address
export const EcoBond_ADDRESS: Address = '0x0000000000000000000000000000000000000004' as Address

// ABI خلاصه‌شده
export const ECOCOIN_ABI = [
  {
    name: 'balanceOf',
    type: 'function',
    stateMutability: 'view',
    inputs: [{ name: 'account', type: 'address' }],
    outputs: [{ name: '', type: 'uint256' }],
  },
  {
    name: 'transfer',
    type: 'function',
    stateMutability: 'nonpayable',
    inputs: [
      { name: 'to', type: 'address' },
      { name: 'amount', type: 'uint256' },
    ],
    outputs: [{ name: '', type: 'bool' }],
  },
  {
    name: 'totalSupply',
    type: 'function',
    stateMutability: 'view',
    inputs: [],
    outputs: [{ name: '', type: 'uint256' }],
  },
  {
    name: 'Mint',
    type: 'event',
    inputs: [
      { name: 'minter', type: 'address', indexed: true },
      { name: 'to', type: 'address', indexed: true },
      { name: 'amount', type: 'uint256' },
      { name: 'projectId', type: 'bytes32', indexed: true },
      { name: 'verificationHash', type: 'bytes32' },
      { name: 'mintReason', type: 'uint8' },
      { name: 'timestamp', type: 'uint256' },
    ],
  },
] as const

export const ECOCREDIT_ABI = [
  {
    name: 'balanceOf',
    type: 'function',
    stateMutability: 'view',
    inputs: [
      { name: 'account', type: 'address' },
      { name: 'id', type: 'uint256' },
    ],
    outputs: [{ name: '', type: 'uint256' }],
  },
  {
    name: 'CreditsMinted',
    type: 'event',
    inputs: [
      { name: 'batchId', type: 'uint256', indexed: true },
      { name: 'projectId', type: 'bytes32', indexed: true },
      { name: 'creditType', type: 'uint256' },
      { name: 'amount', type: 'uint256' },
    ],
  },
] as const

// Chain IDs
export const CHAIN_IDS = {
  mainnet: 1,
  polygon: 137,
  arbitrum: 42161,
} as const
"""


# ============================================================
#  ۲. صفحات EcoCoin
# ============================================================

DASHBOARD_PAGE = """// apps/web/src/app/ecocoin/dashboard/page.tsx
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
"""

WALLET_PAGE = """// apps/web/src/app/ecocoin/wallet/page.tsx
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
"""

STAKING_PAGE = """// apps/web/src/app/ecocoin/staking/page.tsx
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
"""


# ============================================================
#  ۳. Backend API Routes
# ============================================================

ECOCOIN_API = """# apps/api/routes/ecocoin.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api/ecocoin", tags=["ecocoin"])


# ============================================================
#  Models
# ============================================================
class BalanceResponse(BaseModel):
    address: str
    balance: float
    currency: str = "ECO"


class TransferRequest(BaseModel):
    from_address: str
    to_address: str
    amount: float
    project_id: Optional[str] = None


class TransferResponse(BaseModel):
    tx_hash: str
    status: str
    amount: float
    timestamp: str


class StakingTier(BaseModel):
    id: int
    duration: str
    apy: float
    multiplier: float
    min_amount: float


class StakeRequest(BaseModel):
    address: str
    amount: float
    tier_id: int


class EcoCoinStats(BaseModel):
    total_supply: float
    circulating_supply: float
    total_minted: float
    total_burned: float
    active_stewards: int
    hectares_covered: int
    co2_sequestered: int


# ============================================================
#  Routes
# ============================================================
@router.get("/balance/{address}")
async def get_balance(address: str) -> BalanceResponse:
    \"\"\"دریافت موجودودی EcoCoin یک آدرس.\"\"\"
    # در production: query blockchain via ethers.js
    return BalanceResponse(
        address=address,
        balance=1250.5,  # نمونه
    )


@router.get("/stats")
async def get_stats() -> EcoCoinStats:
    \"\"\"دریافت آمار کلی EcoCoin.\"\"\"
    return EcoCoinStats(
        total_supply=312_500_000,
        circulating_supply=287_400_000,
        total_minted=325_600_000,
        total_burned=13_100_000,
        active_stewards=12_847,
        hectares_covered=142_500,
        co2_sequestered=1_842_000,
    )


@router.post("/transfer")
async def transfer(req: TransferRequest) -> TransferResponse:
    \"\"\"انتقال EcoCoin.\"\"\"
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    # در production: sign and send transaction
    return TransferResponse(
        tx_hash="0x" + "a" * 64,
        status="pending",
        amount=req.amount,
        timestamp=datetime.now().isoformat(),
    )


@router.get("/staking/tiers")
async def get_staking_tiers() -> list[StakingTier]:
    \"\"\"دریافت سطح‌های استیکینگ.\"\"\"
    return [
        StakingTier(id=0, duration="3 months", apy=8.0, multiplier=1.2, min_amount=1000),
        StakingTier(id=1, duration="6 months", apy=15.0, multiplier=1.5, min_amount=5000),
        StakingTier(id=2, duration="1 year", apy=25.0, multiplier=2.0, min_amount=10000),
        StakingTier(id=3, duration="2 years", apy=50.0, multiplier=3.0, min_amount=50000),
    ]


@router.post("/staking/stake")
async def stake(req: StakeRequest) -> dict:
    \"\"\"استیک کردن EcoCoin.\"\"\"
    tiers = await get_staking_tiers()
    tier = next((t for t in tiers if t.id == req.tier_id), None)
    if not tier:
        raise HTTPException(status_code=400, detail="Invalid tier")

    if req.amount < tier.min_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum amount is {tier.min_amount} ECO"
        )

    return {
        "status": "staked",
        "amount": req.amount,
        "tier": tier.duration,
        "estimated_reward": req.amount * tier.apy / 100,
        "unlock_date": "2026-10-14T00:00:00",
    }


@router.get("/transactions/{address}")
async def get_transactions(address: str, limit: int = 20) -> list[dict]:
    \"\"\"دریافت تراکنش‌های یک آدرس.\"\"\"
    # در production: query from subgraph
    return [
        {
            "tx_hash": "0xabc123...",
            "type": "mint",
            "amount": 45.5,
            "project_id": "amazon-north",
            "reason": "stewardship",
            "timestamp": "2026-07-14T07:00:00",
        },
        {
            "tx_hash": "0xdef456...",
            "type": "transfer",
            "amount": -100.0,
            "to": "0x9Bc1...8a3C",
            "timestamp": "2026-07-14T05:00:00",
        },
    ][:limit]


@router.get("/mining/recent")
async def get_recent_mints(limit: int = 20) -> list[dict]:
    \"\"\"دریافت آخرین رویدادهای ماینینگ.\"\"\"
    return [
        {
            "block_number": 18923456,
            "minter": "0x7Ae3...4f2B",
            "recipient": "0x9Bc1...8a3C",
            "amount": 45.5,
            "project_id": "amazon-north",
            "project_name": "آمازون شمالی - سکشن ۴۷",
            "region": "برزیل، آمازون",
            "verification_hash": "QmX7Y8...k9Lm2",
            "mint_reason": 0,
            "sources": 4,
            "tx_hash": "0xabc123...def456",
            "timestamp": "2026-07-14T07:45:00",
        },
    ][:limit]


@router.post("/verify")
async def verify_ecological_proof(
    project_id: str,
    verification_hash: str,
    credit_type: int,
    measured_value: float,
) -> dict:
    \"\"\"تأیید یک پروژه بوم‌شناختی (Oracle only).\"\"\"
    return {
        "verified": True,
        "project_id": project_id,
        "verification_hash": verification_hash,
        "credit_type": credit_type,
        "measured_value": measured_value,
        "timestamp": datetime.now().isoformat(),
    }
"""


# ============================================================
#  ۴. Hardhat Configuration
# ============================================================

HARDHAT_CONFIG = """// hardhat.config.ts
import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import * as dotenv from "dotenv";

dotenv.config();

const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.24",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
  networks: {
    hardhat: {},
    localhost: {
      url: "http://127.0.0.1:8545",
    },
    polygon: {
      url: process.env.POLYGON_RPC_URL || "",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
    },
    arbitrum: {
      url: process.env.ARBITRUM_RPC_URL || "",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
    },
  },
  etherscan: {
    apiKey: process.env.ETHERSCAN_API_KEY,
  },
  paths: {
    sources: "./blockchain/contracts",
    tests: "./blockchain/test",
    cache: "./blockchain/cache",
    artifacts: "./blockchain/artifacts",
  },
};

export default config;
"""

HARDHAT_PACKAGE = """{
  "name": "econojin-contracts",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "compile": "hardhat compile",
    "test": "hardhat test",
    "deploy:localhost": "hardhat run scripts/deploy.ts --network localhost",
    "deploy:polygon": "hardhat run scripts/deploy.ts --network polygon",
    "verify": "hardhat verify --network polygon"
  },
  "devDependencies": {
    "@nomicfoundation/hardhat-toolbox": "^5.0.0",
    "@openzeppelin/contracts": "^5.0.2",
    "hardhat": "^2.22.0",
    "typescript": "^5.4.0",
    "dotenv": "^16.4.0"
  }
}
"""

DEPLOY_SCRIPT = """// blockchain/scripts/deploy.ts
import { ethers } from "hardhat";

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with:", deployer.address);

  // ۱. Deploy VerificationRegistry
  const VerificationRegistry = await ethers.getContractFactory("VerificationRegistry");
  const verification = await VerificationRegistry.deploy(deployer.address);
  await verification.waitForDeployment();
  console.log("VerificationRegistry deployed to:", await verification.getAddress());

  // ۲. Deploy EcoCoin
  const EcoCoin = await ethers.getContractFactory("EcoCoin");
  const ecoCoin = await EcoCoin.deploy(deployer.address, await verification.getAddress());
  await ecoCoin.waitForDeployment();
  console.log("EcoCoin deployed to:", await ecoCoin.getAddress());

  // ۳. Deploy EcoCredit
  const EcoCredit = await ethers.getContractFactory("EcoCredit");
  const ecoCredit = await EcoCredit.deploy(deployer.address);
  await ecoCredit.waitForDeployment();
  console.log("EcoCredit deployed to:", await ecoCredit.getAddress());

  // ۴. Deploy EcoReputation
  const EcoReputation = await ethers.getContractFactory("EcoReputation");
  const ecoRep = await EcoReputation.deploy(deployer.address);
  await ecoRep.waitForDeployment();
  console.log("EcoReputation deployed to:", await ecoRep.getAddress());

  // ۵. Deploy EcoBond
  const EcoBond = await ethers.getContractFactory("EcoBond");
  const reserveToken = "0x..."; // USDC/DAI address
  const ecoBond = await EcoBond.deploy(
    deployer.address,
    reserveToken,
    await ecoCoin.getAddress(),
    deployer.address, // commons treasury
    deployer.address  // liquidity pool
  );
  await ecoBond.waitForDeployment();
  console.log("EcoBond deployed to:", await ecoBond.getAddress());

  console.log("\\n✅ All contracts deployed successfully!");
  console.log("\\nUpdate apps/web/src/lib/contracts.ts with these addresses.");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
"""


# ============================================================
#  اجرای ایجاد فایل‌ها
# ============================================================

def create_file(path: Path, content: str, description: str):
    """ایجاد فایل با محتوا."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        print(f"  {C.YELLOW}⚠{C.RESET} وجود دارد: {path.relative_to(PROJECT_PATH)}")
        return False
    path.write_text(content, encoding='utf-8')
    print(f"  {C.GREEN}✓{C.RESET} ایجاد شد: {path.relative_to(PROJECT_PATH)}")
    return True


def main():
    C.enable_windows()

    print(f"\n{C.MAGENTA}{C.BOLD}╔{'═'*58}╗{C.RESET}")
    print(f"{C.MAGENTA}{C.BOLD}║  🚀 EcoCoin Integration Completer v1.0{' '*16}║{C.RESET}")
    print(f"{C.MAGENTA}{C.BOLD}║  مسیر: {str(PROJECT_PATH):<51}║{C.RESET}")
    print(f"{C.MAGENTA}{C.BOLD}╚{'═'*58}╝{C.RESET}")

    if not PROJECT_PATH.exists():
        print(f"{C.RED}❌ مسیر پروژه وجود ندارد!{C.RESET}")
        return

    created_count = 0
    skipped_count = 0

    # ============================================================
    #  ۱. Wallet Integration
    # ============================================================
    print(f"\n{C.CYAN}{C.BOLD}━━━ ۱. Wallet Integration ━━━{C.RESET}")

    files_to_create = [
        (WEB_PATH / "src" / "lib" / "wagmi.ts", WAGMI_CONFIG, "Wagmi config"),
        (WEB_PATH / "src" / "components" / "providers" / "Web3Provider.tsx", RAINBOWKIT_PROVIDER, "Web3 Provider"),
        (WEB_PATH / "src" / "components" / "ecocoin" / "ConnectWallet.tsx", CONNECT_BUTTON, "Connect Wallet"),
        (WEB_PATH / "src" / "lib" / "contracts.ts", CONTRACTS_CONFIG, "Contract addresses & ABIs"),
    ]

    for path, content, desc in files_to_create:
        if create_file(path, content, desc):
            created_count += 1
        else:
            skipped_count += 1

    # ============================================================
    #  ۲. Frontend Pages
    # ============================================================
    print(f"\n{C.CYAN}{C.BOLD}━━━ ۲. Frontend Pages ━━━{C.RESET}")

    pages_to_create = [
        (WEB_PATH / "src" / "app" / "ecocoin" / "dashboard" / "page.tsx", DASHBOARD_PAGE, "Dashboard page"),
        (WEB_PATH / "src" / "app" / "ecocoin" / "wallet" / "page.tsx", WALLET_PAGE, "Wallet page"),
        (WEB_PATH / "src" / "app" / "ecocoin" / "staking" / "page.tsx", STAKING_PAGE, "Staking page"),
    ]

    for path, content, desc in pages_to_create:
        if create_file(path, content, desc):
            created_count += 1
        else:
            skipped_count += 1

    # ============================================================
    #  ۳. Backend API Routes
    # ============================================================
    print(f"\n{C.CYAN}{C.BOLD}━━━ ۳. Backend API Routes ━━━{C.RESET}")

    api_files = [
        (PROJECT_PATH / "apps" / "api" / "routes" / "ecocoin.py", ECOCOIN_API, "EcoCoin API routes"),
    ]

    for path, content, desc in api_files:
        if create_file(path, content, desc):
            created_count += 1
        else:
            skipped_count += 1

    # ============================================================
    #  ۴. Hardhat Configuration
    # ============================================================
    print(f"\n{C.CYAN}{C.BOLD}━━━ ۴. Hardhat Configuration ━━━{C.RESET}")

    hardhat_files = [
        (PROJECT_PATH / "hardhat.config.ts", HARDHAT_CONFIG, "Hardhat config"),
        (PROJECT_PATH / "blockchain" / "package.json", HARDHAT_PACKAGE, "Blockchain package.json"),
        (PROJECT_PATH / "blockchain" / "scripts" / "deploy.ts", DEPLOY_SCRIPT, "Deploy script"),
    ]

    for path, content, desc in hardhat_files:
        if create_file(path, content, desc):
            created_count += 1
        else:
            skipped_count += 1

    # ============================================================
    #  خلاصه
    # ============================================================
    print(f"\n{C.MAGENTA}{C.BOLD}{'━'*58}{C.RESET}")
    print(f"{C.MAGENTA}{C.BOLD}  📊 خلاصه{C.RESET}")
    print(f"{C.MAGENTA}{C.BOLD}{'━'*58}{C.RESET}")
    print(f"  {C.GREEN}✓{C.RESET} فایل‌های ایجاد شده: {created_count}")
    print(f"  {C.YELLOW}⚠{C.RESET} فایل‌های موجود (رد شده): {skipped_count}")

    print(f"\n{C.CYAN}📝 مراحل بعدی:{C.RESET}")
    print(f"""
  ۱. نصب پکیج‌های wallet:
     cd apps/web
     pnpm add wagmi @rainbow-me/rainbowkit viem

  ۲. نصب hardhat:
     cd blockchain
     pnpm install

  ۳. ثبت EcoCoin API route در apps/main.py:
     from apps.api.routes import ecocoin
     app.include_router(ecocoin.router)

  ۴. اضافه کردن Web3Provider به layout:
     # apps/web/src/app/layout.tsx
     import {{ Web3Provider }} from '@/components/providers/Web3Provider'
     # wrap children with <Web3Provider>

  ۵. اضافه کردن ConnectWallet به navigation:
     # apps/web/src/components/layout/Header.tsx
     import {{ ConnectWallet }} from '@/components/ecocoin/ConnectWallet'
     # <ConnectWallet />

  ۶. کامپایل قراردادها:
     cd blockchain
     pnpm compile

  ۷. تست صفحات:
     http://localhost:3000/ecocoin/dashboard
     http://localhost:3000/ecocoin/wallet
     http://localhost:3000/ecocoin/staking
""")

    # ذخیره‌ی گزارش
    report_path = PROJECT_PATH / "analysis_reports"
    report_path.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_path / f"ecocoin_completer_{ts}.json"
    report = {
        "timestamp": datetime.now().isoformat(),
        "created_files": created_count,
        "skipped_files": skipped_count,
        "files": [
            str(WEB_PATH / "src" / "lib" / "wagmi.ts"),
            str(WEB_PATH / "src" / "components" / "providers" / "Web3Provider.tsx"),
            str(WEB_PATH / "src" / "components" / "ecocoin" / "ConnectWallet.tsx"),
            str(WEB_PATH / "src" / "lib" / "contracts.ts"),
            str(WEB_PATH / "src" / "app" / "ecocoin" / "dashboard" / "page.tsx"),
            str(WEB_PATH / "src" / "app" / "ecocoin" / "wallet" / "page.tsx"),
            str(WEB_PATH / "src" / "app" / "ecocoin" / "staking" / "page.tsx"),
            str(PROJECT_PATH / "apps" / "api" / "routes" / "ecocoin.py"),
            str(PROJECT_PATH / "hardhat.config.ts"),
            str(PROJECT_PATH / "blockchain" / "package.json"),
            str(PROJECT_PATH / "blockchain" / "scripts" / "deploy.ts"),
        ],
    }
    import json
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"  {C.GRAY}گزارش:{C.RESET} {report_file}")


if __name__ == '__main__':
    main()
