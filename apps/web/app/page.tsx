"use client";

import Link from 'next/link';
import { useState, useEffect } from 'react';
import { 
  Leaf, Calculator, Globe, Award, ArrowRight, 
  TreePine, Droplets, Shield, Zap, TrendingUp 
} from 'lucide-react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import StatCard from '@/components/StatCard';
import { gaiaApi } from '@/lib/api';
import type { PlatformStats } from '@/lib/types';

export default function HomePage() {
  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await gaiaApi.getStats();
        setStats(res.data);
      } catch (err) {
        console.error('Failed to fetch stats:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 via-white to-blue-50">
      <Navbar />
      
      {/* Hero Section */}
      <section className="pt-24 pb-20 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-green-100 text-green-800 px-4 py-2 rounded-full mb-6 animate-fade-in">
            <Shield className="w-4 h-4" />
            <span className="text-sm font-medium">CVE-2025-66478 Patched • Next.js 15.0.5</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 animate-slide-up">
            Turn Your <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-600 to-emerald-600">Ecological Impact</span>
            <br />Into Real Value
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Econojin combines cutting-edge science (RothC, AquaCrop, IPCC) with 
            satellite verification and blockchain technology to create 
            verifiable carbon credits and living NFTs.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              href="/calculate"
              className="inline-flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700 text-white px-8 py-4 rounded-lg text-lg font-semibold transition shadow-lg hover:shadow-xl"
            >
              <Calculator className="w-5 h-5" />
              Calculate Carbon
              <ArrowRight className="w-5 h-5" />
            </Link>
            
            <Link 
              href="/dashboard"
              className="inline-flex items-center justify-center gap-2 bg-white hover:bg-gray-50 text-gray-900 px-8 py-4 rounded-lg text-lg font-semibold border-2 border-gray-200 transition"
            >
              <TrendingUp className="w-5 h-5" />
              View Dashboard
            </Link>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto">
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading platform stats...</p>
            </div>
          ) : stats ? (
            <div className="grid md:grid-cols-4 gap-6">
              <StatCard
                title="Total Activities"
                value={stats.total_activities.toLocaleString()}
                icon={<TreePine className="w-6 h-6" />}
                color="green"
              />
              <StatCard
                title="CO₂ Absorbed"
                value={`${stats.total_carbon_tons.toFixed(1)} tons`}
                icon={<Droplets className="w-6 h-6" />}
                color="blue"
              />
              <StatCard
                title="Equivalent Trees"
                value={stats.equivalent_trees.toLocaleString()}
                icon={<Leaf className="w-6 h-6" />}
                color="purple"
              />
              <StatCard
                title="GAIA Value"
                value={`$${stats.estimated_value_usd.toLocaleString()}`}
                icon={<Award className="w-6 h-6" />}
                color="yellow"
              />
            </div>
          ) : (
            <div className="grid md:grid-cols-4 gap-6">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="bg-gray-200 rounded-xl h-32 animate-pulse" />
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-4 bg-white">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl font-bold text-center mb-12">Why Econojin?</h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: <Shield className="w-8 h-8" />,
                title: "Scientific Accuracy",
                description: "Based on RothC, AquaCrop, and IPCC 2019 models - the gold standard in carbon accounting.",
                color: "from-blue-500 to-cyan-600",
              },
              {
                icon: <Globe className="w-8 h-8" />,
                title: "Satellite Verification",
                description: "Every activity is verified using Sentinel-2 satellite imagery with NDVI analysis.",
                color: "from-green-500 to-emerald-600",
              },
              {
                icon: <Zap className="w-8 h-8" />,
                title: "Living NFTs",
                description: "Your certificate NFT grows as your real ecosystem grows - truly alive on the blockchain.",
                color: "from-purple-500 to-pink-600",
              },
            ].map((feature, i) => (
              <div 
                key={i} 
                className="bg-gradient-to-br from-gray-50 to-white rounded-xl p-8 shadow-sm hover:shadow-xl transition-all duration-300 border border-gray-100"
              >
                <div className={`w-16 h-16 rounded-lg bg-gradient-to-br ${feature.color} flex items-center justify-center text-white mb-6`}>
                  {feature.icon}
                </div>
                <h3 className="text-2xl font-bold mb-3">{feature.title}</h3>
                <p className="text-gray-600 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4 bg-gradient-to-br from-green-600 to-emerald-700 text-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-6">Ready to Make an Impact?</h2>
          <p className="text-xl mb-8 text-green-100">
            Join thousands of individuals and organizations turning ecological 
            activities into verifiable, valuable digital assets.
          </p>
          <Link
            href="/calculate"
            className="inline-flex items-center gap-2 bg-white text-green-700 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-100 transition shadow-xl"
          >
            Get Started Now
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      <Footer />
    </div>
  );
}
