'use client';
import React from 'react';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { ShoppingCart, Search, Star, Heart } from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';

const PRODUCTS = [
  { id: 1, name: { fa: 'بذر بلوط ایرانی', en: 'Persian Oak Seeds' }, price: 250000, rating: 4.8, image: '🌳', cat: 'seeds' },
  { id: 2, name: { fa: 'کمپوست ارگانیک', en: 'Organic Compost' }, price: 180000, rating: 4.6, image: '🌱', cat: 'soil' },
  { id: 3, name: { fa: 'ابزار باغبانی', en: 'Gardening Tools' }, price: 850000, rating: 4.9, image: '🛠️', cat: 'tools' },
  { id: 4, name: { fa: 'سنسور IoT خاک', en: 'Soil IoT Sensor' }, price: 2500000, rating: 4.7, image: '📡', cat: 'tech' },
  { id: 5, name: { fa: 'کتاب کشاورزی پایدار', en: 'Sustainable Farming Book' }, price: 320000, rating: 4.9, image: '📚', cat: 'books' },
  { id: 6, name: { fa: 'نهال پسته وحشی', en: 'Wild Pistachio Sapling' }, price: 450000, rating: 4.5, image: '🌿', cat: 'seeds' },
];

export default function ShopPage() {
  const params = useParams();
  const locale = (params.locale as Locale) || 'fa';
  const dict = getDictionary(locale);
  const isPersian = locale === 'fa' || locale === 'ar' || locale === 'ur';
  const [cart, setCart] = useState<any[]>([]);
  const [search, setSearch] = useState('');

  const filtered = PRODUCTS.filter(p => p.name[isPersian ? 'fa' : 'en'].toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-white dark:from-gray-900 dark:to-gray-800 pt-20">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold flex items-center gap-3">
              <ShoppingCart className="w-10 h-10 text-orange-600" />
              {dict?.shop?.title || (isPersian ? 'فروشگاه اکونوژین' : 'Econojin Shop')}
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">{dict?.shop?.subtitle || (isPersian ? 'محصولات پایدار' : 'Sustainable products')}</p>
          </div>
          <div className="relative">
            <ShoppingCart className="w-6 h-6" />
            {cart.length > 0 && (
              <span className="absolute -top-2 -right-2 w-6 h-6 bg-orange-600 text-white text-xs rounded-full flex items-center justify-center">
                {cart.length}
              </span>
            )}
          </div>
        </div>

        <div className="relative mb-6">
          <Search className="absolute start-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder={dict?.common?.search || 'Search'}
            className="w-full ps-10 pe-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg focus:border-orange-500 focus:outline-none" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map(product => (
            <div key={product.id} className="bg-white dark:bg-gray-800 rounded-2xl shadow-md hover:shadow-xl transition overflow-hidden group">
              <div className="h-48 bg-gradient-to-br from-orange-100 to-yellow-100 dark:from-gray-700 dark:to-gray-600 flex items-center justify-center text-8xl relative">
                {product.image}
                <button className="absolute top-4 end-4 p-2 bg-white/80 dark:bg-gray-800/80 rounded-full hover:bg-white transition">
                  <Heart className="w-5 h-5 text-gray-600" />
                </button>
              </div>
              <div className="p-6">
                <h3 className="text-xl font-bold mb-2">{product.name[isPersian ? 'fa' : 'en']}</h3>
                <div className="flex items-center gap-1 mb-3">
                  <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                  <span className="text-sm font-medium">{product.rating}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-orange-600">
                    {product.price.toLocaleString()} {isPersian ? 'تومان' : 'IRR'}
                  </span>
                  <button onClick={() => setCart([...cart, product])}
                    className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition flex items-center gap-2">
                    <ShoppingCart className="w-4 h-4" />
                    {dict?.shop?.addToCart || (isPersian ? 'افزودن' : 'Add')}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
