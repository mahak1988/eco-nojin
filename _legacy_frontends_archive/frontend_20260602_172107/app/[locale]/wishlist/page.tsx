'use client';
import React from 'react';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { Heart, BookOpen, Trash2 } from 'lucide-react';
import { getSupabaseClient } from '@/lib/supabase/client';
import { useWishlist } from '@/lib/supabase/hooks';
import WishlistButton from '@/components/WishlistButton';
import type { Resource } from '@/lib/supabase/types';

export default function WishlistPage() {
  const params = useParams();
  const locale = params?.locale || 'fa';
  const { wishlistIds, loading: wishlistLoading } = useWishlist();
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchWishlistResources() {
      if (wishlistIds.length === 0) {
        setResources([]);
        setLoading(false);
        return;
      }

      try {
        const supabase = getSupabaseClient();
        const { data, error } = await supabase
          .from('resources')
          .select('*')
          .in('id', wishlistIds);

        if (error) throw error;
        setResources(data || []);
      } catch (err) {
        console.error('Error fetching wishlist resources:', err);
      } finally {
        setLoading(false);
      }
    }

    if (!wishlistLoading) {
      fetchWishlistResources();
    }
  }, [wishlistIds, wishlistLoading]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-red-50 to-white pt-24">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Heart className="w-10 h-10 text-red-500 fill-red-500" />
            <h1 className="text-4xl font-bold">لیست علاقه‌مندی‌ها</h1>
          </div>
          <p className="text-gray-600">
            {resources.length} منبع در لیست علاقه‌مندی‌های شما
          </p>
        </div>

        {/* Content */}
        {loading || wishlistLoading ? (
          <div className="text-center py-16">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-500 mx-auto"></div>
          </div>
        ) : resources.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-2xl shadow">
            <Heart className="w-20 h-20 text-gray-300 mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-2">لیست علاقه‌مندی‌ها خالی است</h2>
            <p className="text-gray-500 mb-6">
              با کلیک روی آیکون قلب، منابع مورد علاقه خود را ذخیره کنید
            </p>
            <a
              href={`/${locale}/library`}
              className="inline-flex items-center gap-2 px-6 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 transition"
            >
              <BookOpen className="w-5 h-5" />
              مشاهده کتابخانه
            </a>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {resources.map((resource) => (
              <div key={resource.id} className="bg-white rounded-xl shadow-md hover:shadow-xl transition overflow-hidden">
                <div className={`h-48 bg-gradient-to-br ${resource.cover_color} flex items-center justify-center relative`}>
                  <BookOpen className="w-20 h-20 text-white/90" />
                  <div className="absolute top-4 right-4">
                    <WishlistButton resourceId={resource.id} />
                  </div>
                </div>
                <div className="p-6">
                  <h3 className="text-lg font-bold mb-2 line-clamp-2">{resource.title}</h3>
                  <p className="text-sm text-gray-500 mb-3">{resource.author}</p>
                  <p className="text-gray-600 text-sm mb-4 line-clamp-2">{resource.description}</p>
                  <a
                    href={`/${locale}/library/${resource.id}`}
                    className="block w-full py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition text-center"
                  >
                    مشاهده جزئیات
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}