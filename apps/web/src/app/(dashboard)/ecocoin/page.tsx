"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Coins,
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  ArrowDownLeft,
  Gift,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Send,
  Wallet,
  History,
  BarChart3,
} from "lucide-react";
import { useEcoCoinDashboard, useTransferEcoCoin } from "@/lib/api/hooks/useEcoCoin";
import { format } from "date-fns";
import { faIR } from "date-fns/locale";

export default function EcoCoinPage() {
  const { balance, transactions, rewards, stats, isLoading } = useEcoCoinDashboard();
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [activeTab, setActiveTab] = useState<'transactions' | 'rewards'>('transactions');

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-emerald-500 border-t-transparent" />
          <p className="mt-4 text-zinc-400">در حال بارگذاری...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <div>
            <h1 className="text-4xl font-black text-white mb-2">کیف پول اکو کوین</h1>
            <p className="text-zinc-400">مدیریت دارایی‌های دیجیتال شما</p>
          </div>
          <button
            onClick={() => setShowTransferModal(true)}
            className="px-6 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 rounded-xl font-bold text-white transition-all shadow-[0_0_30px_rgba(16,185,129,0.3)] hover:shadow-[0_0_40px_rgba(16,185,129,0.5)] flex items-center gap-2"
          >
            <Send className="h-5 w-5" />
            انتقال اکو کوین
          </button>
        </motion.div>

        {/* Balance Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Available Balance */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="relative bg-gradient-to-br from-emerald-500/10 to-teal-500/5 backdrop-blur-2xl border border-emerald-500/20 rounded-2xl p-6 overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/20 rounded-full blur-3xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-4">
                <Wallet className="h-5 w-5 text-emerald-400" />
                <span className="text-sm text-zinc-400">موجودی قابل برداشت</span>
              </div>
              <p className="text-3xl font-black text-white tabular-nums">
                {balance?.available_balance?.toLocaleString() || 0}
              </p>
              <p className="text-sm text-emerald-400 mt-2">ECO</p>
            </div>
          </motion.div>

          {/* Staked Balance */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="relative bg-gradient-to-br from-blue-500/10 to-cyan-500/5 backdrop-blur-2xl border border-blue-500/20 rounded-2xl p-6 overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/20 rounded-full blur-3xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="h-5 w-5 text-blue-400" />
                <span className="text-sm text-zinc-400">سرمایه‌گذاری شده</span>
              </div>
              <p className="text-3xl font-black text-white tabular-nums">
                {balance?.staked_balance?.toLocaleString() || 0}
              </p>
              <p className="text-sm text-blue-400 mt-2">ECO</p>
            </div>
          </motion.div>

          {/* Pending Balance */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="relative bg-gradient-to-br from-amber-500/10 to-orange-500/5 backdrop-blur-2xl border border-amber-500/20 rounded-2xl p-6 overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-32 h-32 bg-amber-500/20 rounded-full blur-3xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-4">
                <Clock className="h-5 w-5 text-amber-400" />
                <span className="text-sm text-zinc-400">در انتظار تأیید</span>
              </div>
              <p className="text-3xl font-black text-white tabular-nums">
                {balance?.pending_balance?.toLocaleString() || 0}
              </p>
              <p className="text-sm text-amber-400 mt-2">ECO</p>
            </div>
          </motion.div>

          {/* Total Balance */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="relative bg-gradient-to-br from-purple-500/10 to-pink-500/5 backdrop-blur-2xl border border-purple-500/20 rounded-2xl p-6 overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/20 rounded-full blur-3xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-4">
                <Coins className="h-5 w-5 text-purple-400" />
                <span className="text-sm text-zinc-400">مجموع دارایی</span>
              </div>
              <p className="text-3xl font-black text-white tabular-nums">
                {balance?.balance?.toLocaleString() || 0}
              </p>
              <p className="text-sm text-purple-400 mt-2">ECO</p>
            </div>
          </motion.div>
        </div>

        {/* Tabs */}
        <div className="bg-white/[0.03] backdrop-blur-2xl border border-white/10 rounded-2xl p-2">
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab('transactions')}
              className={`flex-1 py-3 rounded-xl font-medium transition-all flex items-center justify-center gap-2 ${
                activeTab === 'transactions'
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : 'text-zinc-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <History className="h-5 w-5" />
              تراکنش‌ها
            </button>
            <button
              onClick={() => setActiveTab('rewards')}
              className={`flex-1 py-3 rounded-xl font-medium transition-all flex items-center justify-center gap-2 ${
                activeTab === 'rewards'
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : 'text-zinc-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <Gift className="h-5 w-5" />
              پاداش‌ها
            </button>
          </div>
        </div>

        {/* Content */}
        {activeTab === 'transactions' ? (
          <div className="bg-white/[0.03] backdrop-blur-2xl border border-white/10 rounded-2xl p-6">
            <h2 className="text-xl font-bold text-white mb-6">تراکنش‌های اخیر</h2>
            <div className="space-y-4">
              {transactions?.data?.transactions?.map((tx) => (
                <TransactionItem key={tx.id} transaction={tx} />
              ))}
            </div>
          </div>
        ) : (
          <div className="bg-white/[0.03] backdrop-blur-2xl border border-white/10 rounded-2xl p-6">
            <h2 className="text-xl font-bold text-white mb-6">پاداش‌های دریافتی</h2>
            <div className="space-y-4">
              {rewards?.data?.map((reward) => (
                <RewardItem key={reward.id} reward={reward} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// Transaction Item Component
// ============================================================================

function TransactionItem({ transaction }: { transaction: any }) {
  const isIncoming = transaction.type === 'transfer_in' || transaction.type === 'reward';
  const Icon = isIncoming ? ArrowDownLeft : ArrowUpRight;
  const color = isIncoming ? 'text-emerald-400' : 'text-rose-400';
  const bgColor = isIncoming ? 'bg-emerald-500/10' : 'bg-rose-500/10';

  const statusConfig = {
    completed: { color: 'text-emerald-400', icon: CheckCircle, label: 'تکمیل شده' },
    pending: { color: 'text-amber-400', icon: Clock, label: 'در انتظار' },
    failed: { color: 'text-rose-400', icon: XCircle, label: 'ناموفق' },
    cancelled: { color: 'text-zinc-400', icon: AlertCircle, label: 'لغو شده' },
  };

  const status = statusConfig[transaction.status as keyof typeof statusConfig];
  const StatusIcon = status.icon;

  return (
    <div className="flex items-center justify-between p-4 bg-black/20 rounded-xl border border-white/5 hover:border-white/10 transition-all">
      <div className="flex items-center gap-4">
        <div className={`p-3 rounded-xl ${bgColor}`}>
          <Icon className={`h-5 w-5 ${color}`} />
        </div>
        <div>
          <p className="text-white font-medium">{transaction.description || transaction.type}</p>
          <p className="text-sm text-zinc-400">
            {format(new Date(transaction.created_at), 'yyyy/MM/dd HH:mm', { locale: faIR })}
          </p>
        </div>
      </div>
      <div className="text-right">
        <p className={`text-lg font-bold ${color} tabular-nums`}>
          {isIncoming ? '+' : '-'}{transaction.amount.toLocaleString()} ECO
        </p>
        <div className={`flex items-center gap-1 text-xs ${status.color}`}>
          <StatusIcon className="h-3 w-3" />
          {status.label}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Reward Item Component
// ============================================================================

function RewardItem({ reward }: { reward: any }) {
  return (
    <div className="flex items-center justify-between p-4 bg-black/20 rounded-xl border border-white/5 hover:border-white/10 transition-all">
      <div className="flex items-center gap-4">
        <div className="p-3 rounded-xl bg-amber-500/10">
          <Gift className="h-5 w-5 text-amber-400" />
        </div>
        <div>
          <p className="text-white font-medium">{reward.description}</p>
          <p className="text-sm text-zinc-400">{reward.source}</p>
        </div>
      </div>
      <div className="text-right">
        <p className="text-lg font-bold text-amber-400 tabular-nums">
          +{reward.amount.toLocaleString()} ECO
        </p>
        <p className="text-xs text-zinc-400">
          {format(new Date(reward.created_at), 'yyyy/MM/dd', { locale: faIR })}
        </p>
      </div>
    </div>
  );
}