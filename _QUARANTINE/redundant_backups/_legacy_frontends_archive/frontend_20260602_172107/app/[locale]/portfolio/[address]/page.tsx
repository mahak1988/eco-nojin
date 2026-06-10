'use client';
import React from 'react';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { Wallet, Leaf, Award, TrendingUp, ExternalLink, Copy, CheckCircle, Loader2 } from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';
import { useWallet } from '@/lib/hooks/useWallet';

export default function PortfolioPage() {
  const params = useParams();
  const locale = (params.locale as Locale) || 'fa';
  const address = (params.address as string) || '';
  const dict = getDictionary(locale);
  const isPersian = locale === 'fa' || locale === 'ar' || locale === 'ur';
  const wallet = useWallet();

  const [copied, setCopied] = useState(false);
  const [portfolio, setPortfolio] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPortfolio = async () => {
      try {
        const res = await fetch(`http://localhost:8000/gaia/portfolio/${address}`);
        if (res.ok) {
          const data = await res.json();
          setPortfolio(data);
        } else {
          // Mock portfolio for demo
          setPortfolio({
            total_certificates: 3,
            total_carbon_kg: 203558,
            total_carbon_tons: 203.56,
            estimated_value_usd: 10177.92,
            certificates: [
              { id: 1, type: 'tree_planting', carbon_kg: 150000, health: 0.94, stage: 'mature' },
              { id: 2, type: 'soil_regeneration', carbon_kg: 28000, health: 0.87, stage: 'improving' },
              { id: 3, type: 'agroforestry', carbon_kg: 25558, health: 0.91, stage: 'young' },
            ],
          });
        }
      } catch {
        setPortfolio({ total_certificates: 0, total_carbon_kg: 0, total_carbon_tons: 0, estimated_value_usd: 0, certificates: [] });
      } finally {
        setLoading(false);
      }
    };
    if (address) fetchPortfolio();
  }, [address]);

  const copyAddress = () => {
    navigator.clipboard.writeText(address);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const shortenAddress = (addr: string) => `${addr.slice(0, 6)}...${addr.slice(-4)}`;

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center pt-20">
        <Loader2 className="w-12 h-12 text-purple-600 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 dark:from-gray-900 dark:to-gray-800 pt-20">
      <div className="max-w-6xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-2xl p-8 text-white mb-8 shadow-2xl">
          <div className="flex items-center gap-4 mb-4">
            <Wallet className="w-12 h-12" />
            <div>
              <h1 className="text-3xl font-bold">{dict?.portfolio?.title || (isPersian ? 'پورتفولیو' : 'Portfolio')}</h1>
              <div className="flex items-center gap-2 mt-2">
                <code className="bg-white/20 backdrop-blur px-3 py-1 rounded-lg font-mono text-sm">
                  {shortenAddress(address)}
                </code>
                <button onClick={copyAddress} className="p-1 hover:bg-white/20 rounded transition">
                  {copied ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                </button>
                <a href={`https://polygonscan.com/address/${address}`} target="_blank" rel="noopener" className="p-1 hover:bg-white/20 rounded transition">
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-xl">
            <Leaf className="w-10 h-10 text-green-500 mb-3" />
            <div className="text-sm text-gray-500 mb-1">{dict?.portfolio?.totalCarbon || 'Total Carbon'}</div>
            <div className="text-3xl font-bold">{(portfolio?.total_carbon_tons || 0).toFixed(2)} t</div>
            <div className="text-xs text-gray-400 mt-1">CO₂ absorbed</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-xl">
            <Award className="w-10 h-10 text-yellow-500 mb-3" />
            <div className="text-sm text-gray-500 mb-1">{dict?.portfolio?.totalTokens || 'SEED Tokens'}</div>
            <div className="text-3xl font-bold">{Math.round((portfolio?.total_carbon_tons || 0) * 100).toLocaleString()}</div>
            <div className="text-xs text-gray-400 mt-1">SEED</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-xl">
            <TrendingUp className="w-10 h-10 text-blue-500 mb-3" />
            <div className="text-sm text-gray-500 mb-1">{isPersian ? 'ارزش تخمینی' : 'Est. Value'}</div>
            <div className="text-3xl font-bold">${(portfolio?.estimated_value_usd || 0).toLocaleString()}</div>
            <div className="text-xs text-gray-400 mt-1">USD</div>
          </div>
        </div>

        {/* NFT Certificates */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-xl">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <Award className="w-6 h-6 text-purple-600" />
            {dict?.portfolio?.nftCertificates || 'NFT Certificates'}
          </h2>
          <div className="grid md:grid-cols-3 gap-4">
            {(portfolio?.certificates || []).map((cert: any, i: number) => (
              <div key={i} className="bg-gradient-to-br from-gray-50 to-white dark:from-gray-900 dark:to-gray-800 rounded-xl p-5 border-2 dark:border-gray-700 hover:border-purple-500 transition">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-3xl">
                    {cert.type === 'tree_planting' && '🌳'}
                    {cert.type === 'soil_regeneration' && '🌱'}
                    {cert.type === 'agroforestry' && '🌾'}
                  </span>
                  <span className="text-xs font-mono text-gray-400">#{cert.id}</span>
                </div>
                <h3 className="font-bold mb-2 capitalize">{cert.type.replace(/_/g, ' ')}</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Carbon:</span>
                    <span className="font-bold text-green-600">{(cert.carbon_kg / 1000).toFixed(2)}t</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Health:</span>
                    <span className="font-bold">{(cert.health * 100).toFixed(0)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Stage:</span>
                    <span className="font-bold capitalize">{cert.stage}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
