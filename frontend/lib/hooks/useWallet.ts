'use client';

import { useState, useEffect, useCallback } from 'react';

declare global {
  interface Window {
    ethereum?: any;
  }
}

interface WalletState {
  address: string | null;
  chainId: string | null;
  connected: boolean;
  connecting: boolean;
  error: string | null;
}

export function useWallet() {
  const [state, setState] = useState<WalletState>({
    address: null,
    chainId: null,
    connected: false,
    connecting: false,
    error: null,
  });

  const connect = useCallback(async () => {
    if (typeof window === 'undefined' || !window.ethereum) {
      setState(s => ({ ...s, error: 'MetaMask not installed. Get it at metamask.io' }));
      return;
    }

    setState(s => ({ ...s, connecting: true, error: null }));
    try {
      const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
      const chainId = await window.ethereum.request({ method: 'eth_chainId' });
      setState({
        address: accounts[0],
        chainId,
        connected: true,
        connecting: false,
        error: null,
      });
    } catch (err: any) {
      setState(s => ({ ...s, connecting: false, error: err.message || 'Connection failed' }));
    }
  }, []);

  const disconnect = useCallback(() => {
    setState({ address: null, chainId: null, connected: false, connecting: false, error: null });
  }, []);

  const switchToPolygon = useCallback(async () => {
    if (!window.ethereum) return;
    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: '0x89' }], // Polygon mainnet = 137
      });
    } catch (err: any) {
      if (err.code === 4902) {
        await window.ethereum.request({
          method: 'wallet_addEthereumChain',
          params: [{
            chainId: '0x89',
            chainName: 'Polygon',
            nativeCurrency: { name: 'MATIC', symbol: 'MATIC', decimals: 18 },
            rpcUrls: ['https://polygon-rpc.com'],
            blockExplorerUrls: ['https://polygonscan.com'],
          }],
        });
      }
    }
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined' || !window.ethereum) return;

    const handleAccountsChanged = (accounts: string[]) => {
      if (accounts.length === 0) {
        disconnect();
      } else {
        setState(s => ({ ...s, address: accounts[0] }));
      }
    };

    const handleChainChanged = (chainId: string) => {
      setState(s => ({ ...s, chainId }));
    };

    window.ethereum.on('accountsChanged', handleAccountsChanged);
    window.ethereum.on('chainChanged', handleChainChanged);

    // Auto-reconnect if previously connected
    window.ethereum.request({ method: 'eth_accounts' }).then((accounts: string[]) => {
      if (accounts.length > 0) {
        window.ethereum.request({ method: 'eth_chainId' }).then((chainId: string) => {
          setState({ address: accounts[0], chainId, connected: true, connecting: false, error: null });
        });
      }
    });

    return () => {
      window.ethereum?.removeListener('accountsChanged', handleAccountsChanged);
      window.ethereum?.removeListener('chainChanged', handleChainChanged);
    };
  }, [disconnect]);

  return { ...state, connect, disconnect, switchToPolygon };
}
