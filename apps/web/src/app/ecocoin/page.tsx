"use client";

import { useState } from 'react';
import { useTranslation } from '@/hooks/useTranslation';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { useWallet, useTokenStats, useTransactions, useTransfer, useStake } from '@/hooks/blockchain/useBlockchain';
import { 
  Wallet, Coins, TrendingUp, ArrowUpRight, ArrowDownRight,
  Lock, Unlock, History, DollarSign, Leaf, Zap
} from 'lucide-react';

export default function EcoCoinPage() {
  const { t } = useTranslation();
  const [transferTo, setTransferTo] = useState('');
  const [transferAmount, setTransferAmount] = useState('');
  const [transferToken, setTransferToken] = useState('ECO');
  const [stakeAmount, setStakeAmount] = useState('');
  const [stakeToken, setStakeToken] = useState('ECO');
  const [lockDays, setLockDays] = useState(30);
  
  const { data: wallet } = useWallet();
  const { data: stats } = useTokenStats();
  const { data: transactions } = useTransactions();
  const transferMutation = useTransfer();
  const stakeMutation = useStake();

  const handleTransfer = () => {
    if (transferTo && transferAmount) {
      transferMutation.mutate({
        to: transferTo,
        amount: parseFloat(transferAmount),
        token: transferToken
      });
    }
  };

  const handleStake = () => {
    if (stakeAmount) {
      stakeMutation.mutate({
        amount: parseFloat(stakeAmount),
        token: stakeToken,
        lock_days: lockDays
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 pt-20">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">{t('ecocoin.title')}</h1>
          <p className="text-slate-400">{t('ecocoin.subtitle')}</p>
        </div>

        {/* Wallet Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <Card className="bg-gradient-to-br from-emerald-900/30 to-emerald-800/10 border-emerald-800 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <Leaf className="w-5 h-5 text-emerald-400" />
                ECO Token
              </h3>
              <Badge className="bg-emerald-600">Utility Token</Badge>
            </div>
            <div className="text-4xl font-bold text-white mb-2">
              {wallet?.balance_eco?.toFixed(2) || '0.00'} ECO
            </div>
            <div className="text-sm text-slate-400 mb-4">
              ≈ ${(wallet?.balance_eco || 0) * (stats?.eco?.price_usd || 0.5)} USD
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="bg-slate-900/50 rounded p-2">
                <div className="text-slate-400">Staked</div>
                <div className="text-white font-bold">{wallet?.staked_eco?.toFixed(2) || '0.00'}</div>
              </div>
              <div className="bg-slate-900/50 rounded p-2">
                <div className="text-slate-400">{t('ecocoin.price')}</div>
                <div className="text-emerald-400 font-bold">${stats?.eco?.price_usd || '0.50'}</div>
              </div>
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-blue-900/30 to-blue-800/10 border-blue-800 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <Zap className="w-5 h-5 text-blue-400" />
                GRC Token
              </h3>
              <Badge className="bg-blue-600">Carbon Credit</Badge>
            </div>
            <div className="text-4xl font-bold text-white mb-2">
              {wallet?.balance_grc?.toFixed(2) || '0.00'} GRC
            </div>
            <div className="text-sm text-slate-400 mb-4">
              ≈ ${(wallet?.balance_grc || 0) * (stats?.grc?.price_usd || 10)} USD
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="bg-slate-900/50 rounded p-2">
                <div className="text-slate-400">Staked</div>
                <div className="text-white font-bold">{wallet?.staked_grc?.toFixed(2) || '0.00'}</div>
              </div>
              <div className="bg-slate-900/50 rounded p-2">
                <div className="text-slate-400">{t('ecocoin.price')}</div>
                <div className="text-blue-400 font-bold">${stats?.grc?.price_usd || '10.00'}</div>
              </div>
            </div>
          </Card>
        </div>

        {/* Market Stats */}
        {stats && (
          <Card className="bg-slate-900/50 border-slate-800 p-6 mb-6">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-blue-400" />
              آمار بازار
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-slate-800/50 rounded-lg p-4">
                <div className="text-sm text-slate-400 mb-1">Market Cap ECO</div>
                <div className="text-xl font-bold text-white">
                  ${((stats.eco?.market_cap || 0) / 1000000).toFixed(2)}M
                </div>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-4">
                <div className="text-sm text-slate-400 mb-1">Market Cap GRC</div>
                <div className="text-xl font-bold text-white">
                  ${((stats.grc?.market_cap || 0) / 1000000).toFixed(2)}M
                </div>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-4">
                <div className="text-sm text-slate-400 mb-1">کل کیف پول‌ها</div>
                <div className="text-xl font-bold text-white">{stats.total_wallets || 0}</div>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-4">
                <div className="text-sm text-slate-400 mb-1">کل تراکنش‌ها</div>
                <div className="text-xl font-bold text-white">{stats.total_transactions || 0}</div>
              </div>
            </div>
          </Card>
        )}

        {/* Transfer & Stake */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <Card className="bg-slate-900/50 border-slate-800 p-6">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <ArrowUpRight className="w-5 h-5 text-emerald-400" />
              انتقال توکن
            </h3>
            <div className="space-y-3">
              <div>
                <label className="text-sm text-slate-400 mb-1 block">آدرس مقصد</label>
                <Input
                  value={transferTo}
                  onChange={(e) => setTransferTo(e.target.value)}
                  placeholder="0x..."
                  className="bg-slate-800 border-slate-700 text-white font-mono"
                />
              </div>
              <div>
                <label className="text-sm text-slate-400 mb-1 block">مقدار</label>
                <Input
                  type="number"
                  step="0.01"
                  value={transferAmount}
                  onChange={(e) => setTransferAmount(e.target.value)}
                  placeholder="0.00"
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>
              <div>
                <label className="text-sm text-slate-400 mb-1 block">توکن</label>
                <select
                  value={transferToken}
                  onChange={(e) => setTransferToken(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded px-3 py-2"
                >
                  <option value="ECO">ECO Token</option>
                  <option value="GRC">GRC Token</option>
                </select>
              </div>
              <Button 
                onClick={handleTransfer}
                className="w-full bg-emerald-600 hover:bg-emerald-700"
                disabled={transferMutation.isPending}
              >
                {transferMutation.isPending ? 'در حال انتقال...' : 'انتقال'}
              </Button>
            </div>
          </Card>

          <Card className="bg-slate-900/50 border-slate-800 p-6">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Lock className="w-5 h-5 text-purple-400" />
              Staking
            </h3>
            <div className="space-y-3">
              <div>
                <label className="text-sm text-slate-400 mb-1 block">مقدار</label>
                <Input
                  type="number"
                  step="0.01"
                  value={stakeAmount}
                  onChange={(e) => setStakeAmount(e.target.value)}
                  placeholder="0.00"
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>
              <div>
                <label className="text-sm text-slate-400 mb-1 block">توکن</label>
                <select
                  value={stakeToken}
                  onChange={(e) => setStakeToken(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded px-3 py-2"
                >
                  <option value="ECO">ECO (8% APY)</option>
                  <option value="GRC">GRC (12% APY)</option>
                </select>
              </div>
              <div>
                <label className="text-sm text-slate-400 mb-1 block">مدت قفل (روز)</label>
                <Input
                  type="number"
                  value={lockDays}
                  onChange={(e) => setLockDays(parseInt(e.target.value))}
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>
              <Button 
                onClick={handleStake}
                className="w-full bg-purple-600 hover:bg-purple-700"
                disabled={stakeMutation.isPending}
              >
                {stakeMutation.isPending ? 'در حال stake...' : 'Stake کردن'}
              </Button>
            </div>
          </Card>
        </div>

        {/* Transaction History */}
        {transactions && transactions.length > 0 && (
          <Card className="bg-slate-900/50 border-slate-800 p-6">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <History className="w-5 h-5 text-blue-400" />
              تاریخچه تراکنش‌ها
            </h3>
            <div className="space-y-2">
              {transactions.slice(0, 10).map((tx: any, idx: number) => (
                <div key={idx} className="bg-slate-800/50 rounded-lg p-3 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {tx.tx_type === 'reward' ? (
                      <ArrowDownRight className="w-5 h-5 text-green-400" />
                    ) : (
                      <ArrowUpRight className="w-5 h-5 text-red-400" />
                    )}
                    <div>
                      <div className="text-sm font-medium text-white">{tx.tx_type}</div>
                      <div className="text-xs text-slate-400">{tx.timestamp}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`font-bold ${tx.tx_type === 'reward' ? 'text-green-400' : 'text-white'}`}>
                      {tx.tx_type === 'reward' ? '+' : '-'}{tx.amount?.toFixed(2)} {tx.token_type}
                    </div>
                    <div className="text-xs text-slate-400 font-mono">{tx.tx_hash?.slice(0, 10)}...</div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Info */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <Card className="bg-slate-900/50 border-slate-800 p-4">
            <h4 className="font-bold text-white mb-2">شبکه Polygon</h4>
            <p className="text-sm text-slate-400">تراکنش‌های سریع و کم‌هزینه بر بستر L2</p>
          </Card>
          <Card className="bg-slate-900/50 border-slate-800 p-4">
            <h4 className="font-bold text-white mb-2">پاداش سبز</h4>
            <p className="text-sm text-slate-400">کسب توکن با اقدامات زیست‌محیطی</p>
          </Card>
          <Card className="bg-slate-900/50 border-slate-800 p-4">
            <h4 className="font-bold text-white mb-2">Staking سودآور</h4>
            <p className="text-sm text-slate-400">۸-۱۲٪ APY با قفل کردن توکن</p>
          </Card>
        </div>
      </div>
    </div>
  );
}
