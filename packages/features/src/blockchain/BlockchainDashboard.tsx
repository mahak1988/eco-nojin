"use client";

import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useWallet, useTokenStats } from '@/hooks/blockchain/useBlockchain';
import { Wallet, TrendingUp, Coins } from 'lucide-react';

export function BlockchainDashboard() {
  const { data: wallet } = useWallet();
  const { data: stats } = useTokenStats();

  return (
    <div className="space-y-4">
      <Card className="bg-slate-900/50 border-slate-800 p-6">
        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <Wallet className="w-5 h-5 text-emerald-400" />
          کیف پول EcoCoin
        </h3>
        
        {wallet && (
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-emerald-900/30 border border-emerald-800 rounded-lg p-4">
              <div className="text-sm text-emerald-400 mb-1">ECO Balance</div>
              <div className="text-3xl font-bold text-white">{wallet.balance_eco?.toFixed(2)}</div>
              <div className="text-xs text-slate-400">Staked: {wallet.staked_eco?.toFixed(2)}</div>
            </div>
            
            <div className="bg-blue-900/30 border border-blue-800 rounded-lg p-4">
              <div className="text-sm text-blue-400 mb-1">GRC Balance</div>
              <div className="text-3xl font-bold text-white">{wallet.balance_grc?.toFixed(2)}</div>
              <div className="text-xs text-slate-400">Staked: {wallet.staked_grc?.toFixed(2)}</div>
            </div>
          </div>
        )}
      </Card>

      {stats && (
        <Card className="bg-slate-900/50 border-slate-800 p-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-blue-400" />
            آمار بازار
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-800/50 rounded-lg p-4">
              <div className="text-sm text-slate-400 mb-1">ECO Price</div>
              <div className="text-2xl font-bold text-white">${stats.eco?.price_usd}</div>
              <div className="text-xs text-slate-400">Market Cap: ${(stats.eco?.market_cap / 1000000).toFixed(2)}M</div>
            </div>
            
            <div className="bg-slate-800/50 rounded-lg p-4">
              <div className="text-sm text-slate-400 mb-1">GRC Price</div>
              <div className="text-2xl font-bold text-white">${stats.grc?.price_usd}</div>
              <div className="text-xs text-slate-400">Market Cap: ${(stats.grc?.market_cap / 1000000).toFixed(2)}M</div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
