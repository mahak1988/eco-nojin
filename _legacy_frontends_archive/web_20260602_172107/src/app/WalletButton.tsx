'use client';

import { Wallet, Loader2, CheckCircle } from 'lucide-react';
import { useWallet } from '@/lib/hooks/useWallet';

export default function WalletButton() {
  const { address, connected, connecting, error, connect, disconnect, switchToPolygon } = useWallet();

  const shortenAddress = (addr: string) => `${addr.slice(0, 6)}...${addr.slice(-4)}`;

  if (connecting) {
    return (
      <button disabled className="flex items-center gap-2 px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg">
        <Loader2 className="w-4 h-4 animate-spin" />
        Connecting...
      </button>
    );
  }

  if (connected && address) {
    return (
      <div className="flex items-center gap-2">
        <button onClick={switchToPolygon} className="flex items-center gap-2 px-3 py-2 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded-lg hover:bg-purple-200 transition text-sm">
          <CheckCircle className="w-4 h-4" />
          Polygon
        </button>
        <a href={`/portfolio/${address}`} className="flex items-center gap-2 px-3 py-2 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-lg hover:bg-green-200 transition text-sm font-medium">
          <Wallet className="w-4 h-4" />
          {shortenAddress(address)}
        </a>
        <button onClick={disconnect} className="px-3 py-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 text-sm">
          Disconnect
        </button>
      </div>
    );
  }

  return (
    <button onClick={connect} className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition font-medium">
      <Wallet className="w-4 h-4" />
      Connect Wallet
    </button>
  );
}
