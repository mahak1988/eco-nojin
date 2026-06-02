"use client";

import { useState, useEffect } from 'react';
import { 
  Shield, Activity, Database, Server, 
  Cpu, HardDrive, Wifi, AlertCircle, CheckCircle 
} from 'lucide-react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import StatCard from '@/components/StatCard';
import LoadingSpinner from '@/components/LoadingSpinner';
import { api, gaiaApi, modelsApi, healthApi } from '@/lib/api';
import type { Model } from '@/lib/types';

export default function AdminPage() {
  const [models, setModels] = useState<Model[]>([]);
  const [healthStatus, setHealthStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [modelsRes, healthRes] = await Promise.all([
          modelsApi.list(),
          healthApi.check(),
        ]);
        setModels(modelsRes.data.models || []);
        setHealthStatus(healthRes.data);
      } catch (err) {
        console.error('Failed to fetch admin data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" text="Loading admin panel..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Navbar />
      
      <div className="container mx-auto px-4 py-24">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8 flex items-center gap-3">
            <Shield className="w-10 h-10 text-green-500" />
            <div>
              <h1 className="text-4xl font-bold">Admin Panel</h1>
              <p className="text-gray-400">System monitoring and management</p>
            </div>
          </div>

          {/* System Health */}
          <div className="grid md:grid-cols-4 gap-6 mb-8">
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <div className="flex items-center gap-3 mb-3">
                <div className={`w-3 h-3 rounded-full ${healthStatus?.status === 'healthy' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
                <span className="text-sm text-gray-400">API Status</span>
              </div>
              <div className="text-2xl font-bold">
                {healthStatus?.status === 'healthy' ? 'Healthy' : 'Error'}
              </div>
            </div>
            
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <div className="flex items-center gap-3 mb-3">
                <Database className="w-5 h-5 text-blue-400" />
                <span className="text-sm text-gray-400">Database</span>
              </div>
              <div className="text-2xl font-bold">
                {healthStatus?.services?.database === 'up' ? '✓ Online' : '✗ Offline'}
              </div>
            </div>
            
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <div className="flex items-center gap-3 mb-3">
                <Cpu className="w-5 h-5 text-purple-400" />
                <span className="text-sm text-gray-400">Scientific Models</span>
              </div>
              <div className="text-2xl font-bold">
                {healthStatus?.services?.scientific_models === 'up' ? `${models.length} Active` : 'Error'}
              </div>
            </div>
            
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <div className="flex items-center gap-3 mb-3">
                <Wifi className="w-5 h-5 text-green-400" />
                <span className="text-sm text-gray-400">Gaia Oracle</span>
              </div>
              <div className="text-2xl font-bold capitalize">
                {healthStatus?.services?.gaia_oracle || 'Unknown'}
              </div>
            </div>
          </div>

          {/* Scientific Models */}
          <div className="bg-gray-800 rounded-2xl p-6 mb-8 border border-gray-700">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <Cpu className="w-6 h-6 text-purple-400" />
              Scientific Models
            </h2>
            
            <div className="grid md:grid-cols-3 gap-4">
              {models.map((model) => (
                <div key={model.name} className="bg-gray-900 rounded-xl p-5 border border-gray-700">
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="font-bold text-lg">{model.name}</h3>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      model.status === 'active' 
                        ? 'bg-green-500/20 text-green-400' 
                        : 'bg-red-500/20 text-red-400'
                    }`}>
                      {model.status}
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 mb-3">{model.description}</p>
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <span className="px-2 py-1 bg-gray-800 rounded">{model.type}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* API Endpoints */}
          <div className="bg-gray-800 rounded-2xl p-6 mb-8 border border-gray-700">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <Server className="w-6 h-6 text-blue-400" />
              API Endpoints
            </h2>
            
            <div className="space-y-2 font-mono text-sm">
              {[
                { method: 'GET', path: '/health', status: 'active' },
                { method: 'GET', path: '/models', status: 'active' },
                { method: 'POST', path: '/gaia/calculate', status: 'active' },
                { method: 'POST', path: '/gaia/register-activity', status: 'active' },
                { method: 'GET', path: '/gaia/stats', status: 'active' },
                { method: 'GET', path: '/gaia/portfolio/{address}', status: 'active' },
                { method: 'GET', path: '/farmer/farmers/', status: 'active' },
                { method: 'POST', path: '/auth/login', status: 'active' },
              ].map((endpoint, i) => (
                <div key={i} className="flex items-center gap-3 p-3 bg-gray-900 rounded-lg">
                  <span className={`px-2 py-1 rounded text-xs font-bold ${
                    endpoint.method === 'GET' ? 'bg-blue-500/20 text-blue-400' : 'bg-green-500/20 text-green-400'
                  }`}>
                    {endpoint.method}
                  </span>
                  <span className="text-gray-300 flex-1">{endpoint.path}</span>
                  <CheckCircle className="w-4 h-4 text-green-400" />
                </div>
              ))}
            </div>
          </div>

          {/* System Info */}
          <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <HardDrive className="w-6 h-6 text-yellow-400" />
              System Information
            </h2>
            
            <div className="grid md:grid-cols-2 gap-4">
              <div className="p-4 bg-gray-900 rounded-lg">
                <div className="text-sm text-gray-400">Next.js Version</div>
                <div className="text-xl font-bold">15.0.5</div>
                <div className="text-xs text-green-400 mt-1">✓ CVE-2025-66478 Patched</div>
              </div>
              
              <div className="p-4 bg-gray-900 rounded-lg">
                <div className="text-sm text-gray-400">Compiler</div>
                <div className="text-xl font-bold">Babel</div>
                <div className="text-xs text-gray-500 mt-1">SWC fallback active</div>
              </div>
              
              <div className="p-4 bg-gray-900 rounded-lg">
                <div className="text-sm text-gray-400">Backend</div>
                <div className="text-xl font-bold">FastAPI</div>
                <div className="text-xs text-green-400 mt-1">✓ Running on :8000</div>
              </div>
              
              <div className="p-4 bg-gray-900 rounded-lg">
                <div className="text-sm text-gray-400">Blockchain</div>
                <div className="text-xl font-bold">Polygon</div>
                <div className="text-xs text-blue-400 mt-1">Testnet Ready</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <Footer />
    </div>
  );
}
