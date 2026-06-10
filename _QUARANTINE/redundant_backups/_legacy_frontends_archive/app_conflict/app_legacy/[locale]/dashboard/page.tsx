'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { BarChart3, Activity, Users, Leaf, Award, TreePine, TrendingUp, Loader2 } from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';

const FALLBACK_STATS = {
  total_activities: 156,
  total_carbon_tons: 203.56,
  estimated_value_usd: 10177.92,
  by_activity: {
    tree_planting: { count: 85, carbon_kg: 154000 },
    soil_regeneration: { count: 32, carbon_kg: 28000 },
  },
};

export default function DashboardPage() {
  const params = useParams();
  const locale = (params?.locale as Locale) || 'fa';
  const dict = getDictionary(locale);
  const isRTL = ['fa', 'ar', 'ur'].includes(locale);

  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const fetchData = async () => {
      try {
        setLoading(true);
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000);

        const res = await fetch(`${apiUrl}/gaia/stats`, { signal: controller.signal });
        clearTimeout(timeoutId);

        if (!res.ok) throw new Error(`API error: ${res.status}`);
        
        const data = await res.json();
        if (isMounted) setStats(data);
      } catch (err: any) {
        // ✅ استفاده از console.warn به جای console.error
        console.warn('Dashboard: Using fallback data -', err?.message);
        if (isMounted) setStats(FALLBACK_STATS);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchData();
    return () => { isMounted = false; };
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center pt-20">
        <Loader2 className="w-12 h-12 text-green-600 animate-spin" />
      </div>
    );
  }

  const displayStats = stats || FALLBACK_STATS;

  return (
    <div className="min-h-screen bg-gray-50 pt-20">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold mb-8">{dict?.dashboard?.title || 'داشبورد'}</h1>
        
        <div className="grid md:grid-cols-4 gap-6">
          {[
            { icon: TreePine, value: displayStats?.total_activities || 0, label: 'Activities' },
            { icon: Leaf, value: `${displayStats?.total_carbon_tons || 0}t`, label: 'CO₂' },
            { icon: Award, value: '20K+', label: 'SEED' },
            { icon: TrendingUp, value: '$10K', label: 'Value' },
          ].map((stat, i) => {
            const Icon = stat.icon;
            return (
              <div key={i} className="bg-white rounded-xl p-6 shadow">
                <Icon className="w-8 h-8 text-green-500 mb-3" />
                <div className="text-3xl font-bold">{stat.value}</div>
                <div className="text-sm text-gray-500">{stat.label}</div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
