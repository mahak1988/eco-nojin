"use client";

﻿"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight, Search, Eye, User, Mail, Calendar,
  Shield, Edit, Trash2, CheckCircle, XCircle, Users as UsersIcon, DollarSign } from "lucide-react";

const USERS = [
  {
    id: 1,
    name: "علی احمدی",
    email: "ali@example.com",
    role: "customer",
    status: "active",
    registered_at: "۱۴۰۳/۰۸/۱۵",
    orders_count: 12,
    total_spent: 15600000,
    avatar: "👨‍🌾"
  },
  {
    id: 2,
    name: "فاطمه رضایی",
    email: "fateme@example.com",
    role: "customer",
    status: "active",
    registered_at: "۱۴۰۳/۰۷/۲۰",
    orders_count: 8,
    total_spent: 9800000,
    avatar: "👩‍🌾"
  },
  {
    id: 3,
    name: "دکتر محمد حسینی",
    email: "mohammad@example.com",
    role: "admin",
    status: "active",
    registered_at: "۱۴۰۳/۰۱/۰۱",
    orders_count: 0,
    total_spent: 0,
    avatar: "👨‍💼"
  },
  {
    id: 4,
    name: "زهرا کریمی",
    email: "zahra@example.com",
    role: "customer",
    status: "inactive",
    registered_at: "۱۴۰۳/۰۶/۱۰",
    orders_count: 3,
    total_spent: 4500000,
    avatar: "👩‍💼"
  },
  {
    id: 5,
    name: "حسین نوری",
    email: "hossein@example.com",
    role: "customer",
    status: "active",
    registered_at: "۱۴۰۳/۰۵/۲۵",
    orders_count: 15,
    total_spent: 23400000,
    avatar: "👨‍🔬"
  },
];

const ROLE_CONFIG = {
  customer: { label: "مشتری", color: "#8b6f47", icon: User },
  admin: { label: "مدیر", color: "#2d5016", icon: Shield },
};

export default function UsersManagement() {
  const [searchQuery, setSearchQuery] = useState("");
  const [filterRole, setFilterRole] = useState("all");
  const [selectedUser, setSelectedUser] = useState<any>(null);

  const filteredUsers = USERS.filter(user => {
    const matchSearch = 
      user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.email.toLowerCase().includes(searchQuery.toLowerCase());
    const matchRole = filterRole === "all" || user.role === filterRole;
    return matchSearch && matchRole;
  });

  const totalUsers = USERS.length;
  const activeUsers = USERS.filter(u => u.status === "active").length;
  const totalRevenue = USERS.reduce((sum, u) => sum + u.total_spent, 0);

  return (
    <div className="min-h-screen" style={{ backgroundColor: "#f5f1e8" }}>
      {/* Header */}
      <header className="bg-white border-b px-6 py-4" style={{ borderColor: "#e5dfd3" }}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/admin" className="p-2 rounded-lg hover:bg-gray-100 transition-colors">
              <ArrowRight className="h-5 w-5" style={{ color: "#6b5d4f" }} />
            </Link>
            <h1 className="text-2xl font-black" style={{ color: "#2c2416" }}>مدیریت کاربران</h1>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="p-6">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-white rounded-2xl p-6 border" style={{ borderColor: "#e5dfd3" }}>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-3 rounded-xl" style={{ backgroundColor: "#8b6f4720" }}>
                <UsersIcon className="h-6 w-6" style={{ color: "#8b6f47" }} />
              </div>
              <div>
                <p className="text-sm" style={{ color: "#6b5d4f" }}>کل کاربران</p>
                <p className="text-2xl font-black" style={{ color: "#2c2416" }}>{totalUsers}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-6 border" style={{ borderColor: "#e5dfd3" }}>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-3 rounded-xl" style={{ backgroundColor: "#05966920" }}>
                <CheckCircle className="h-6 w-6" style={{ color: "#059669" }} />
              </div>
              <div>
                <p className="text-sm" style={{ color: "#6b5d4f" }}>کاربران فعال</p>
                <p className="text-2xl font-black" style={{ color: "#2c2416" }}>{activeUsers}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-6 border" style={{ borderColor: "#e5dfd3" }}>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-3 rounded-xl" style={{ backgroundColor: "#2d501620" }}>
                <DollarSign className="h-6 w-6" style={{ color: "#2d5016" }} />
              </div>
              <div>
                <p className="text-sm" style={{ color: "#6b5d4f" }}>کل درآمد از کاربران</p>
                <p className="text-2xl font-black" style={{ color: "#2c2416" }}>
                  {totalRevenue.toLocaleString()} تومان
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-2xl p-6 border mb-6" style={{ borderColor: "#e5dfd3" }}>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute right-4 top-1/2 -translate-y-1/2 h-5 w-5" style={{ color: "#6b5d4f" }} />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="جستجو بر اساس نام یا ایمیل..."
                className="w-full pr-12 pl-4 py-3 rounded-xl border focus:outline-none focus:ring-2"
                style={{ borderColor: "#e5dfd3", color: "#2c2416" }}
              />
            </div>
            <select
              value={filterRole}
              onChange={(e) => setFilterRole(e.target.value)}
              className="px-4 py-3 rounded-xl border focus:outline-none focus:ring-2"
              style={{ borderColor: "#e5dfd3", color: "#2c2416" }}
            >
              <option value="all">همه نقش‌ها</option>
              <option value="customer">مشتری</option>
              <option value="admin">مدیر</option>
            </select>
          </div>
        </div>

        {/* Users Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredUsers.map((user, idx) => {
            const roleConfig = ROLE_CONFIG[user.role as keyof typeof ROLE_CONFIG];
            const RoleIcon = roleConfig.icon;
            return (
              <motion.div
                key={user.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="bg-white rounded-2xl overflow-hidden border hover:shadow-lg transition-shadow"
                style={{ borderColor: "#e5dfd3" }}
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-16 h-16 rounded-full flex items-center justify-center text-3xl" style={{ backgroundColor: "#f5f1e8" }}>
                        {user.avatar}
                      </div>
                      <div>
                        <h3 className="font-black text-lg" style={{ color: "#2c2416" }}>{user.name}</h3>
                        <p className="text-sm flex items-center gap-1" style={{ color: "#6b5d4f" }}>
                          <Mail className="h-3 w-3" />
                          {user.email}
                        </p>
                      </div>
                    </div>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-bold ${
                        user.status === "active" ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-700"
                      }`}
                    >
                      {user.status === "active" ? "فعال" : "غیرفعال"}
                    </span>
                  </div>

                  <div className="space-y-3 mb-4">
                    <div className="flex items-center gap-2">
                      <RoleIcon className="h-4 w-4" style={{ color: roleConfig.color }} />
                      <span className="text-sm font-bold" style={{ color: roleConfig.color }}>
                        {roleConfig.label}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-sm" style={{ color: "#6b5d4f" }}>
                      <Calendar className="h-4 w-4" />
                      <span>عضویت: {user.registered_at}</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3 mb-4 pt-4 border-t" style={{ borderColor: "#e5dfd3" }}>
                    <div>
                      <p className="text-xs" style={{ color: "#6b5d4f" }}>تعداد سفارشات</p>
                      <p className="font-black text-lg" style={{ color: "#2c2416" }}>{user.orders_count}</p>
                    </div>
                    <div>
                      <p className="text-xs" style={{ color: "#6b5d4f" }}>مجموع خرید</p>
                      <p className="font-black text-lg" style={{ color: "#2d5016" }}>
                        {user.total_spent.toLocaleString()}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setSelectedUser(user)}
                      className="flex-1 py-2 rounded-lg font-bold text-white text-sm"
                      style={{ backgroundColor: "#8b6f47" }}
                    >
                      <Eye className="h-4 w-4 inline ml-1" />
                      مشاهده
                    </button>
                    <button onClick={() => console.log("Button clicked")}  className="p-2 rounded-lg hover:bg-blue-50">
                      <Edit className="h-4 w-4 text-blue-600" />
                    </button>
                    <button onClick={() => console.log("Button clicked")}  className="p-2 rounded-lg hover:bg-red-50">
                      <Trash2 className="h-4 w-4 text-red-600" />
                    </button>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>

        {filteredUsers.length === 0 && (
          <div className="text-center py-12 bg-white rounded-2xl border" style={{ borderColor: "#e5dfd3" }}>
            <User className="h-16 w-16 mx-auto mb-4" style={{ color: "#6b5d4f" }} />
            <p className="text-lg" style={{ color: "#6b5d4f" }}>کاربری یافت نشد</p>
          </div>
        )}
      </div>

      {/* User Details Modal */}
      {selectedUser && (
        <div
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedUser(null)}
        >
          <div
            className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between" style={{ borderColor: "#e5dfd3" }}>
              <h2 className="text-xl font-black" style={{ color: "#2c2416" }}>
                جزئیات کاربر
              </h2>
              <button onClick={() => setSelectedUser(null)} className="p-2 rounded-lg hover:bg-gray-100">
                <XCircle className="h-5 w-5" style={{ color: "#6b5d4f" }} />
              </button>
            </div>

            <div className="p-6 space-y-6">
              <div className="flex items-center gap-4">
                <div className="w-24 h-24 rounded-full flex items-center justify-center text-5xl" style={{ backgroundColor: "#f5f1e8" }}>
                  {selectedUser.avatar}
                </div>
                <div>
                  <h3 className="text-2xl font-black" style={{ color: "#2c2416" }}>{selectedUser.name}</h3>
                  <p className="text-sm flex items-center gap-1" style={{ color: "#6b5d4f" }}>
                    <Mail className="h-4 w-4" />
                    {selectedUser.email}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-xl p-4">
                  <p className="text-sm mb-1" style={{ color: "#6b5d4f" }}>نقش</p>
                  <p className="font-black" style={{ color: "#2c2416" }}>
                    {ROLE_CONFIG[selectedUser.role as keyof typeof ROLE_CONFIG].label}
                  </p>
                </div>
                <div className="bg-gray-50 rounded-xl p-4">
                  <p className="text-sm mb-1" style={{ color: "#6b5d4f" }}>وضعیت</p>
                  <p className="font-black" style={{ color: selectedUser.status === "active" ? "#059669" : "#6b5d4f" }}>
                    {selectedUser.status === "active" ? "فعال" : "غیرفعال"}
                  </p>
                </div>
                <div className="bg-gray-50 rounded-xl p-4">
                  <p className="text-sm mb-1" style={{ color: "#6b5d4f" }}>تاریخ عضویت</p>
                  <p className="font-black" style={{ color: "#2c2416" }}>{selectedUser.registered_at}</p>
                </div>
                <div className="bg-gray-50 rounded-xl p-4">
                  <p className="text-sm mb-1" style={{ color: "#6b5d4f" }}>تعداد سفارشات</p>
                  <p className="font-black" style={{ color: "#2c2416" }}>{selectedUser.orders_count}</p>
                </div>
              </div>

              <div className="bg-green-50 rounded-xl p-6">
                <p className="text-sm mb-2" style={{ color: "#6b5d4f" }}>مجموع خرید</p>
                <p className="text-3xl font-black" style={{ color: "#2d5016" }}>
                  {selectedUser.total_spent.toLocaleString()} تومان
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}