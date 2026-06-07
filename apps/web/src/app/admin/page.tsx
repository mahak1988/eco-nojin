"use client";

// apps/web/src/app/admin/page.tsx
import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  LayoutDashboard, BookOpen, Package, ShoppingCart, Users,
  TrendingUp, DollarSign, Eye, Heart, MessageSquare,
  Calendar, Bell, Settings, LogOut, Menu, X, Search
} from "lucide-react";

const stats = [
  { label: "کل مقالات", value: "۱۲۴", change: "+۱۲%", icon: BookOpen, color: "#2d5016" },
  { label: "کل محصولات", value: "۸۹", change: "+۸%", icon: Package, color: "#8b6f47" },
  { label: "سفارشات امروز", value: "۳۴", change: "+۲۳%", icon: ShoppingCart, color: "#1e40af" },
  { label: "کاربران جدید", value: "۱۵۶", change: "+۱۸%", icon: Users, color: "#7c3aed" },
  { label: "درآمد ماهانه", value: "۴۵.۲M", change: "+۱۵%", icon: DollarSign, color: "#059669" },
  { label: "بازدید امروز", value: "۲,۳۴۵", change: "+۳۲%", icon: Eye, color: "#ea580c" },
];

const recentActivities = [
  { type: "order", title: "سفارش جدید #۱۲۳۴", time: "۵ دقیقه پیش", icon: ShoppingCart },
  { type: "user", title: "کاربر جدید ثبت‌نام کرد", time: "۱۲ دقیقه پیش", icon: Users },
  { type: "article", title: "مقاله جدید منتشر شد", time: "۱ ساعت پیش", icon: BookOpen },
  { type: "comment", title: "نظر جدید روی مقاله", time: "۲ ساعت پیش", icon: MessageSquare },
  { type: "product", title: "محصول جدید اضافه شد", time: "۳ ساعت پیش", icon: Package },
];

const topArticles = [
  { title: "احیای زمین شور در مغان", views: 3420, likes: 245 },
  { title: "آبیاری قطره‌ای زیرسطحی", views: 2890, likes: 189 },
  { title: "تغییر اقلیم و زاینده‌رود", views: 4120, likes: 312 },
  { title: "کشاورزی حفاظتی", views: 2340, likes: 156 },
  { title: "تجربه آبیاری هوشمند", views: 5670, likes: 423 },
];

export default function AdminDashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const menuItems = [
    { label: "داشبورد", icon: LayoutDashboard, href: "/admin", active: true },
    { label: "مقالات", icon: BookOpen, href: "/admin/blog", active: false },
    { label: "محصولات", icon: Package, href: "/admin/products", active: false },
    { label: "سفارشات", icon: ShoppingCart, href: "/admin/orders", active: false },
    { label: "کاربران", icon: Users, href: "/admin/users", active: false },
  ];

  return (
    <div className="min-h-screen flex" style={{ backgroundColor: "#f5f1e8" }}>
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? "w-64" : "w-20"
        } transition-all duration-300 border-l flex flex-col`}
        style={{ backgroundColor: "#2c2416", borderColor: "#3d3226" }}
      >
        {/* Logo */}
        <div className="p-6 border-b" style={{ borderColor: "#3d3226" }}>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center text-white font-black" style={{ backgroundColor: "#2d5016" }}>
              E
            </div>
            {sidebarOpen && (
              <div>
                <h2 className="text-white font-black">اکو نوژین</h2>
                <p className="text-xs" style={{ color: "#a89882" }}>پنل مدیریت</p>
              </div>
            )}
          </div>
        </div>

        {/* Menu */}
        <nav className="flex-1 p-4 space-y-2">
          {menuItems.map((item, idx) => {
            const Icon = item.icon;
            return (
              <Link
                key={idx}
                href={item.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                  item.active ? "text-white" : "hover:bg-white/10"
                }`}
                style={{
                  backgroundColor: item.active ? "#2d5016" : "transparent",
                  color: item.active ? "white" : "#a89882"
                }}
              >
                <Icon className="h-5 w-5 flex-shrink-0" />
                {sidebarOpen && <span className="font-bold">{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        {/* User */}
        <div className="p-4 border-t" style={{ borderColor: "#3d3226" }}>
          <div className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/10 transition-all cursor-pointer">
            <div className="w-10 h-10 rounded-full flex items-center justify-center text-white font-black" style={{ backgroundColor: "#8b6f47" }}>
              م
            </div>
            {sidebarOpen && (
              <div className="flex-1">
                <p className="text-white font-bold text-sm">مدیر سایت</p>
                <p className="text-xs" style={{ color: "#a89882" }}>admin@econojin.com</p>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b px-6 py-4 flex items-center justify-between" style={{ borderColor: "#e5dfd3" }}>
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <Menu className="h-5 w-5" style={{ color: "#2c2416" }} />
            </button>
            <h1 className="text-2xl font-black" style={{ color: "#2c2416" }}>داشبورد</h1>
          </div>

          <div className="flex items-center gap-4">
            <button onClick={() => console.log("Button clicked")}  className="p-2 rounded-lg hover:bg-gray-100 transition-colors relative">
              <Bell className="h-5 w-5" style={{ color: "#6b5d4f" }} />
              <span className="absolute top-1 right-1 w-2 h-2 rounded-full" style={{ backgroundColor: "#dc2626" }} />
            </button>
            <button onClick={() => console.log("Button clicked")}  className="p-2 rounded-lg hover:bg-gray-100 transition-colors">
              <Settings className="h-5 w-5" style={{ color: "#6b5d4f" }} />
            </button>
          </div>
        </header>

        {/* Content */}
        <div className="flex-1 p-6 overflow-y-auto">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {stats.map((stat, idx) => {
              const Icon = stat.icon;
              return (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="bg-white rounded-2xl p-6 border hover:shadow-lg transition-shadow"
                  style={{ borderColor: "#e5dfd3" }}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="p-3 rounded-xl" style={{ backgroundColor: stat.color + "20" }}>
                      <Icon className="h-6 w-6" style={{ color: stat.color }} />
                    </div>
                    <span className="text-sm font-bold px-2 py-1 rounded-lg" style={{ backgroundColor: "#05966920", color: "#059669" }}>
                      {stat.change}
                    </span>
                  </div>
                  <h3 className="text-3xl font-black mb-1" style={{ color: "#2c2416" }}>
                    {stat.value}
                  </h3>
                  <p className="text-sm" style={{ color: "#6b5d4f" }}>{stat.label}</p>
                </motion.div>
              );
            })}
          </div>

          {/* Charts and Activities */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Recent Activities */}
            <div className="lg:col-span-2 bg-white rounded-2xl p-6 border" style={{ borderColor: "#e5dfd3" }}>
              <h2 className="text-xl font-black mb-6 flex items-center gap-2" style={{ color: "#2c2416" }}>
                <TrendingUp className="h-5 w-5" style={{ color: "#8b6f47" }} />
                فعالیت‌های اخیر
              </h2>
              <div className="space-y-4">
                {recentActivities.map((activity, idx) => {
                  const Icon = activity.icon;
                  return (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      className="flex items-center gap-4 p-4 rounded-xl hover:bg-gray-50 transition-colors"
                    >
                      <div className="p-2 rounded-lg" style={{ backgroundColor: "#f5f1e8" }}>
                        <Icon className="h-5 w-5" style={{ color: "#8b6f47" }} />
                      </div>
                      <div className="flex-1">
                        <p className="font-bold text-sm" style={{ color: "#2c2416" }}>{activity.title}</p>
                        <p className="text-xs" style={{ color: "#6b5d4f" }}>{activity.time}</p>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </div>

            {/* Top Articles */}
            <div className="bg-white rounded-2xl p-6 border" style={{ borderColor: "#e5dfd3" }}>
              <h2 className="text-xl font-black mb-6 flex items-center gap-2" style={{ color: "#2c2416" }}>
                <BookOpen className="h-5 w-5" style={{ color: "#2d5016" }} />
                پربازدیدترین مقالات
              </h2>
              <div className="space-y-4">
                {topArticles.map((article, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className="pb-4 border-b last:border-0 last:pb-0"
                    style={{ borderColor: "#e5dfd3" }}
                  >
                    <h3 className="font-bold text-sm mb-2 line-clamp-2" style={{ color: "#2c2416" }}>
                      {article.title}
                    </h3>
                    <div className="flex items-center gap-4 text-xs" style={{ color: "#6b5d4f" }}>
                      <span className="flex items-center gap-1">
                        <Eye className="h-3 w-3" />
                        {article.views.toLocaleString()}
                      </span>
                      <span className="flex items-center gap-1">
                        <Heart className="h-3 w-3" />
                        {article.likes}
                      </span>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}