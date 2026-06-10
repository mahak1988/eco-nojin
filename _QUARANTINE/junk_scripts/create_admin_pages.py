#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📦 ایجاد صفحات مدیریت سفارشات و کاربران
"""
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
WEB_DIR = ROOT / "apps" / "web" / "src" / "app"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"   ✅ {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")


def main():
    print("📦 ایجاد صفحات مدیریت سفارشات و کاربران")
    print("=" * 70)

    # =========================================================================
    # 1. صفحه مدیریت سفارشات
    # =========================================================================
    print("\n📝 ایجاد صفحه مدیریت سفارشات...")
    
    orders_content = '''"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight, Search, Eye, Package, User, Calendar,
  DollarSign, CheckCircle, Clock, XCircle, Truck, Filter
} from "lucide-react";

const ORDERS = [
  {
    id: "ECO-1234",
    customer: "علی احمدی",
    email: "ali@example.com",
    products: ["بذر گندم مقاوم", "سنسور رطوبت"],
    total: 2950000,
    status: "delivered",
    date: "۱۴۰۳/۰۹/۱۵",
    address: "تهران، خیابان ولیعصر"
  },
  {
    id: "ECO-1235",
    customer: "فاطمه رضایی",
    email: "fateme@example.com",
    products: ["کود هیومیک اسید"],
    total: 850000,
    status: "processing",
    date: "۱۴۰۳/۰۹/۱۴",
    address: "اصفهان، خیابان چهارباغ"
  },
  {
    id: "ECO-1236",
    customer: "محمد حسینی",
    email: "mohammad@example.com",
    products: ["سیستم آبیاری قطره‌ای", "بذر پسته"],
    total: 15450000,
    status: "shipped",
    date: "۱۴۰۳/۰۹/۱۳",
    address: "کرمان، بلوار جمهوری"
  },
  {
    id: "ECO-1237",
    customer: "زهرا کریمی",
    email: "zahra@example.com",
    products: ["سنسور دما"],
    total: 1200000,
    status: "pending",
    date: "۱۴۰۳/۰۹/۱۲",
    address: "شیراز، خیابان زند"
  },
  {
    id: "ECO-1238",
    customer: "حسین نوری",
    email: "hossein@example.com",
    products: ["کود ارگانیک", "بذر جو"],
    total: 1650000,
    status: "cancelled",
    date: "۱۴۰۳/۰۹/۱۱",
    address: "مشهد، بلوار وکیل‌آباد"
  },
];

const STATUS_CONFIG = {
  pending: { label: "در انتظار پرداخت", color: "#f59e0b", icon: Clock },
  processing: { label: "در حال پردازش", color: "#3b82f6", icon: Package },
  shipped: { label: "ارسال شده", color: "#8b5cf6", icon: Truck },
  delivered: { label: "تحویل داده شده", color: "#059669", icon: CheckCircle },
  cancelled: { label: "لغو شده", color: "#dc2626", icon: XCircle },
};

export default function OrdersManagement() {
  const [searchQuery, setSearchQuery] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");
  const [selectedOrder, setSelectedOrder] = useState<any>(null);

  const filteredOrders = ORDERS.filter(order => {
    const matchSearch = 
      order.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      order.customer.toLowerCase().includes(searchQuery.toLowerCase());
    const matchStatus = filterStatus === "all" || order.status === filterStatus;
    return matchSearch && matchStatus;
  });

  const totalRevenue = ORDERS.reduce((sum, o) => sum + o.total, 0);
  const pendingOrders = ORDERS.filter(o => o.status === "pending").length;
  const deliveredOrders = ORDERS.filter(o => o.status === "delivered").length;

  return (
    <div className="min-h-screen" style={{ backgroundColor: "#f5f1e8" }}>
      {/* Header */}
      <header className="bg-white border-b px-6 py-4" style={{ borderColor: "#e5dfd3" }}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/admin" className="p-2 rounded-lg hover:bg-gray-100 transition-colors">
              <ArrowRight className="h-5 w-5" style={{ color: "#6b5d4f" }} />
            </Link>
            <h1 className="text-2xl font-black" style={{ color: "#2c2416" }}>مدیریت سفارشات</h1>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="p-6">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-white rounded-2xl p-6 border" style={{ borderColor: "#e5dfd3" }}>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-3 rounded-xl" style={{ backgroundColor: "#05966920" }}>
                <DollarSign className="h-6 w-6" style={{ color: "#059669" }} />
              </div>
              <div>
                <p className="text-sm" style={{ color: "#6b5d4f" }}>کل درآمد</p>
                <p className="text-2xl font-black" style={{ color: "#2c2416" }}>
                  {totalRevenue.toLocaleString()} تومان
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-6 border" style={{ borderColor: "#e5dfd3" }}>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-3 rounded-xl" style={{ backgroundColor: "#f59e0b20" }}>
                <Clock className="h-6 w-6" style={{ color: "#f59e0b" }} />
              </div>
              <div>
                <p className="text-sm" style={{ color: "#6b5d4f" }}>در انتظار پرداخت</p>
                <p className="text-2xl font-black" style={{ color: "#2c2416" }}>{pendingOrders}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-6 border" style={{ borderColor: "#e5dfd3" }}>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-3 rounded-xl" style={{ backgroundColor: "#05966920" }}>
                <CheckCircle className="h-6 w-6" style={{ color: "#059669" }} />
              </div>
              <div>
                <p className="text-sm" style={{ color: "#6b5d4f" }}>تحویل داده شده</p>
                <p className="text-2xl font-black" style={{ color: "#2c2416" }}>{deliveredOrders}</p>
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
                placeholder="جستجو بر اساس شماره سفارش یا نام مشتری..."
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
              <option value="pending">در انتظار پرداخت</option>
              <option value="processing">در حال پردازش</option>
              <option value="shipped">ارسال شده</option>
              <option value="delivered">تحویل داده شده</option>
              <option value="cancelled">لغو شده</option>
            </select>
          </div>
        </div>

        {/* Orders Table */}
        <div className="bg-white rounded-2xl border overflow-hidden" style={{ borderColor: "#e5dfd3" }}>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead style={{ backgroundColor: "#f5f1e8" }}>
                <tr>
                  <th className="text-right px-6 py-4 font-bold text-sm" style={{ color: "#6b5d4f" }}>شماره سفارش</th>
                  <th className="text-right px-6 py-4 font-bold text-sm" style={{ color: "#6b5d4f" }}>مشتری</th>
                  <th className="text-right px-6 py-4 font-bold text-sm" style={{ color: "#6b5d4f" }}>محصولات</th>
                  <th className="text-right px-6 py-4 font-bold text-sm" style={{ color: "#6b5d4f" }}>مبلغ کل</th>
                  <th className="text-right px-6 py-4 font-bold text-sm" style={{ color: "#6b5d4f" }}>وضعیت</th>
                  <th className="text-right px-6 py-4 font-bold text-sm" style={{ color: "#6b5d4f" }}>تاریخ</th>
                  <th className="text-right px-6 py-4 font-bold text-sm" style={{ color: "#6b5d4f" }}>عملیات</th>
                </tr>
              </thead>
              <tbody>
                {filteredOrders.map((order, idx) => {
                  const statusConfig = STATUS_CONFIG[order.status as keyof typeof STATUS_CONFIG];
                  const StatusIcon = statusConfig.icon;
                  return (
                    <motion.tr
                      key={order.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      className="border-t hover:bg-gray-50 transition-colors"
                      style={{ borderColor: "#e5dfd3" }}
                    >
                      <td className="px-6 py-4">
                        <span className="font-black text-sm" style={{ color: "#2c2416" }}>{order.id}</span>
                      </td>
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-bold text-sm" style={{ color: "#2c2416" }}>{order.customer}</p>
                          <p className="text-xs" style={{ color: "#6b5d4f" }}>{order.email}</p>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-1">
                          {order.products.slice(0, 2).map((product, i) => (
                            <span key={i} className="px-2 py-1 rounded text-xs" style={{ backgroundColor: "#f5f1e8", color: "#6b5d4f" }}>
                              {product}
                            </span>
                          ))}
                          {order.products.length > 2 && (
                            <span className="px-2 py-1 rounded text-xs" style={{ backgroundColor: "#f5f1e8", color: "#6b5d4f" }}>
                              +{order.products.length - 2}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="font-black" style={{ color: "#2d5016" }}>
                          {order.total.toLocaleString()} تومان
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold"
                          style={{ backgroundColor: statusConfig.color + "20", color: statusConfig.color }}
                        >
                          <StatusIcon className="h-3 w-3" />
                          {statusConfig.label}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-sm" style={{ color: "#6b5d4f" }}>{order.date}</span>
                      </td>
                      <td className="px-6 py-4">
                        <button
                          onClick={() => setSelectedOrder(order)}
                          className="p-2 rounded-lg hover:bg-blue-50 transition-colors"
                          title="مشاهده جزئیات"
                        >
                          <Eye className="h-4 w-4 text-blue-600" />
                        </button>
                      </td>
                    </motion.tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {filteredOrders.length === 0 && (
            <div className="text-center py-12">
              <Package className="h-16 w-16 mx-auto mb-4" style={{ color: "#6b5d4f" }} />
              <p className="text-lg" style={{ color: "#6b5d4f" }}>سفارشی یافت نشد</p>
            </div>
          )}
        </div>
      </div>

      {/* Order Details Modal */}
      {selectedOrder && (
        <div
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedOrder(null)}
        >
          <div
            className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between" style={{ borderColor: "#e5dfd3" }}>
              <h2 className="text-xl font-black" style={{ color: "#2c2416" }}>
                جزئیات سفارش {selectedOrder.id}
              </h2>
              <button onClick={() => setSelectedOrder(null)} className="p-2 rounded-lg hover:bg-gray-100">
                <XCircle className="h-5 w-5" style={{ color: "#6b5d4f" }} />
              </button>
            </div>

            <div className="p-6 space-y-6">
              <div>
                <h3 className="font-bold mb-3" style={{ color: "#2c2416" }}>اطلاعات مشتری</h3>
                <div className="bg-gray-50 rounded-xl p-4 space-y-2">
                  <p className="flex items-center gap-2">
                    <User className="h-4 w-4" style={{ color: "#6b5d4f" }} />
                    <span style={{ color: "#2c2416" }}>{selectedOrder.customer}</span>
                  </p>
                  <p className="text-sm" style={{ color: "#6b5d4f" }}>{selectedOrder.email}</p>
                  <p className="text-sm" style={{ color: "#6b5d4f" }}>{selectedOrder.address}</p>
                </div>
              </div>

              <div>
                <h3 className="font-bold mb-3" style={{ color: "#2c2416" }}>محصولات</h3>
                <div className="space-y-2">
                  {selectedOrder.products.map((product, idx) => (
                    <div key={idx} className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
                      <Package className="h-5 w-5" style={{ color: "#8b6f47" }} />
                      <span style={{ color: "#2c2416" }}>{product}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="font-bold mb-3" style={{ color: "#2c2416" }}>مبلغ کل</h3>
                <div className="bg-green-50 rounded-xl p-4">
                  <p className="text-2xl font-black" style={{ color: "#2d5016" }}>
                    {selectedOrder.total.toLocaleString()} تومان
                  </p>
                </div>
              </div>

              <div>
                <h3 className="font-bold mb-3" style={{ color: "#2c2416" }}>وضعیت</h3>
                <div className="flex items-center gap-2">
                  {(() => {
                    const statusConfig = STATUS_CONFIG[selectedOrder.status as keyof typeof STATUS_CONFIG];
                    const StatusIcon = statusConfig.icon;
                    return (
                      <span
                        className="inline-flex items-center gap-2 px-4 py-2 rounded-full font-bold"
                        style={{ backgroundColor: statusConfig.color + "20", color: statusConfig.color }}
                      >
                        <StatusIcon className="h-5 w-5" />
                        {statusConfig.label}
                      </span>
                    );
                  })()}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
'''
    
    write_file(WEB_DIR / "admin" / "orders" / "page.tsx", orders_content)

    # =========================================================================
    # 2. صفحه مدیریت کاربران
    # =========================================================================
    print("\n📝 ایجاد صفحه مدیریت کاربران...")
    
    users_content = '''"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight, Search, Eye, User, Mail, Calendar,
  Shield, Edit, Trash2, CheckCircle, XCircle, Users as UsersIcon
} from "lucide-react";

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
                    <button className="p-2 rounded-lg hover:bg-blue-50">
                      <Edit className="h-4 w-4 text-blue-600" />
                    </button>
                    <button className="p-2 rounded-lg hover:bg-red-50">
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
'''
    
    write_file(WEB_DIR / "admin" / "users" / "page.tsx", users_content)

    # =========================================================================
    # 3. پاک‌سازی کش Next.js
    # =========================================================================
    print("\n🧹 پاک‌سازی کش Next.js...")
    next_dir = ROOT / "apps" / "web" / ".next"
    if next_dir.exists():
        try:
            shutil.rmtree(next_dir)
            print("   ✅ پوشه .next حذف شد")
        except Exception as e:
            print(f"   ⚠️  خطا در حذف: {e}")
    else:
        print("   ℹ️  پوشه .next وجود نداشت")

    # =========================================================================
    # خلاصه
    # =========================================================================
    print("\n" + "=" * 70)
    print("✅ تمام صفحات CMS با موفقیت ایجاد شدند!")
    print("\n🎯 صفحات ایجاد شده:")
    print("   📊 داشبورد اصلی: /admin")
    print("   📝 مدیریت مقالات: /admin/blog")
    print("   📦 مدیریت محصولات: /admin/products")
    print("   🛒 مدیریت سفارشات: /admin/orders")
    print("   👥 مدیریت کاربران: /admin/users")

    print("\n🚀 گام بعدی:")
    print("   1. سرور فرانت‌اند را ری‌استارت کنید:")
    print("      pnpm run dev -- -p 3001")
    print("")
    print("   2. مشاهده:")
    print("      • http://localhost:3001/admin")
    print("      • http://localhost:3001/admin/orders")
    print("      • http://localhost:3001/admin/users")

    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())