"use client";

import { useState } from "react";
import { ShoppingCart, Search, Filter, Star, Heart, Leaf, Droplets, Sprout } from "lucide-react";

const PRODUCTS = [
  { id: 1, name: "بذر گندم پایدار", price: "۴۵۰,۰۰۰", category: "بذر", rating: 4.8, icon: Sprout, color: "from-lime-500 to-green-500" },
  { id: 2, name: "کود آلی طبیعی", price: "۲۸۰,۰۰۰", category: "کود", rating: 4.9, icon: Leaf, color: "from-emerald-500 to-green-600" },
  { id: 3, name: "سیستم آبیاری قطره‌ای", price: "۲,۵۰۰,۰۰۰", category: "تجهیزات", rating: 4.7, icon: Droplets, color: "from-blue-500 to-cyan-500" },
  { id: 4, name: "بذر جو مقاوم به خشکی", price: "۳۸۰,۰۰۰", category: "بذر", rating: 4.6, icon: Sprout, color: "from-amber-500 to-orange-500" },
  { id: 5, name: "کمپوست حرفه‌ای", price: "۱۵۰,۰۰۰", category: "کود", rating: 4.8, icon: Leaf, color: "from-green-500 to-emerald-500" },
  { id: 6, name: "سنسور رطوبت خاک", price: "۱,۲۰۰,۰۰۰", category: "تجهیزات", rating: 4.9, icon: Droplets, color: "from-sky-500 to-blue-500" },
  { id: 7, name: "بذر ذرت هیبریدی", price: "۵۲۰,۰۰۰", category: "بذر", rating: 4.5, icon: Sprout, color: "from-yellow-500 to-amber-500" },
  { id: 8, name: "پمپ آب خورشیدی", price: "۸,۵۰۰,۰۰۰", category: "تجهیزات", rating: 4.9, icon: Droplets, color: "from-orange-500 to-red-500" },
];

const CATEGORIES = ["همه", "بذر", "کود", "تجهیزات"];

export default function ShopPage() {
  const [category, setCategory] = useState("همه");
  const [search, setSearch] = useState("");

  const filtered = PRODUCTS.filter(p =>
    (category === "همه" || p.category === category) &&
    p.name.includes(search)
  );

  return (
    <div className="container mx-auto px-6 py-12">
      {/* Header */}
      <div className="mb-10">
        <h1 className="text-4xl font-bold text-white mb-3">فروشگاه اکو نوژین</h1>
        <p className="text-lg text-slate-400">محصولات پایدار برای کشاورزی مدرن</p>
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-8">
        <div className="relative flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="جستجوی محصول..." className="w-full pr-10 pl-4 py-3 bg-slate-900/50 border border-slate-800 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500" />
        </div>
        <div className="flex gap-2">
          {CATEGORIES.map(c => (
            <button key={c} onClick={() => setCategory(c)} className={`px-5 py-3 rounded-xl transition-all ${category === c ? "bg-emerald-600 text-white" : "bg-slate-900/50 text-slate-400 hover:bg-slate-800"}`}>
              {c}
            </button>
          ))}
        </div>
      </div>

      {/* Products Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
        {filtered.map(product => (
          <div key={product.id} className="group bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden hover:border-slate-700 transition-all">
            <div className={`relative h-48 bg-gradient-to-br ${product.color} flex items-center justify-center`}>
              <product.icon className="h-20 w-20 text-white/80" />
              <button onClick={() => console.log("Button clicked")}  className="absolute top-3 left-3 p-2 bg-white/20 backdrop-blur rounded-full hover:bg-white/30">
                <Heart className="h-4 w-4 text-white" />
              </button>
              <span className="absolute top-3 right-3 px-2 py-1 bg-black/30 backdrop-blur rounded text-xs text-white">{product.category}</span>
            </div>
            <div className="p-5">
              <h3 className="font-bold text-white mb-2 group-hover:text-emerald-300 transition-colors">{product.name}</h3>
              <div className="flex items-center gap-1 mb-3">
                <Star className="h-4 w-4 fill-amber-400 text-amber-400" />
                <span className="text-sm text-slate-300">{product.rating}</span>
              </div>
              <div className="flex items-center justify-between">
                <p className="text-lg font-bold text-emerald-400">{product.price} <span className="text-xs text-slate-500">تومان</span></p>
                <button onClick={() => console.log("Button clicked")}  className="p-2 bg-emerald-600 hover:bg-emerald-700 rounded-lg transition-colors">
                  <ShoppingCart className="h-4 w-4 text-white" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}