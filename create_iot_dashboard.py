#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 ایجاد داشبورد IoT فرانت‌اند
نمایش real-time داده‌های سنسورها با چارت‌های تعاملی
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
WEB = ROOT / "apps" / "web" / "src"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"   ✅ {path.relative_to(ROOT)}")


# ========== 1. IoT Dashboard Page ==========
def create_dashboard():
    print("\n📊 ایجاد داشبورد IoT...")
    
    content = '''"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { 
  ArrowRight, Activity, Battery, Droplets, Thermometer, 
  Wind, MapPin, RefreshCw, AlertTriangle, CheckCircle,
  TrendingUp, Wifi, Signal
} from "lucide-react";
import {
  ResponsiveContainer, LineChart, Line, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, BarChart, Bar
} from "recharts";

interface Sensor {
  sensor_code: string;
  sensor_type: string;
  location_name: string;
  latitude: number;
  longitude: number;
  status: string;
  battery_level: number;
}

interface Stats {
  total_sensors: number;
  active_sensors: number;
  total_readings_24h: number;
  alerts_today: number;
  avg_battery: number;
}

const SENSOR_ICONS: Record<string, any> = {
  tdr: Droplets,
  flume: Activity,
  rain: Wind,
  piez: Thermometer,
  weather: Thermometer,
};

const SENSOR_COLORS: Record<string, string> = {
  tdr: "#3b82f6",
  flume: "#10b981",
  rain: "#06b6d4",
  piez: "#8b5cf6",
  weather: "#f59e0b",
};

export default function IoTDashboardPage() {
  const [sensors, setSensors] = useState<Sensor[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const fetchData = async () => {
    try {
      const [sensorsRes, statsRes] = await Promise.all([
        fetch("http://localhost:8000/api/v1/iot/sensors"),
        fetch("http://localhost:8000/api/v1/iot/stats"),
      ]);
      
      if (sensorsRes.ok && statsRes.ok) {
        const sensorsData = await sensorsRes.json();
        const statsData = await statsRes.json();
        setSensors(sensorsData);
        setStats(statsData);
        setLastUpdate(new Date());
      }
    } catch (error) {
      console.error("Failed to fetch data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  // Generate mock time-series data for chart
  const generateChartData = () => {
    const data = [];
    const now = new Date();
    for (let i = 23; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 3600000);
      data.push({
        time: time.getHours() + ":00",
        tdr: 35 + Math.random() * 20,
        flume: 0.5 + Math.random() * 1.5,
        rain: Math.random() * 10,
      });
    }
    return data;
  };

  const chartData = generateChartData();

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-500 to-blue-600 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-16">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-6 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-6">
              <div className="p-5 rounded-3xl bg-gradient-to-br from-cyan-500 to-blue-600 shadow-2xl">
                <Activity className="h-12 w-12 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-cyan-400 text-sm font-medium mb-2">Real-time Monitoring</p>
                <h1 className="text-5xl md:text-6xl font-black text-white mb-4">داشبورد IoT</h1>
                <p className="text-xl text-slate-300 max-w-3xl leading-relaxed">
                  پایش لحظه‌ای سنسورهای حوضه‌های آبریز با داده‌های real-time از شبکه IoT
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-4 text-sm text-slate-400">
              <span className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                Live
              </span>
              <span>آخرین به‌روزرسانی: {lastUpdate.toLocaleTimeString("fa-IR")}</span>
              <button 
                onClick={fetchData}
                className="flex items-center gap-2 px-3 py-1 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
              >
                <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
                بروزرسانی
              </button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats Cards */}
      <section className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {[
            { label: "کل سنسورها", value: stats?.total_sensors || 0, icon: Activity, color: "#06b6d4" },
            { label: "سنسورهای فعال", value: stats?.active_sensors || 0, icon: CheckCircle, color: "#10b981" },
            { label: "خوانش‌های ۲۴ ساعت", value: stats?.total_readings_24h || 0, icon: TrendingUp, color: "#3b82f6" },
            { label: "هشدارهای امروز", value: stats?.alerts_today || 0, icon: AlertTriangle, color: stats?.alerts_today ? "#ef4444" : "#10b981" },
            { label: "میانگین باتری", value: `${stats?.avg_battery || 0}%`, icon: Battery, color: "#f59e0b" },
          ].map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all"
            >
              <stat.icon className="h-8 w-8 mb-3" style={{ color: stat.color }} />
              <p className="text-3xl font-black text-white mb-1">{stat.value}</p>
              <p className="text-sm text-slate-400">{stat.label}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Time Series Chart */}
      <section className="container mx-auto px-6 py-8">
        <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
          <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-cyan-400" />
            روند داده‌ها (۲۴ ساعت اخیر)
          </h3>
          <ResponsiveContainer width="100%" height={350}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="tdrGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="flumeGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="time" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: "#0f172a", 
                  border: "1px solid #334155", 
                  borderRadius: "8px" 
                }}
              />
              <Legend />
              <Area type="monotone" dataKey="tdr" stroke="#3b82f6" fill="url(#tdrGrad)" name="رطوبت خاک (%)" />
              <Area type="monotone" dataKey="flume" stroke="#10b981" fill="url(#flumeGrad)" name="دبی (m³/s)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Sensors Grid */}
      <section className="container mx-auto px-6 py-8">
        <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
          <Wifi className="h-6 w-6 text-cyan-400" />
          سنسورهای فعال
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sensors.map((sensor, i) => {
            const Icon = SENSOR_ICONS[sensor.sensor_type] || Activity;
            const color = SENSOR_COLORS[sensor.sensor_type] || "#64748b";
            
            return (
              <motion.div
                key={sensor.sensor_code}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all group"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="p-3 rounded-xl" style={{ backgroundColor: color + "20" }}>
                    <Icon className="h-6 w-6" style={{ color }} />
                  </div>
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${
                      sensor.status === "active" ? "bg-emerald-400 animate-pulse" : "bg-red-400"
                    }`} />
                    <span className="text-xs text-slate-400 capitalize">{sensor.status}</span>
                  </div>
                </div>
                
                <h4 className="text-xl font-bold text-white mb-1">{sensor.sensor_code}</h4>
                <p className="text-sm text-slate-400 mb-4 flex items-center gap-1">
                  <MapPin className="h-3 w-3" />
                  {sensor.location_name}
                </p>
                
                <div className="space-y-3">
                  <div>
                    <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                      <span className="flex items-center gap-1">
                        <Battery className="h-3 w-3" /> باتری
                      </span>
                      <span>{sensor.battery_level?.toFixed(0)}%</span>
                    </div>
                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${sensor.battery_level}%` }}
                        transition={{ duration: 1, delay: i * 0.1 }}
                        className={`h-full rounded-full ${
                          sensor.battery_level > 50 ? "bg-emerald-500" :
                          sensor.battery_level > 20 ? "bg-amber-500" : "bg-red-500"
                        }`}
                      />
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-800">
                    <span className="flex items-center gap-1">
                      <Signal className="h-3 w-3" /> {sensor.sensor_type.toUpperCase()}
                    </span>
                    <span>
                      {sensor.latitude?.toFixed(3)}, {sensor.longitude?.toFixed(3)}
                    </span>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </section>

      {/* API Info */}
      <section className="container mx-auto px-6 py-8">
        <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
          <h3 className="text-xl font-bold text-white mb-4">📡 API Endpoints</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { method: "GET", path: "/api/v1/iot/sensors", desc: "لیست تمام سنسورها" },
              { method: "GET", path: "/api/v1/iot/stats", desc: "آمار کلی IoT" },
              { method: "GET", path: "/api/v1/iot/sensors/{code}/latest", desc: "آخرین خوانش" },
              { method: "POST", path: "/api/v1/iot/ingest", desc: "ثبت خوانش جدید" },
            ].map((api, i) => (
              <div key={i} className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-xl">
                <span className={`px-2 py-1 rounded text-xs font-bold ${
                  api.method === "GET" ? "bg-emerald-500/20 text-emerald-400" : "bg-blue-500/20 text-blue-400"
                }`}>
                  {api.method}
                </span>
                <code className="text-sm text-slate-300 flex-1">{api.path}</code>
                <span className="text-xs text-slate-500">{api.desc}</span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
'''
    
    write_file(WEB / "app" / "iot" / "page.tsx", content)


# ========== 2. Add IoT link to Navbar ==========
def update_navbar():
    print("\n🧭 به‌روزرسانی Navbar...")
    
    navbar_path = WEB / "components" / "layout" / "Navbar.tsx"
    if not navbar_path.exists():
        print("   ⚠️  Navbar.tsx not found, skipping")
        return
    
    content = navbar_path.read_text(encoding="utf-8")
    
    # Add IoT link if not exists
    if 'href="/iot"' not in content:
        # Find the scientific modules section and add IoT
        if "SCIENTIFIC_MODULES" in content:
            content = content.replace(
                '{ id: "drought", title: "پایش خشکسالی", href: "/drought" },',
                '{ id: "drought", title: "پایش خشکسالی", href: "/drought" },\n  { id: "iot", title: "داشبورد IoT", href: "/iot" },'
            )
            navbar_path.write_text(content, encoding="utf-8")
            print("   ✅ IoT link added to Navbar")
        else:
            print("   ⚠️  Could not find SCIENTIFIC_MODULES in Navbar")
    else:
        print("   ℹ️  IoT link already exists")


# ========== Main ==========
def main():
    print("📊 ایجاد داشبورد IoT فرانت‌اند")
    print("=" * 70)
    
    if not WEB.exists():
        print(f"❌ دایرکتوری {WEB} یافت نشد!")
        return 1
    
    create_dashboard()
    update_navbar()
    
    print("\n" + "=" * 70)
    print("✅ داشبورد IoT ایجاد شد!")
    print("\n🚀 گام‌های بعدی:")
    print("   1. پاک‌سازی کش:")
    print("      cd apps\\web")
    print("      Remove-Item .next -Recurse -Force")
    print("")
    print("   2. اجرای سرور بک‌اند (در ترمینال ۱):")
    print("      cd D:\\econojin.com")
    print("      uvicorn api.main:app --reload --port 8000")
    print("")
    print("   3. اجرای سرور فرانت‌اند (در ترمینال ۲):")
    print("      cd D:\\econojin.com\\apps\\web")
    print("      pnpm run dev -- -p 3001")
    print("")
    print("   4. مشاهده:")
    print("      • داشبورد IoT: http://localhost:3001/iot")
    print("      • API Docs: http://localhost:8000/docs")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())