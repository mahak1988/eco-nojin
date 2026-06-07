"use client";

// apps/web/src/app/admin/products/page.tsx
import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight, Plus, Search, Edit, Trash2, Package,
  DollarSign, TrendingUp, X, Save, Image as ImageIcon
} from "lucide-react";

const PRODUCTS = [
  {
    id: 1,
    name: "بذر گندم مقاوم به خشکی",
    category: "بذر و نهال",
    price: 450000,
    stock: 150,
    status: "active",
    image: "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400"
  },
  {
    id: 2,
    name: "سنسور رطوبت خاک TDR",
    category: "تجهیزات IoT",
    price: 2500000,
    stock: 45,
    status: "active",
    image: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"
  },
  {
    id: 3,
    name: "کود هیومیک اسید مایع",
    category: "کودهای ارگانیک",
    price: 850000,
    stock: 80,
    status: "active",
    image: "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=400"
  },
  {
    id: 4,
    name: "سیستم آبیاری قطره‌ای",
    category: "سیستم‌های آبیاری",
    price: 15000000,
    stock: 10,
    status: "low-stock",
    image: "https://images.unsplash.com/photo-1622383563227-04401ab4e5ea?w=400"
  },
];

export default function ProductsManagement() {
  const [searchQuery, setSearchQuery] = useState("");
  const [showEditor, setShowEditor] = useState(false);

  const filteredProducts = PRODUCTS.filter(p =>
    p.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen" style={{ backgroundColor: "#f5f1e8" }}>
      {/* Header */}
      <header className="bg-white border-b px-6 py-4" style={{ borderColor: "#e5dfd3" }}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/admin" className="p-2 rounded-lg hover:bg-gray-100">
              <ArrowRight className="h-5 w-5" style={{ color: "#6b5d4f" }} />
            </Link>
            <h1 className="text-2xl font-black" style={{ color: "#2c2416" }}>مدیریت محصولات</h1>
          </div>
          <button
            onClick={() => setShowEditor(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl font-bold text-white"
            style={{ backgroundColor: "#8b6f47" }}
          >
            <Plus className="h-5 w-5" />
            محصول جدید
          </button>
        </div>
      </header>

      {/* Content */}
      <div className="p-6">
        {/* Search */}
        <div className="bg-white rounded-2xl p-6 border mb-6" style={{ borderColor: "#e5dfd3" }}>
          <div className="relative">
            <Search className="absolute right-4 top-1/2 -translate-y-1/2 h-5 w-5" style={{ color: "#6b5d4f" }} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="جستجو در محصولات..."
              className="w-full pr-12 pl-4 py-3 rounded-xl border focus:outline-none focus:ring-2"
              style={{ borderColor: "#e5dfd3", color: "#2c2416" }}
            />
          </div>
        </div>

        {/* Products Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map((product, idx) => (
            <motion.div
              key={product.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              className="bg-white rounded-2xl overflow-hidden border hover:shadow-lg transition-shadow"
              style={{ borderColor: "#e5dfd3" }}
            >
              <img src={product.image} alt={product.name} className="w-full h-48 object-cover" />
              <div className="p-5">
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-2 py-1 rounded text-xs font-bold" style={{ backgroundColor: "#8b6f4720", color: "#8b6f47" }}>
                    {product.category}
                  </span>
                </div>
                <h3 className="font-black mb-3" style={{ color: "#2c2416" }}>{product.name}</h3>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="text-xs" style={{ color: "#6b5d4f" }}>قیمت</p>
                    <p className="font-black text-lg" style={{ color: "#2d5016" }}>
                      {product.price.toLocaleString()} تومان
                    </p>
                  </div>
                  <div>
                    <p className="text-xs" style={{ color: "#6b5d4f" }}>موجودی</p>
                    <p className={`font-black text-lg ${product.stock < 20 ? "text-red-600" : ""}`} style={product.stock >= 20 ? { color: "#2c2416" } : {}}>
                      {product.stock}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button onClick={() => console.log("Button clicked")}  className="flex-1 py-2 rounded-lg font-bold text-white text-sm" style={{ backgroundColor: "#8b6f47" }}>
                    <Edit className="h-4 w-4 inline ml-1" />
                    ویرایش
                  </button>
                  <button onClick={() => console.log("Button clicked")}  className="p-2 rounded-lg hover:bg-red-50">
                    <Trash2 className="h-4 w-4 text-red-600" />
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}