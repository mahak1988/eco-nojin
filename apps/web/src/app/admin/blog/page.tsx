"use client";

﻿// apps/web/src/app/admin/blog/page.tsx
import { useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowRight, Plus, Search, Edit, Trash2, Eye, Calendar, Clock, User, Tag, X, Save, Image as ImageIcon, Heart, BookOpen
} from "lucide-react";

const ARTICLES = [
  {
    id: 1,
    title: "احیای ۵۰ هکتار زمین شور در دشت مغان",
    author: "دکتر محمد رضایی",
    category: "success-story",
    status: "published",
    views: 3420,
    likes: 245,
    published_at: "۱۴۰۳/۰۹/۱۵",
    image: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400"
  },
  {
    id: 2,
    title: "تکنیک‌های نوین آبیاری قطره‌ای زیرسطحی",
    author: "مهندس علی احمدی",
    category: "water-management",
    status: "published",
    views: 2890,
    likes: 189,
    published_at: "۱۴۰۳/۰۹/۱۰",
    image: "https://images.unsplash.com/photo-1622383563227-04401ab4e5ea?w=400"
  },
  {
    id: 3,
    title: "تأثیر تغییر اقلیم بر حوضه زاینده‌رود",
    author: "دکتر فاطمه کریمی",
    category: "climate",
    status: "draft",
    views: 0,
    likes: 0,
    published_at: null,
    image: "https://images.unsplash.com/photo-1569163139394-de4e4f43e4e3?w=400"
  },
  {
    id: 4,
    title: "کشاورزی حفاظتی: راهکاری برای حفظ خاک",
    author: "دکتر حسین نوری",
    category: "sustainable-agriculture",
    status: "published",
    views: 2340,
    likes: 156,
    published_at: "۱۴۰۳/۰۸/۲۸",
    image: "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=400"
  },
  {
    id: 5,
    title: "تجربه آبیاری هوشمند در بهبهان",
    author: "حاج رحیم آقایی",
    category: "farmer-experience",
    status: "published",
    views: 5670,
    likes: 423,
    published_at: "۱۴۰۳/۰۸/۲۰",
    image: "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400"
  },
];

const CATEGORIES = [
  { id: "sustainable-agriculture", name: "کشاورزی پایدار", color: "#2d5016" },
  { id: "water-management", name: "مدیریت آب", color: "#1e40af" },
  { id: "climate", name: "تغییر اقلیم", color: "#dc2626" },
  { id: "research", name: "تحقیقات علمی", color: "#7c3aed" },
  { id: "farmer-experience", name: "تجربیات کشاورزان", color: "#ea580c" },
  { id: "success-story", name: "داستان موفقیت", color: "#059669" },
];

export default function BlogManagement() {
  const [searchQuery, setSearchQuery] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");
  const [showEditor, setShowEditor] = useState(false);
  const [editingArticle, setEditingArticle] = useState<any>(null);

  const filteredArticles = ARTICLES.filter(article => {
    const matchSearch = article.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchStatus = filterStatus === "all" || article.status === filterStatus;
    return matchSearch && matchStatus;
  });

  const handleEdit = (article: any) => {
    setEditingArticle(article);
    setShowEditor(true);
  };

  const handleDelete = (id: number) => {
    if (confirm("آیا از حذف این مقاله مطمئن هستید؟")) {
      // حذف مقاله
    }
  };

  const handleNew = () => {
    setEditingArticle(null);
    setShowEditor(true);
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: "#f5f1e8" }}>
      {/* Header */}
      <header className="bg-white border-b px-6 py-4" style={{ borderColor: "#e5dfd3" }}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/admin" className="p-2 rounded-lg hover:bg-gray-100 transition-colors">
              <ArrowRight className="h-5 w-5" style={{ color: "#6b5d4f" }} />
            </Link>
            <h1 className="text-2xl font-black" style={{ color: "#2c2416" }}>مدیریت مقالات</h1>
          </div>
          <button
            onClick={handleNew}
            className="flex items-center gap-2 px-4 py-2 rounded-xl font-bold text-white hover:opacity-90 transition-opacity"
            style={{ backgroundColor: "#2d5016" }}
          >
            <Plus className="h-5 w-5" />
            مقاله جدید
          </button>
        </div>
      </header>

      {/* Content */}
      <div className="p-6">
        {/* Filters */}
        <div className="bg-white rounded-2xl p-6 border mb-6" style={{ borderColor: "#e5dfd3" }}>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute right-4 top-1/2 -translate-y-1/2 h-5 w-5" style={{ color: "#6b5d4f" }} />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="جستجو در مقالات..."
                className="w-full pr-12 pl-4 py-3 rounded-xl border focus:outline-none focus:ring-2"
                style={{ borderColor: "#e5dfd3", color: "#2c2416" }}
              />
            </div>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-3 rounded-xl border focus:outline-none focus:ring-2"
              style={{ borderColor: "#e5dfd3", color: "#2c2416" }}
            >
              <option value="all">همه وضعیت‌ها</option>
              <option value="published">منتشر شده</option>
              <option value="draft">پیش‌نویس</option>
            </select>
          </div>
        </div>

        {/* Articles Table */}
        <div className="bg-white rounded-2xl border overflow-hidden" style={{ borderColor: "#e5dfd3" }}>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead style={{ backgroundColor: "#f5f1e8" }}>
                <tr>
                  <th className="text-right px-6 py-4 font-bold text-sm" style={{ color: "#6b5d4f" }}>عنوان</th>
                  <th className="text-right px-6 py-4 font-bold text-sm" style={{ color: "#6b5d4f" }}>نویسنده</th>
                  <th className="text-right px-6 py-4 font-bold text-sm" style={{ color: "#6b5d4f" }}>دسته‌بندی</th>
                  <th className="text-right px-6 py-4 font-bold text-sm" style={{ color: "#6b5d4f" }}>وضعیت</th>
                  <th className="text-right px-6 py-4 font-bold text-sm" style={{ color: "#6b5d4f" }}>آمار</th>
                  <th className="text-right px-6 py-4 font-bold text-sm" style={{ color: "#6b5d4f" }}>تاریخ</th>
                  <th className="text-right px-6 py-4 font-bold text-sm" style={{ color: "#6b5d4f" }}>عملیات</th>
                </tr>
              </thead>
              <tbody>
                {filteredArticles.map((article, idx) => {
                  const category = CATEGORIES.find(c => c.id === article.category);
                  return (
                    <motion.tr
                      key={article.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      className="border-t hover:bg-gray-50 transition-colors"
                      style={{ borderColor: "#e5dfd3" }}
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <img
                            src={article.image}
                            alt={article.title}
                            className="w-16 h-16 rounded-lg object-cover"
                          />
                          <div>
                            <h3 className="font-bold text-sm mb-1 line-clamp-2" style={{ color: "#2c2416" }}>
                              {article.title}
                            </h3>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <User className="h-4 w-4" style={{ color: "#6b5d4f" }} />
                          <span className="text-sm" style={{ color: "#6b5d4f" }}>{article.author}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        {category && (
                          <span
                            className="px-3 py-1 rounded-full text-xs font-bold"
                            style={{ backgroundColor: category.color + "20", color: category.color }}
                          >
                            {category.name}
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-bold ${
                            article.status === "published"
                              ? "bg-green-100 text-green-700"
                              : "bg-yellow-100 text-yellow-700"
                          }`}
                        >
                          {article.status === "published" ? "منتشر شده" : "پیش‌نویس"}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3 text-xs" style={{ color: "#6b5d4f" }}>
                          <span className="flex items-center gap-1">
                            <Eye className="h-3 w-3" />
                            {article.views.toLocaleString()}
                          </span>
                          <span className="flex items-center gap-1">
                            <Heart className="h-3 w-3" />
                            {article.likes}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-sm" style={{ color: "#6b5d4f" }}>
                          {article.published_at || "—"}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleEdit(article)}
                            className="p-2 rounded-lg hover:bg-blue-50 transition-colors"
                            title="ویرایش"
                          >
                            <Edit className="h-4 w-4 text-blue-600" />
                          </button>
                          <button
                            onClick={() => handleDelete(article.id)}
                            className="p-2 rounded-lg hover:bg-red-50 transition-colors"
                            title="حذف"
                          >
                            <Trash2 className="h-4 w-4 text-red-600" />
                          </button>
                        </div>
                      </td>
                    </motion.tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {filteredArticles.length === 0 && (
            <div className="text-center py-12">
              <BookOpen className="h-16 w-16 mx-auto mb-4" style={{ color: "#6b5d4f" }} />
              <p className="text-lg" style={{ color: "#6b5d4f" }}>مقاله‌ای یافت نشد</p>
            </div>
          )}
        </div>
      </div>

      {/* Editor Modal */}
      <AnimatePresence>
        {showEditor && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowEditor(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between" style={{ borderColor: "#e5dfd3" }}>
                <h2 className="text-xl font-black" style={{ color: "#2c2416" }}>
                  {editingArticle ? "ویرایش مقاله" : "مقاله جدید"}
                </h2>
                <button onClick={() => setShowEditor(false)} className="p-2 rounded-lg hover:bg-gray-100">
                  <X className="h-5 w-5" style={{ color: "#6b5d4f" }} />
                </button>
              </div>

              <div className="p-6 space-y-6">
                <div>
                  <label className="block text-sm font-bold mb-2" style={{ color: "#2c2416" }}>عنوان مقاله</label>
                  <input
                    type="text"
                    defaultValue={editingArticle?.title || ""}
                    placeholder="عنوان مقاله را وارد کنید"
                    className="w-full px-4 py-3 rounded-xl border focus:outline-none focus:ring-2"
                    style={{ borderColor: "#e5dfd3", color: "#2c2416" }}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-bold mb-2" style={{ color: "#2c2416" }}>نویسنده</label>
                    <input
                      type="text"
                      defaultValue={editingArticle?.author || ""}
                      placeholder="نام نویسنده"
                      className="w-full px-4 py-3 rounded-xl border focus:outline-none focus:ring-2"
                      style={{ borderColor: "#e5dfd3", color: "#2c2416" }}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-bold mb-2" style={{ color: "#2c2416" }}>دسته‌بندی</label>
                    <select
                      defaultValue={editingArticle?.category || ""}
                      className="w-full px-4 py-3 rounded-xl border focus:outline-none focus:ring-2"
                      style={{ borderColor: "#e5dfd3", color: "#2c2416" }}
                    >
                      {CATEGORIES.map(cat => (
                        <option key={cat.id} value={cat.id}>{cat.name}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-bold mb-2" style={{ color: "#2c2416" }}>تصویر شاخص</label>
                  <div className="border-2 border-dashed rounded-xl p-8 text-center" style={{ borderColor: "#e5dfd3" }}>
                    <ImageIcon className="h-12 w-12 mx-auto mb-2" style={{ color: "#6b5d4f" }} />
                    <p className="text-sm" style={{ color: "#6b5d4f" }}>برای آپلود تصویر کلیک کنید</p>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-bold mb-2" style={{ color: "#2c2416" }}>خلاصه مقاله</label>
                  <textarea
                    rows={3}
                    defaultValue={editingArticle?.excerpt || ""}
                    placeholder="خلاصه کوتاه مقاله"
                    className="w-full px-4 py-3 rounded-xl border focus:outline-none focus:ring-2 resize-none"
                    style={{ borderColor: "#e5dfd3", color: "#2c2416" }}
                  />
                </div>

                <div>
                  <label className="block text-sm font-bold mb-2" style={{ color: "#2c2416" }}>محتوای مقاله</label>
                  <textarea
                    rows={10}
                    defaultValue={editingArticle?.content || ""}
                    placeholder="محتوای کامل مقاله را اینجا بنویسید..."
                    className="w-full px-4 py-3 rounded-xl border focus:outline-none focus:ring-2 resize-none"
                    style={{ borderColor: "#e5dfd3", color: "#2c2416" }}
                  />
                </div>

                <div>
                  <label className="block text-sm font-bold mb-2" style={{ color: "#2c2416" }}>برچسب‌ها</label>
                  <input
                    type="text"
                    placeholder="برچسب‌ها را با کاما جدا کنید"
                    className="w-full px-4 py-3 rounded-xl border focus:outline-none focus:ring-2"
                    style={{ borderColor: "#e5dfd3", color: "#2c2416" }}
                  />
                </div>

                <div className="flex items-center gap-4 pt-4 border-t" style={{ borderColor: "#e5dfd3" }}>
                  <button
                    onClick={() => setShowEditor(false)}
                    className="flex-1 py-3 rounded-xl font-bold border hover:bg-gray-50 transition-colors"
                    style={{ borderColor: "#e5dfd3", color: "#6b5d4f" }}
                  >
                    انصراف
                  </button>
                  <button onClick={() =>
} 
                    className="flex-1 py-3 rounded-xl font-bold text-white hover:opacity-90 transition-opacity"
                    style={{ backgroundColor: "#8b6f47" }}
                  >
                    ذخیره پیش‌نویس
                  </button>
                  <button onClick={() =>
} 
                    className="flex-1 py-3 rounded-xl font-bold text-white hover:opacity-90 transition-opacity"
                    style={{ backgroundColor: "#2d5016" }}
                  >
                    <Save className="h-5 w-5 inline ml-2" />
                    انتشار
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}