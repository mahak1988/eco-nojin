// apps/web/src/lib/contracts.ts
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
