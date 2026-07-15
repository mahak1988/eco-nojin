// apps/web/src/components/ecocoin/ConnectWallet.tsx
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
