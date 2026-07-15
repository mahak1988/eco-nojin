// apps/web/src/components/providers/Web3Provider.tsx
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
