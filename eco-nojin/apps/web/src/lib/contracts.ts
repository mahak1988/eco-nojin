// apps/web/src/lib/contracts.ts

// آدرس‌های قراردادهای Mock (همان‌هایی که در بک‌اند تعریف کردیم)
export const CONTRACTS = {
  EcoCoin: "0x0000000000000000000000000000000000000001",
  VerificationOracle: "0x0000000000000000000000000000000000000002",
  MrvRegistry: "0x0000000000000000000000000000000000000003",
} as const;

// ABI حداقلی برای تعامل فرانت‌اند با قرارداد EcoCoin
// (شما می‌توانید بعداً ABI کامل را از کامپایل Hardhat/Foundry جایگزین کنید)
export const ECOCOIN_ABI = [
  {
    "inputs": [{ "internalType": "address", "name": "account", "type": "address" }],
    "name": "balanceOf",
    "outputs": [{ "internalType": "uint256", "name": "", "type": "uint256" }],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      { "internalType": "address", "name": "to", "type": "address" },
      { "internalType": "uint256", "name": "amount", "type": "uint256" }
    ],
    "name": "transfer",
    "outputs": [{ "internalType": "bool", "name": "", "type": "bool" }],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "totalSupply",
    "outputs": [{ "internalType": "uint256", "name": "", "type": "uint256" }],
    "stateMutability": "view",
    "type": "function"
  }
] as const;

// نوع داده برای TypeScript
export type ContractName = keyof typeof CONTRACTS;