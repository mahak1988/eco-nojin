#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 Econojin Frontend Generator - نسخه نهایی و مطمئن
استفاده از .replace() به جای f-string برای جلوگیری از خطای JSX
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
WEB = ROOT / "apps" / "web" / "src"

MODULES = [
    {"id": "calendar", "name": "تقویم", "icon": "Calendar", "color": "#3b82f6", "desc": "مدیریت رویدادها", "chart": "bar", "data": "events", "xKey": "start", "yKey": "title"},
    {"id": "weather", "name": "هواشناسی", "icon": "CloudSun", "color": "#0ea5e9", "desc": "پیش‌بینی کشاورزی", "chart": "line", "data": "forecast", "xKey": "day", "yKey": "temp"},
    {"id": "accounting", "name": "حسابداری", "icon": "Wallet", "color": "#10b981", "desc": "مدیریت مالی", "chart": "pie", "data": "expenses", "xKey": "name", "yKey": "value"},
    {"id": "gis", "name": "GIS", "icon": "Map", "color": "#8b5cf6", "desc": "نقشه و تحلیل", "chart": "scatter", "data": "coordinates", "xKey": "x", "yKey": "ndvi"},
    {"id": "education", "name": "آموزش", "icon": "GraduationCap", "color": "#f59e0b", "desc": "کلاس‌های آنلاین", "chart": "radar", "data": "progress", "xKey": "skill", "yKey": "level"},
    {"id": "psychology", "name": "روانشناسی", "icon": "Brain", "color": "#ec4899", "desc": "سلامت روان", "chart": "area", "data": "mood", "xKey": "date", "yKey": "score"},
    {"id": "ecomining", "name": "EcoCoin", "icon": "Leaf", "color": "#22c55e", "desc": "ماینینگ سبز", "chart": "line", "data": "price", "xKey": "time", "yKey": "close"},
]

def write_file(filepath, content):
    fp = Path(filepath)
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(content, encoding="utf-8")
    rel = str(fp).replace(str(ROOT.parent.parent) + "\\", "")
    print(f"✅ {rel}")

# ========== کامپوننت‌های مشترک (بدون f-string) ==========
CHART_CARD = '''"""use client";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ResponsiveContainer, LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, Legend, AreaChart, Area } from "recharts";

export function ChartCard({ title, icon, data, chartType, xKey="name", yKey="value", colors=["#3b82f6","#10b981","#f59e0b","#ec4899"], badge, loading }) {
  if (loading) return <Card className="animate-pulse"><CardHeader><div className="h-6 bg-slate-700 rounded w-32"/></CardHeader><CardContent><div className="h-48 bg-slate-700 rounded"/></CardContent></Card>;
  const common = <><XAxis dataKey={xKey} stroke="#94a3b8" fontSize={12}/><YAxis stroke="#94a3b8" fontSize={12}/><Tooltip contentStyle={{backgroundColor:"#1e293b",border:"1px solid #334155",borderRadius:"8px"}}/><Legend/></>;
  const renderChart = () => {
    switch(chartType) {
      case "line": return <ResponsiveContainer width="100%" height={200}><LineChart data={data}>{common}<Line type="monotone" dataKey={yKey} stroke={colors[0]} strokeWidth={2} dot={{r:4}}/></LineChart></ResponsiveContainer>;
      case "bar": return <ResponsiveContainer width="100%" height={200}><BarChart data={data}>{common}<Bar dataKey={yKey} fill={colors[0]} radius={[4,4,0,0]}/></BarChart></ResponsiveContainer>;
      case "pie": return <ResponsiveContainer width="100%" height={200}><PieChart><Pie data={data} dataKey={yKey} nameKey={xKey} cx="50%" cy="50%" outerRadius={70} label>{data.map((_,i)=> <Cell key={i} fill={colors[i%colors.length]}/>)}</Pie><Tooltip contentStyle={{backgroundColor:"#1e293b",border:"1px solid #334155"}}/></PieChart></ResponsiveContainer>;
      case "area": return <ResponsiveContainer width="100%" height={200}><AreaChart data={data}>{common}<Area type="monotone" dataKey={yKey} stroke={colors[0]} fill={`url(#g)`} fillOpacity={0.3}/><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor={colors[0]} stopOpacity={0.3}/><stop offset="95%" stopColor={colors[0]} stopOpacity={0}/></linearGradient></defs></AreaChart></ResponsiveContainer>;
      default: return <div className="h-48 flex items-center justify-center text-slate-500">نمودار</div>;
    }
  };
  return (
    <motion.div initial={{opacity:0,y:20}} animate={{opacity:1,y:0}} transition={{duration:0.3}}>
      <Card className="card-hover">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg" style={{backgroundColor:colors[0]+"20"}}>{icon}</div>
              <CardTitle className="text-base">{title}</CardTitle>
            </div>
            {badge && <Badge variant={badge.variant}>{badge.label}</Badge>}
          </div>
        </CardHeader>
        <CardContent>{renderChart()}</CardContent>
      </Card>
    </motion.div>
  );
}
'''

DATA_TABLE = '''"""use client";
import { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, Filter, ChevronLeft, ChevronRight, ChevronUp, ChevronDown } from "lucide-react";

export function DataTable({data,columns,searchKeys=[],pageSize=10,emptyMessage="داده‌ای یافت نشد",onRowClick}){
  const [searchQuery,setSearchQuery]=useState("");
  const [sortKey,setSortKey]=useState(null);
  const [sortAsc,setSortAsc]=useState(true);
  const [page,setPage]=useState(1);
  const filtered=useMemo(()=>{
    let r=[...data];
    if(searchQuery) r=r.filter(row=>searchKeys.some(k=>String(row[k]).toLowerCase().includes(searchQuery.toLowerCase())));
    if(sortKey) r.sort((a,b)=>{const av=a[sortKey],bv=b[sortKey];return av<bv?(sortAsc?-1:1):av>bv?(sortAsc?1:-1):0;});
    return r;
  },[data,searchQuery,sortKey,sortAsc]);
  const paginated=filtered.slice((page-1)*pageSize,page*pageSize);
  const totalPages=Math.ceil(filtered.length/pageSize);
  return (
    <Card>
      <CardContent className="p-4">
        {searchKeys.length>0 && <div className="mb-4 relative"><Search className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500"/><Input placeholder="جستجو..." className="pr-10 max-w-xs" value={searchQuery} onChange={e=>{setSearchQuery(e.target.value);setPage(1);}}/></div>}
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-right">
            <thead><tr className="border-b border-slate-700">{columns.map(col=><th key={String(col.key)} className="px-4 py-3 font-semibold text-slate-300 cursor-pointer hover:text-primary-400" onClick={()=>col.sortable&&setSortKey(col.key)}><div className="flex items-center gap-1">{col.title}{col.sortable&&sortKey===col.key&&(sortAsc?<ChevronUp className="h-4 w-4"/>:<ChevronDown className="h-4 w-4"/>)}</div></th>)}</tr></thead>
            <tbody><AnimatePresence mode="popLayout">{paginated.map((row,idx)=><motion.tr key={row.id} initial={{opacity:0,x:-20}} animate={{opacity:1,x:0}} exit={{opacity:0}} transition={{delay:idx*0.03}} className={`border-b border-slate-800 hover:bg-slate-800/50 ${onRowClick?"cursor-pointer":""}`} onClick={()=>onRowClick?.(row)}>{columns.map(col=><td key={String(col.key)} className="px-4 py-3 text-slate-300" style={{width:col.width}}>{col.render?col.render(row[col.key],row):row[col.key]}</td>)}</motion.tr>)}</AnimatePresence></tbody>
          </table>
        </div>
        {paginated.length===0 && <div className="text-center py-12 text-slate-500"><Filter className="h-12 w-12 mx-auto mb-4 opacity-50"/><p>{emptyMessage}</p></div>}
        {totalPages>1 && <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-700"><p className="text-sm text-slate-400">صفحه {page} از {totalPages}</p><div className="flex gap-2"><Button variant="outline" size="sm" onClick={()=>setPage(p=>Math.max(1,p-1))} disabled={page===1}><ChevronRight className="h-4 w-4"/>قبلی</Button><Button variant="outline" size="sm" onClick={()=>setPage(p=>Math.min(totalPages,p+1))} disabled={page===totalPages}>بعدی <ChevronLeft className="h-4 w-4"/></Button></div></div>}
      </CardContent>
    </Card>
  );
}
'''

ANIMATED_STAT = '''"""use client";
import { motion, useSpring, useTransform } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { useEffect } from "react";

export function AnimatedStatCard({title,value,suffix="",prefix="",icon,color,trend}){
  const spring=useSpring(0,{damping:25,stiffness:150});
  const display=useTransform(spring,v=>prefix+Math.round(v).toLocaleString("fa-IR")+suffix);
  useEffect(()=>{spring.set(value);},[value,spring]);
  return (
    <motion.div whileHover={{y:-4}} transition={{type:"spring",stiffness:300}}>
      <Card className="card-hover" style={{borderLeft:"4px solid "+color}}>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div><p className="text-sm text-slate-400">{title}</p><motion.p className="text-2xl font-bold mt-1" style={{color}}>{display}</motion.p>{trend&&<div className={"flex items-center gap-1 mt-1 text-xs "+(trend.positive!==false?"text-success-400":"text-danger-400")}><span>{trend.positive!==false?"↑":"↓"}{Math.abs(trend.value).toLocaleString("fa-IR")}{trend.suffix||"%"}</span><span className="text-slate-500">{trend.label}</span></div>}</div>
            <motion.div className="p-3 rounded-xl" style={{backgroundColor:color+"20"}} whileHover={{scale:1.1}} transition={{type:"spring",stiffness:400}}>{icon}</motion.div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
'''

# ========== صفحه ماژول با استفاده از .replace() ==========
PAGE_TEMPLATE = '''"""use client";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { MainLayout } from "@/components/layout/main-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ChartCard } from "@/components/ui/ChartCard";
import { DataTable } from "@/components/ui/DataTable";
import { AnimatedStatCard } from "@/components/ui/AnimatedStatCard";
import { __ICON__, Plus, Search, Filter, Download, RefreshCw, Calendar as CalendarIcon, TrendingUp, AlertTriangle } from "lucide-react";

const mockData = {
  events: [{ id: 1, title: "جلسه تیم", start: "2026-06-10T10:00", category: "work" }],
  forecast: [{ day: "شنبه", temp: 22, rain: 10 }, { day: "یکشنبه", temp: 24, rain: 5 }],
  expenses: [{ name: "آب", value: 35 }, { name: "بذر", value: 28 }],
  coordinates: [{ x: 59.6, y: 36.3, ndvi: 0.62 }],
  progress: [{ skill: "برنامه‌نویسی", level: 85 }],
  mood: [{ date: "۱ خرداد", score: 7 }],
  price: [{ time: "۰۹:۰۰", close: 1.23 }],
};

export default function __NAME_CAP__Page() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({});
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => { setTimeout(() => { setData(mockData); setLoading(false); }, 800); }, []);

  const stats = [
    { title: "مجموع", value: 48, icon: <__ICON__ className="h-5 w-5"/>, color: "__COLOR__" },
    { title: "فعال", value: 32, icon: <TrendingUp className="h-5 w-5"/>, color: "#10b981" },
    { title: "در انتظار", value: 12, icon: <CalendarIcon className="h-5 w-5"/>, color: "#f59e0b" },
    { title: "هشدارها", value: 4, icon: <AlertTriangle className="h-5 w-5"/>, color: "#ef4444" },
  ];

  const columns = [
    { key: "id", title: "شناسه", sortable: true, width: "80px" },
    { key: "title", title: "عنوان", sortable: true },
    { key: "__XKEY__", title: "__XLABEL__", sortable: true },
    { key: "category", title: "دسته", render: (v) => <Badge variant="default">{v}</Badge> },
    { key: "actions", title: "عملیات", render: () => <div className="flex gap-1"><Button variant="ghost" size="sm">ویرایش</Button><Button variant="ghost" size="sm" className="text-danger-400">حذف</Button></div> },
  ];

  return (
    <MainLayout>
      <div className="space-y-6">
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <__ICON__ className="h-7 w-7" style={{ color: "__COLOR__" }} />
              __NAME_FA__
            </h1>
            <p className="text-slate-400">__DESC__</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm"><RefreshCw className="h-4 w-4 ml-1" /></Button>
            <Button variant="outline" size="sm"><Download className="h-4 w-4 ml-1" /> خروجی</Button>
            <Button size="sm" style={{ backgroundColor: "__COLOR__" }}><Plus className="h-4 w-4 ml-1" /> افزودن</Button>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.map((stat,i)=><AnimatedStatCard key={i} {...stat} />)}
        </div>

        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
            <Input placeholder="جستجو..." className="pr-10" value={searchQuery} onChange={e=>setSearchQuery(e.target.value)} />
          </div>
          <Button variant="secondary"><Filter className="h-4 w-4 ml-1" /> فیلتر</Button>
        </div>

        <ChartCard 
          title="نمودار __NAME_FA__"
          icon={<__ICON__ className="h-5 w-5" style={{ color: "__COLOR__" }} />}
          data={data["__DATA__"] || []}
          chartType="__CHART__"
          xKey="__XKEY__"
          yKey="__YKEY__"
          colors={["__COLOR__", "#10b981", "#f59e0b", "#ec4899"]}
          loading={loading}
        />

        <Card>
          <CardHeader><CardTitle>📋 لیست __NAME_FA__</CardTitle></CardHeader>
          <CardContent>
            <DataTable 
              data={data["__DATA__S"]?.slice(0,5) || []}
              columns={columns}
              searchKeys={["title","name","description"]}
              emptyMessage="هیچ داده‌ای یافت نشد"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>⚡ اقدامات سریع</CardTitle></CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            <Button variant="outline" size="sm"><Plus className="h-4 w-4 ml-1" /> ایجاد جدید</Button>
            <Button variant="outline" size="sm"><Download className="h-4 w-4 ml-1" /> گزارش</Button>
            <Button variant="outline" size="sm"><Filter className="h-4 w-4 ml-1" /> تنظیمات</Button>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
'''

def create_module_page(mod):
    """ایجاد صفحه ماژول با جایگزینی ساده"""
    name_cap = mod["name"].replace(" ", "")
    x_label = {"start":"زمان","day":"روز","name":"نام","x":"مختصات","skill":"مهارت","date":"تاریخ","time":"ساعت"}.get(mod["xKey"], "مقدار")
    
    content = PAGE_TEMPLATE
    content = content.replace("__ICON__", mod["icon"])
    content = content.replace("__NAME_CAP__", name_cap)
    content = content.replace("__NAME_FA__", mod["name"])
    content = content.replace("__DESC__", mod["desc"])
    content = content.replace("__COLOR__", mod["color"])
    content = content.replace("__DATA__", mod["data"])
    content = content.replace("__DATA__S", mod["data"] + "s")
    content = content.replace("__CHART__", mod["chart"])
    content = content.replace("__XKEY__", mod["xKey"])
    content = content.replace("__YKEY__", mod["yKey"])
    content = content.replace("__XLABEL__", x_label)
    return content

def main():
    print("🎨 Econojin Frontend Generator")
    print("=" * 50)
    
    print("\n[1/3] Creating shared components...")
    write_file(WEB / "components" / "ui" / "ChartCard.tsx", CHART_CARD)
    write_file(WEB / "components" / "ui" / "DataTable.tsx", DATA_TABLE)
    write_file(WEB / "components" / "ui" / "AnimatedStatCard.tsx", ANIMATED_STAT)
    print("✅ Shared components created")
    
    print("\n[2/3] Creating module pages...")
    for mod in MODULES:
        page_dir = WEB / "app" / mod["id"]
        write_file(page_dir / "page.tsx", create_module_page(mod))
        # کامپوننت اختصاصی
        comp_dir = page_dir / "components"
        mod_card = f'''"""use client";
import {{ Card, CardContent }} from "@/components/ui/card";
import {{ motion }} from "framer-motion";
export function {mod["name"].replace(" ", "")}Card({{ title, value, icon, color }}) {{
  return (
    <motion.div whileHover={{ y: -4 }} transition={{ type: "spring", stiffness: 300 }}>
      <Card className="card-hover" style={{ borderLeft: "4px solid "+color }}>
        <CardContent className="p-4 flex items-center gap-3">
          <div className="p-2 rounded-lg" style={{ backgroundColor: color+"20" }}>{{icon}}</div>
          <div><p className="text-sm text-slate-400">{{title}}</p><p className="text-xl font-bold" style={{ color }}>{value}</p></div>
        </CardContent>
      </Card>
    </motion.div>
  );
}}
'''
        write_file(comp_dir / "ModuleCard.tsx", mod_card)
    
    print("\n[3/3] Updating sidebar...")
    sidebar = WEB / "components" / "layout" / "sidebar.tsx"
    if sidebar.exists():
        content = sidebar.read_text(encoding="utf-8")
        for mod in MODULES:
            if f'id: "{mod["id"]}"' not in content:
                entry = f'  {{ id: "{mod["id"]}", name: "{mod["name"]}", icon: {mod["icon"]}, href: "/{mod["id"]}" }},'
                if "const modules = [" in content:
                    content = content.replace("const modules = [", f"const modules = [\n{entry}\n  ")
        sidebar.write_text(content, encoding="utf-8")
        print("✅ Sidebar updated")
    
    print("\n" + "=" * 50)
    print(f"✅ Created {len(MODULES)} module pages")
    print("📊 Charts: Recharts | ✨ Animations: Framer Motion")
    print("🎨 Icons: Lucide | 📱 Responsive: Tailwind")
    print(f"\n🚀 Test: http://localhost:3001/{{module-id}}")
    print("=" * 50)
    return 0

if __name__ == "__main__":
    sys.exit(main())