// apps/web/src/lib/wagmi.ts
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
