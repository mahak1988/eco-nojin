'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { Sparkles, BookOpen, TrendingUp, Download, Star } from 'lucide-react';
import { getRecommendations, getTrendingResources } from '@/lib/ai/recommendations';
import WishlistButton from './WishlistButton';
import type { Resource } from '@/lib/supabase/types';

interface RecommendedResourcesProps {
  resourceId?: string;
  category?: string;
  mode?: 'similar' | 'trending' | 'personalized';
  limit?: number;
}

export default function RecommendedResources({
  resourceId,
  category,
  mode = 'similar',
  limit = 6,
}: RecommendedResourcesProps) {
  const params = useParams();
  const locale = params?.locale || 'fa';
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadRecommendations() {
      setLoading(true);
      try {
        let data: Resource[];
        if (mode === 'trending') {
          data = await getTrendingResources(limit);
        } else if (resourceId) {
          data = await getRecommendations({ resourceId, category, limit });
        } else {
          data = await getTrendingResources(limit);
        }
        setResources(data);
      } catch (err) {
        console.error('Error loading recommendations:', err);
      } finally {
        setLoading(false);
      }
    }

    loadRecommendations();
  }, [resourceId, category, mode, limit]);

  if (loading) {
    return (
      <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-6">
        <div className="flex items-center gap-2 mb-6">
          <Sparkles className="w-6 h-6 text-purple-600" />
          <h2 className="text-2xl font-bold">
            {mode === 'similar' ? 'منابع مشابه' : 'منابع پرطرفدار'}
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: limit }).map((_, i) => (
            <div key={i} className="bg-white rounded-xl p-4 animate-pulse">
              <div className="h-32 bg-gray-200 rounded-lg mb-3"></div>
              <div className="h-4 bg-gray-200 rounded mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (resources.length === 0) {
    return null;
  }

  return (
    <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-6">
      <div className="flex items-center gap-2 mb-6">
        {mode === 'similar' ? (
          <Sparkles className="w-6 h-6 text-purple-600" />
        ) : (
          <TrendingUp className="w-6 h-6 text-pink-600" />
        )}
        <h2 className="text-2xl font-bold">
          {mode === 'similar' ? 'منابع مشابه پیشنهادی' : 'منابع پرطرفدار'}
        </h2>
        <span className="text-sm text-purple-600 bg-purple-100 px-2 py-1 rounded-full">
          AI Powered
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {resources.map((resource) => (
          <a
            key={resource.id}
            href={`/${locale}/library/${resource.id}`}
            className="bg-white rounded-xl shadow-md hover:shadow-xl transition overflow-hidden group"
          >
            <div className={`h-32 bg-gradient-to-br ${resource.cover_color} flex items-center justify-center relative`}>
              <BookOpen className="w-16 h-16 text-white/90 group-hover:scale-110 transition" />
              <div className="absolute top-2 right-2">
                <WishlistButton resourceId={resource.id} size="sm" />
              </div>
            </div>
            <div className="p-4">
              <h3 className="font-bold mb-1 line-clamp-2 group-hover:text-purple-600 transition">
                {resource.title}
              </h3>
              <p className="text-sm text-gray-500 mb-2">{resource.author}</p>
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span className="flex items-center gap-1">
                  <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                  {resource.rating.toFixed(1)}
                </span>
                <span className="flex items-center gap-1">
                  <Download className="w-3 h-3" />
                  {resource.download_count.toLocaleString()}
                </span>
              </div>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}