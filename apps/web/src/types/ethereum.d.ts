/**
 * ============================================================================
 *  Ethereum provider type declarations (window.ethereum) — EIP-1193
 * ============================================================================
 */

export type HexString = `0x${string}`;
export type TxHash = `0x${string}`;

export interface EIP1193RequestArguments {
  readonly method: string;
  readonly params?: readonly unknown[] | object;
}

export interface ProviderRpcError extends Error {
  readonly code: 4001 | 4100 | 4200 | 4900 | 4901 | number;
  readonly data?: unknown;
}

export interface ChainInfo {
  chainId: HexString;
  chainName: string;
  nativeCurrency: {
    name: string;
    symbol: string;
    decimals: 18;
  };
  rpcUrls: readonly string[];
  blockExplorerUrls?: readonly string[];
}

export interface EthereumProviderEvents {
  accountsChanged: (accounts: readonly HexString[]) => void;
  chainChanged: (chainId: HexString) => void;
  connect: (info: { chainId: HexString }) => void;
  disconnect: (error: ProviderRpcError) => void;
  message: (message: { type: string; data: unknown }) => void;
}

export interface EIP1193Provider {
  request<T = unknown>(args: EIP1193RequestArguments): Promise<T>;
  on<K extends keyof EthereumProviderEvents>(
    event: K,
    handler: EthereumProviderEvents[K],
  ): void;
  removeListener<K extends keyof EthereumProviderEvents>(
    event: K,
    handler: EthereumProviderEvents[K],
  ): void;
  isMetaMask?: boolean;
  isRabby?: boolean;
  isCoinbaseWallet?: boolean;
  providers?: readonly EIP1193Provider[];
}

declare global {
  interface Window {
    ethereum?: EIP1193Provider & {
      readonly isEconojin?: boolean;
    };
  }
}

export {};
