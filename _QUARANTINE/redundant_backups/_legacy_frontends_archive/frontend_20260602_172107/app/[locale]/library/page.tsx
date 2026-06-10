'use client';
import React from 'react';

import { useState, useMemo } from 'react';
import { useParams } from 'next/navigation';
import {
  Search, BookOpen, FileText, Video, Mic, Code,
  Filter, Grid, List, Star, Download, Eye,
  Upload, Tag, Calendar, User, ChevronDown, X, Sparkles
} from 'lucide-react';
import { useResources } from '@/lib/supabase/hooks';
import UploadModal from '@/components/UploadModal';
import WishlistButton from '@/components/WishlistButton';
import RecommendedResources from '@/components/RecommendedResources';
import StarRating from '@/components/StarRating';

const CATEGORIES = [
  { id: 'all', name: 'همه', icon: Grid },
  { id: 'environmental_science', name: 'علوم محیط زیست', icon: BookOpen },
  { id: 'blockchain', name: 'بلاکچین', icon: Code },
  { id: 'agriculture', name: 'کشاورزی', icon: BookOpen },
  { id: 'ai', name: 'هوش مصنوعی', icon: Sparkles },
  { id: 'economics', name: 'اقتصاد', icon: BookOpen },
  { id: 'energy', name: 'انرژی', icon: BookOpen },
];

const RESOURCE_TYPES = {
  book: { icon: BookOpen, label: 'کتاب', color: 'green' },
  article: { icon: FileText, label: 'مقاله', color: 'blue' },
  thesis: { icon: BookOpen, label: 'پایان‌نامه', color: 'yellow' },
  video: { icon: Video, label: 'ویدیو', color: 'purple' },
  podcast: { icon: Mic, label: 'پادکست', color: 'red' },
};

export default function LibraryPage() {
  const params = useParams();
  const locale = params?.locale || 'fa';
  const isRTL = ['fa', 'ar', 'ur'].includes(locale as string);

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedType, setSelectedType] = useState('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [showFilters, setShowFilters] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);

  const { resources, loading, error } = useResources({
    category: selectedCategory,
    type: selectedType,
    search: searchQuery,
  });

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 via-white to-blue-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 via-emerald-600 to-teal-600 text-white pt-24 pb-12 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <BookOpen className="w-12 h-12" />
              <div>
                <h1 className="text-4xl font-bold">کتابخانه دیجیتال</h1>
                <p className="text-green-100">منابع علمی با کیفیت بالا</p>
              </div>
            </div>
            <button
              onClick={() => setShowUploadModal(true)}
              className="flex items-center gap-2 px-6 py-3 bg-white text-green-600 rounded-xl font-bold hover:bg-green-50 transition shadow-lg"
            >
              <Upload className="w-5 h-5" />
              آپلود منبع
            </button>
          </div>

          {/* Search */}
          <div className="relative max-w-2xl">
            <Search className={`absolute ${isRTL ? 'right-4' : 'left-4'} top-1/2 -translate-y-1/2 w-6 h-6 text-gray-400`} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="جستجو در کتاب‌ها، مقالات، ویدیوها..."
              className={`w-full ${isRTL ? 'pr-14 pl-4' : 'pl-14 pr-4'} py-4 text-lg text-gray-900 bg-white rounded-xl shadow-lg focus:outline-none focus:ring-4 focus:ring-green-300`}
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className={`absolute ${isRTL ? 'left-4' : 'right-4'} top-1/2 -translate-y-1/2`}
              >
                <X className="w-5 h-5 text-gray-400" />
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
        {/* Categories */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold">دسته‌بندی‌ها</h2>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-4 py-2 bg-white rounded-lg shadow hover:shadow-md transition"
            >
              <Filter className="w-5 h-5" />
              فیلترها
              <ChevronDown className={`w-4 h-4 transition ${showFilters ? 'rotate-180' : ''}`} />
            </button>
          </div>

          <div className="flex flex-wrap gap-2">
            {CATEGORIES.map(cat => {
              const Icon = cat.icon;
              const isActive = selectedCategory === cat.id;
              return (
                <button
                  key={cat.id}
                  onClick={() => setSelectedCategory(cat.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition ${
                    isActive
                      ? 'bg-green-600 text-white shadow-lg'
                      : 'bg-white text-gray-700 hover:bg-gray-50 shadow'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {cat.name}
                </button>
              );
            })}
          </div>

          {showFilters && (
            <div className="mt-4 p-6 bg-white rounded-xl shadow-lg">
              <h3 className="font-bold mb-3">نوع منبع</h3>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setSelectedType('all')}
                  className={`px-3 py-1 rounded-lg ${
                    selectedType === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-100'
                  }`}
                >
                  همه
                </button>
                {Object.entries(RESOURCE_TYPES).map(([type, config]) => {
                  const Icon = config.icon;
                  return (
                    <button
                      key={type}
                      onClick={() => setSelectedType(type)}
                      className={`flex items-center gap-1 px-3 py-1 rounded-lg ${
                        selectedType === type ? 'bg-blue-600 text-white' : 'bg-gray-100'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      {config.label}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* View Toggle */}
        <div className="flex items-center justify-between">
          <p className="text-gray-600">
            {resources.length} منبع یافت شد
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-lg ${viewMode === 'grid' ? 'bg-green-600 text-white' : 'bg-white'}`}
            >
              <Grid className="w-5 h-5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-lg ${viewMode === 'list' ? 'bg-green-600 text-white' : 'bg-white'}`}
            >
              <List className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Resources */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="bg-white rounded-xl p-6 animate-pulse">
                <div className="h-48 bg-gray-200 rounded-lg mb-4"></div>
                <div className="h-4 bg-gray-200 rounded mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-2/3"></div>
              </div>
            ))}
          </div>
        ) : resources.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-2xl shadow">
            <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-xl text-gray-500">منبعی یافت نشد</p>
            <p className="text-gray-400 mt-2">فیلترهای خود را تغییر دهید</p>
          </div>
        ) : (
          <div className={viewMode === 'grid' 
            ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
            : 'space-y-4'
          }>
            {resources.map(resource => {
              const typeConfig = RESOURCE_TYPES[resource.resource_type as keyof typeof RESOURCE_TYPES];
              const TypeIcon = typeConfig?.icon || BookOpen;
              
              return (
                <a
                  key={resource.id}
                  href={`/${locale}/library/${resource.id}`}
                  className="bg-white rounded-xl shadow-md hover:shadow-xl transition overflow-hidden group"
                >
                  <div className={`h-48 bg-gradient-to-br ${resource.cover_color || 'from-green-400 to-emerald-600'} flex items-center justify-center relative`}>
                    <TypeIcon className="w-20 h-20 text-white/90 group-hover:scale-110 transition" />
                    <div className="absolute top-4 right-4">
                      <WishlistButton resourceId={resource.id} />
                    </div>
                    <div className="absolute top-4 left-4 flex items-center gap-1 px-2 py-1 bg-white/90 rounded-full text-sm font-medium">
                      <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                      {resource.rating.toFixed(1)}
                    </div>
                  </div>
                  <div className="p-6">
                    <h3 className="text-lg font-bold mb-2 line-clamp-2">{resource.title}</h3>
                    <p className="text-sm text-gray-500 mb-3 flex items-center gap-2">
                      <User className="w-4 h-4" />
                      {resource.author}
                    </p>
                    <p className="text-gray-600 text-sm mb-4 line-clamp-2">{resource.description}</p>
                    <div className="flex items-center justify-between text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <Download className="w-4 h-4" />
                        {resource.download_count.toLocaleString()}
                      </span>
                      <span className="flex items-center gap-1">
                        <Eye className="w-4 h-4" />
                        {resource.view_count.toLocaleString()}
                      </span>
                    </div>
                  </div>
                </a>
              );
            })}
          </div>
        )}

        {/* AI Recommendations */}
        <RecommendedResources mode="trending" limit={6} />
      </div>

      {/* Upload Modal */}
      <UploadModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
      />
    </div>
  );
}