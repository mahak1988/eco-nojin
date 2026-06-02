"use client";

import { useState, useEffect } from 'react';
import { 
  Leaf, TreePine, TrendingUp, Award, Activity, 
  Calendar, BarChart3, Users, Zap 
} from 'lucide-react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import StatCard from '@/components/StatCard';
import LoadingSpinner from '@/components/LoadingSpinner';
import { gaiaApi, farmerApi } from '@/lib/api';
import { formatNumber, formatUSD, formatDate } from '@/lib/utils';
import type { PlatformStats, Farmer } from '@/lib/types';

export default function DashboardPage() {
  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [farmers, setFarmers] = useState<Farmer[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'activities' | 'farmers'>('overview');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, farmersRes] = await Promise.all([
          gaiaApi.getStats(),
          farmerApi.list(0, 10),
        ]);
        setStats(statsRes.data);
        setFarmers(farmersRes.data.farmers || []);
      } catch (err) {
        console.error('Failed to fetch data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" text="Loading dashboard..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="container mx-auto px-4 py-24">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-4xl font-bold mb-2">Dashboard</h1>
            <p className="text-gray-600">Monitor your ecological impact in real-time</p>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-8 border-b">
            {[
              { id: 'overview', label: 'Overview', icon: BarChart3 },
              { id: 'activities', label: 'Activities', icon: Activity },
              { id: 'farmers', label: 'Farmers', icon: Users },
            ].map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center gap-2 px-6 py-3 font-medium transition border-b-2 ${
                    activeTab === tab.id
                      ? 'text-green-600 border-green-600'
                      : 'text-gray-500 border-transparent hover:text-gray-700'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {activeTab === 'overview' && stats && (
            <>
              {/* Stats Grid */}
              <div className="grid md:grid-cols-4 gap-6 mb-8">
                <StatCard
                  title="Total Activities"
                  value={stats.total_activities.toLocaleString()}
                  icon={<TreePine className="w-6 h-6" />}
                  color="green"
                  trend={{ value: 12, isPositive: true }}
                />
                <StatCard
                  title="CO₂ Absorbed"
                  value={`${stats.total_carbon_tons.toFixed(1)}t`}
                  subtitle={formatNumber(stats.total_carbon_kg) + ' kg'}
                  icon={<Leaf className="w-6 h-6" />}
                  color="blue"
                  trend={{ value: 8, isPositive: true }}
                />
                <StatCard
                  title="Trees Equivalent"
                  value={stats.equivalent_trees.toLocaleString()}
                  icon={<TreePine className="w-6 h-6" />}
                  color="purple"
                />
                <StatCard
                  title="Total Value"
                  value={formatUSD(stats.estimated_value_usd)}
                  icon={<Award className="w-6 h-6" />}
                  color="yellow"
                  trend={{ value: 15, isPositive: true }}
                />
              </div>

              {/* Activity Breakdown */}
              <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
                <h2 className="text-2xl font-bold mb-6">Activities Breakdown</h2>
                <div className="space-y-4">
                  {Object.entries(stats.by_activity || {}).map(([type, data]) => {
                    const total = stats.total_carbon_kg;
                    const percentage = (data.carbon_kg / total) * 100;
                    return (
                      <div key={type}>
                        <div className="flex justify-between mb-2">
                          <span className="font-medium capitalize">{type.replace(/_/g, ' ')}</span>
                          <span className="text-gray-600">
                            {data.count} activities • {formatNumber(data.carbon_kg)} kg
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                          <div
                            className="bg-gradient-to-r from-green-500 to-emerald-600 h-3 rounded-full transition-all duration-500"
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Recent Info */}
              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-white rounded-2xl shadow-lg p-6">
                  <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                    <Calendar className="w-5 h-5" />
                    Last Updated
                  </h3>
                  <p className="text-3xl font-bold text-green-600">
                    {formatDate(stats.timestamp)}
                  </p>
                  <p className="text-gray-500 mt-2">
                    Platform statistics refreshed
                  </p>
                </div>

                <div className="bg-white rounded-2xl shadow-lg p-6">
                  <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                    <Zap className="w-5 h-5" />
                    Quick Actions
                  </h3>
                  <div className="space-y-2">
                    <a href="/calculate" className="block p-3 bg-green-50 hover:bg-green-100 rounded-lg transition">
                      🧮 Calculate New Activity
                    </a>
                    <a href="/map" className="block p-3 bg-blue-50 hover:bg-blue-100 rounded-lg transition">
                      🗺️ View Global Map
                    </a>
                    <a href="/admin" className="block p-3 bg-purple-50 hover:bg-purple-100 rounded-lg transition">
                      ⚙️ Admin Panel
                    </a>
                  </div>
                </div>
              </div>
            </>
          )}

          {activeTab === 'farmers' && (
            <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
              <div className="p-6 border-b">
                <h2 className="text-2xl font-bold">Registered Farmers</h2>
                <p className="text-gray-600 mt-1">{farmers.length} farmers in the system</p>
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Farm Size</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Contact</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Joined</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {farmers.map((farmer) => (
                      <tr key={farmer.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-emerald-600 rounded-full flex items-center justify-center text-white font-bold">
                              {farmer.name.charAt(0)}
                            </div>
                            <div className="ml-4">
                              <div className="font-medium text-gray-900">{farmer.name}</div>
                              <div className="text-sm text-gray-500">ID: {farmer.id}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {farmer.farm_location || '—'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {farmer.farm_size_hectares ? `${farmer.farm_size_hectares} ha` : '—'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          <div>{farmer.email || '—'}</div>
                          <div className="text-xs text-gray-400">{farmer.phone}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {formatDate(farmer.created_at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'activities' && stats && (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {Object.entries(stats.by_activity || {}).map(([type, data]) => (
                <div key={type} className="bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-bold capitalize">{type.replace(/_/g, ' ')}</h3>
                    <span className="text-3xl">
                      {type === 'tree_planting' && '🌳'}
                      {type === 'soil_regeneration' && '🌱'}
                      {type === 'agroforestry' && '🌾'}
                      {type === 'mangrove_planting' && '🌊'}
                      {type === 'wetland_restoration' && '💧'}
                    </span>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Activities:</span>
                      <span className="font-bold text-lg">{data.count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Carbon:</span>
                      <span className="font-bold text-lg text-green-600">
                        {formatNumber(data.carbon_kg)} kg
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">CO₂ tons:</span>
                      <span className="font-bold text-lg">{formatNumber(data.carbon_kg / 1000)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      
      <Footer />
    </div>
  );
}
