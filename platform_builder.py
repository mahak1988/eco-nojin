#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Econojin Platform Builder v2.0
تکمیل‌کننده‌ی جامع پلتفرم econojin.com

این اسکریپت یک‌جا همه‌ی بخش‌های پلتفرم رو می‌سازه:
  - Backend: accounting, simulator, monitoring routes
  - Frontend: صفحات حسابداری، شبیه‌ساز، پایش
  - Shared components: PageHeader, StatCard, ChartCard, FileUpload

محل اجرا:
  cd D:\\econojin.com
  python platform_builder.py
  python platform_builder.py --force  (برای بازنویسی)
"""

import os
import sys
import platform
import json
from pathlib import Path
from datetime import datetime


class C:
    RESET = "\033[0m"; BOLD = "\033[1m"; RED = "\033[91m"; GREEN = "\033[92m"
    YELLOW = "\033[93m"; CYAN = "\033[96m"; MAGENTA = "\033[95m"; GRAY = "\033[90m"

    @staticmethod
    def enable_windows():
        if platform.system() == "Windows":
            try:
                import ctypes
                ctypes.windll.kernel32.SetConsoleMode(ctypes.windll.kernel32.GetStdHandle(-11), 7)
            except:
                pass


PROJECT = Path(r"D:\econojin.com")
WEB = PROJECT / "apps" / "web"
API = PROJECT / "apps" / "api"


def write_file(path: Path, content: str, force: bool = False) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        print(f"  {C.YELLOW}⚠{C.RESET} رد شد: {path.relative_to(PROJECT)}")
        return False
    path.write_text(content, encoding="utf-8")
    print(f"  {C.GREEN}✓{C.RESET} ایجاد: {path.relative_to(PROJECT)}")
    return True


# ============================================================
#  BACKEND FILES
# ============================================================

BACKEND_FILES = {}

BACKEND_FILES["apps/api/routes/accounting.py"] = '''"""ماژول حسابداری Econojin"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/api/accounting", tags=["accounting"])


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    ECO_REWARD = "eco_reward"
    CARBON_CREDIT = "carbon_credit"


class Transaction(BaseModel):
    id: Optional[str] = None
    type: TransactionType
    amount: float
    currency: str = "ECO"
    description: str
    category: str
    date: datetime
    status: str = "confirmed"


_sample_tx = [
    {"id": "TX001", "type": "eco_reward", "amount": 45.5, "currency": "ECO",
     "description": "مراقبت روزانه - آمازون", "category": "stewardship",
     "date": "2026-07-14T10:00:00", "status": "confirmed"},
    {"id": "TX002", "type": "carbon_credit", "amount": 1200, "currency": "USD",
     "description": "فروش اعتبار کربن", "category": "carbon_sales",
     "date": "2026-07-13T14:00:00", "status": "confirmed"},
    {"id": "TX003", "type": "expense", "amount": 350, "currency": "USD",
     "description": "هزینه ماهواره", "category": "operations",
     "date": "2026-07-12T09:00:00", "status": "confirmed"},
    {"id": "TX004", "type": "income", "amount": 5000, "currency": "USD",
     "description": "سرمایه‌گذاری ESG", "category": "investment",
     "date": "2026-07-11T16:00:00", "status": "confirmed"},
    {"id": "TX005", "type": "transfer", "amount": 100, "currency": "ECO",
     "description": "انتقال به کیف پول", "category": "transfer",
     "date": "2026-07-10T12:00:00", "status": "confirmed"},
]


@router.get("/transactions")
async def list_transactions(limit: int = 50, offset: int = 0, type: Optional[TransactionType] = None):
    result = _sample_tx
    if type:
        result = [t for t in result if t["type"] == type.value]
    return {"transactions": result[offset:offset+limit], "total": len(result)}


@router.get("/transactions/{tx_id}")
async def get_transaction(tx_id: str):
    for t in _sample_tx:
        if t["id"] == tx_id:
            return t
    raise HTTPException(status_code=404, detail="Not found")


@router.post("/transactions")
async def create_transaction(tx: Transaction):
    tx.id = f"TX{len(_sample_tx)+1:03d}"
    _sample_tx.append(tx.dict())
    return {"status": "created", "transaction": tx}


@router.get("/summary")
async def get_summary():
    return {
        "total_income": 6200.0,
        "total_expense": 350.0,
        "net_profit": 5850.0,
        "eco_rewards_distributed": 45.5,
        "carbon_credits_value": 1200.0,
        "transactions_count": len(_sample_tx),
    }


@router.get("/charts/income-expense")
async def get_income_expense_chart():
    return {
        "labels": ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور"],
        "income": [4500, 5200, 4800, 6200, 5800, 6500],
        "expense": [1200, 1100, 1350, 1400, 980, 1100],
        "profit": [3300, 4100, 3450, 4800, 4820, 5400],
    }


@router.get("/charts/category-distribution")
async def get_category_distribution():
    return [
        {"name": "مراقبت", "value": 35, "color": "#22c55e"},
        {"name": "کربن", "value": 25, "color": "#3b82f6"},
        {"name": "سرمایه‌گذاری", "value": 20, "color": "#a855f7"},
        {"name": "عملیات", "value": 12, "color": "#f59e0b"},
        {"name": "انتقال", "value": 8, "color": "#06b6d4"},
    ]


@router.get("/invoices")
async def list_invoices():
    return {"invoices": [
        {"id": "INV001", "number": "INV-2026-001", "client": "شرکت ESG",
         "amount": 5000, "total": 5750, "status": "paid",
         "issue_date": "2026-07-01", "due_date": "2026-07-15"},
        {"id": "INV002", "number": "INV-2026-002", "client": "سازمان محیط‌زیست",
         "amount": 3200, "total": 3680, "status": "pending",
         "issue_date": "2026-07-05", "due_date": "2026-07-20"},
    ]}


@router.get("/reports/download")
async def download_report(format: str = "json"):
    return {"format": format, "generated_at": datetime.now().isoformat()}


@router.post("/upload/statement")
async def upload_statement(file: UploadFile = File(...)):
    return {"status": "uploaded", "filename": file.filename, "size": file.size}


@router.get("/ledger")
async def get_ledger():
    return {"entries": _sample_tx, "balance": 5850.0}
'''

BACKEND_FILES["apps/api/routes/simulator.py"] = '''"""شبیه‌سازهای بوم‌شناختی Econojin"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import math

router = APIRouter(prefix="/api/simulator", tags=["simulator"])


class CarbonSim(BaseModel):
    area_hectares: float
    forest_type: str
    years: int


class WaterSim(BaseModel):
    area_hectares: float
    region: str
    years: int


class BioSim(BaseModel):
    area_hectares: float
    ecosystem_type: str
    restoration_level: float
    years: int


CARBON_RATES = {"rainforest": 25, "temperate": 12, "mangrove": 35, "grassland": 5, "boreal": 8, "agroforestry": 10}
WATER_RATES = {"wetland": 5000, "forest": 2000, "grassland": 800, "agriculture": 300}
BIO_BASELINE = {"rainforest": 0.85, "temperate": 0.65, "wetland": 0.75, "grassland": 0.45, "coral_reef": 0.90}


@router.post("/carbon/run")
async def run_carbon(sim: CarbonSim):
    rate = CARBON_RATES.get(sim.forest_type, 10)
    yearly = []
    cumulative = 0
    for y in range(1, sim.years + 1):
        growth = 1 - math.exp(-y / 3)
        annual = sim.area_hectares * rate * growth
        cumulative += annual
        yearly.append({
            "year": y,
            "annual_sequestration": round(annual, 2),
            "cumulative": round(cumulative, 2),
            "eco_reward": round(annual * 10, 2),
            "carbon_value_usd": round(annual * 30, 2),
        })
    return {
        "total_sequestration": round(cumulative, 2),
        "total_eco_reward": round(cumulative * 10, 2),
        "total_value_usd": round(cumulative * 30, 2),
        "yearly_data": yearly,
        "chart_data": {
            "labels": [f"سال {y['year']}" for y in yearly],
            "annual": [y["annual_sequestration"] for y in yearly],
            "cumulative": [y["cumulative"] for y in yearly],
        },
    }


@router.post("/water/run")
async def run_water(sim: WaterSim):
    rate = WATER_RATES.get(sim.region.lower(), 1000)
    yearly = []
    for y in range(1, sim.years + 1):
        retention = sim.area_hectares * rate * (0.8 + 0.2 * min(y / 5, 1))
        yearly.append({
            "year": y,
            "water_retained_m3": round(retention, 2),
            "water_quality_index": round(min(95, 60 + y * 5), 1),
        })
    return {
        "total_water_m3": round(sum(y["water_retained_m3"] for y in yearly), 2),
        "yearly_data": yearly,
        "chart_data": {
            "labels": [f"سال {y['year']}" for y in yearly],
            "retention": [y["water_retained_m3"] for y in yearly],
        },
    }


@router.post("/biodiversity/run")
async def run_biodiversity(sim: BioSim):
    baseline = BIO_BASELINE.get(sim.ecosystem_type, 0.5)
    target = baseline + (1 - baseline) * sim.restoration_level
    yearly = []
    for y in range(1, sim.years + 1):
        current = baseline + (target - baseline) * (1 - math.exp(-y / 3))
        species = int(sim.area_hectares * current * 50)
        yearly.append({
            "year": y,
            "biodiversity_index": round(current, 3),
            "estimated_species": species,
            "eco_reward": round((current - baseline) * sim.area_hectares * 20, 2),
        })
    return {
        "baseline_index": baseline,
        "final_index": round(yearly[-1]["biodiversity_index"], 3) if yearly else baseline,
        "yearly_data": yearly,
        "chart_data": {
            "labels": [f"سال {y['year']}" for y in yearly],
            "biodiversity": [y["biodiversity_index"] for y in yearly],
            "species": [y["estimated_species"] for y in yearly],
        },
    }


@router.get("/forest-types")
async def get_forest_types():
    return [
        {"value": "rainforest", "label": "جنگل بارانی", "rate": 25, "icon": "🌴"},
        {"value": "temperate", "label": "جنگل معتدل", "rate": 12, "icon": "🌳"},
        {"value": "mangrove", "label": "جنگل حرا", "rate": 35, "icon": "🌊"},
        {"value": "grassland", "label": "مرتع", "rate": 5, "icon": "🌾"},
        {"value": "boreal", "label": "جنگل شمالی", "rate": 8, "icon": "🌲"},
        {"value": "agroforestry", "label": "آگروفارستری", "rate": 10, "icon": "🌱"},
    ]


@router.get("/ecosystem-types")
async def get_ecosystem_types():
    return [
        {"value": "rainforest", "label": "جنگل بارانی", "baseline": 0.85, "icon": "🌴"},
        {"value": "temperate", "label": "جنگل معتدل", "baseline": 0.65, "icon": "🌳"},
        {"value": "wetland", "label": "تالاب", "baseline": 0.75, "icon": "🦆"},
        {"value": "grassland", "label": "مرتع", "baseline": 0.45, "icon": "🌾"},
        {"value": "coral_reef", "label": "صخره مرجانی", "baseline": 0.90, "icon": "🪸"},
    ]
'''

BACKEND_FILES["apps/api/routes/monitoring.py"] = '''"""پایش ماهواره‌ای و AI Econojin"""
from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import math

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


class SatRequest(BaseModel):
    project_id: str
    lat: float
    lng: float
    area_hectares: float
    start_date: str
    end_date: str


class AIRequest(BaseModel):
    project_id: str
    data_type: str
    timeframe: str


_sample_data = [
    {"date": "2026-07-01", "ndvi": 0.65, "ndwi": 0.42, "biomass": 120},
    {"date": "2026-07-05", "ndvi": 0.67, "ndwi": 0.44, "biomass": 122},
    {"date": "2026-07-10", "ndvi": 0.69, "ndwi": 0.46, "biomass": 125},
    {"date": "2026-07-15", "ndvi": 0.71, "ndwi": 0.48, "biomass": 128},
]


@router.post("/satellite/analyze")
async def analyze_satellite(req: SatRequest):
    ndvi = [d["ndvi"] for d in _sample_data]
    avg = sum(ndvi) / len(ndvi)
    trend = ndvi[-1] - ndvi[0]
    return {
        "indices": {
            "ndvi": {"avg": round(avg, 3), "trend": round(trend, 3), "status": "improving" if trend > 0 else "declining"},
            "ndwi": {"avg": 0.45, "trend": 0.02, "status": "stable"},
            "evi": {"avg": 0.58, "trend": 0.01, "status": "improving"},
        },
        "biomass_estimate": {"total_tons": round(req.area_hectares * 125, 2), "per_hectare": 125},
        "health_score": 85,
        "time_series": _sample_data,
        "chart_data": {
            "labels": [d["date"] for d in _sample_data],
            "ndvi": [d["ndvi"] for d in _sample_data],
            "ndwi": [d["ndwi"] for d in _sample_data],
            "biomass": [d["biomass"] for d in _sample_data],
        },
    }


@router.post("/satellite/upload")
async def upload_satellite(file: UploadFile = File(...)):
    return {"status": "uploaded", "filename": file.filename, "analysis_started": True}


@router.post("/ai/analyze")
async def ai_analyze(req: AIRequest):
    return {
        "summary": "وضعیت بوم‌شناختی در حال بهبود است. NDVI 3.2٪ افزایش.",
        "insights": [
            {"type": "positive", "message": "افزایش پوشش گیاهی در ۸۵٪ منطقه", "confidence": 0.92},
            {"type": "warning", "message": "کاهش رطوبت در بخش شمالی", "confidence": 0.78},
        ],
        "predictions": [
            {"metric": "biomass", "next_30d": "+2.5%", "confidence": 0.85},
            {"metric": "biodiversity", "next_90d": "+5.1%", "confidence": 0.79},
        ],
        "recommendations": [
            "افزایش نظارت در بخش شمالی",
            "کاشت گونه‌های مقاوم به خشکی",
        ],
    }


@router.get("/ai/models")
async def get_ai_models():
    return [
        {"id": "biomass", "name": "برآورد زیست‌توده", "accuracy": 0.92},
        {"id": "species", "name": "تشخیص گونه", "accuracy": 0.88},
        {"id": "deforestation", "name": "تشخیص جنگل‌زدایی", "accuracy": 0.95},
        {"id": "carbon", "name": "پیش‌بینی کربن", "accuracy": 0.87},
    ]


@router.get("/alerts")
async def get_alerts():
    return {"alerts": [
        {"id": "AL001", "type": "deforestation", "severity": "high",
         "message": "کاهش پوشش در ۵ هکتار", "timestamp": "2026-07-14T08:00:00"},
        {"id": "AL002", "type": "moisture", "severity": "medium",
         "message": "کاهش رطوبت خاک", "timestamp": "2026-07-14T06:00:00"},
    ]}


@router.get("/projects/overview")
async def get_projects_overview():
    return {"projects": [
        {"id": "amazon-north", "name": "آمازون شمالی", "hectares": 45200, "ndvi": 0.72, "health": 88},
        {"id": "kenya-grassland", "name": "مراتع کنیا", "hectares": 28900, "ndvi": 0.58, "health": 75},
        {"id": "indonesia-mangrove", "name": "حرای اندونزی", "hectares": 18700, "ndvi": 0.81, "health": 92},
    ]}
'''


# ============================================================
#  FRONTEND SHARED COMPONENTS
# ============================================================

FRONTEND_COMPONENTS = {}

FRONTEND_COMPONENTS["components/shared/PageHeader.tsx"] = """'use client'
import { motion } from 'framer-motion'
import { LucideIcon } from 'lucide-react'

export function PageHeader({ title, description, icon: Icon, color = 'text-green-500' }: {
  title: string; description?: string; icon: LucideIcon; color?: string
}) {
  return (
    <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className='mb-8'>
      <div className='flex items-center gap-4'>
        <motion.div whileHover={{ scale: 1.1, rotate: 5 }} className='w-14 h-14 rounded-2xl bg-gradient-to-br from-green-500/10 to-emerald-500/10 flex items-center justify-center'>
          <Icon className={`w-7 h-7 ${color}`} />
        </motion.div>
        <div>
          <h1 className='text-3xl font-bold'>{title}</h1>
          {description && <p className='text-muted-foreground mt-1'>{description}</p>}
        </div>
      </div>
    </motion.div>
  )
}
"""

FRONTEND_COMPONENTS["components/shared/StatCard.tsx"] = """'use client'
import { motion } from 'framer-motion'
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react'
import { Card } from '@/components/ui/card'

export function StatCard({ label, value, icon: Icon, color = 'text-green-500', bgColor = 'bg-green-500/10', trend, delay = 0 }: {
  label: string; value: string | number; icon: LucideIcon; color?: string; bgColor?: string; trend?: number; delay?: number
}) {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay }} whileHover={{ y: -4 }}>
      <Card className='overflow-hidden'>
        <div className='p-6'>
          <div className='flex items-start justify-between mb-4'>
            <div className={`w-12 h-12 rounded-xl ${bgColor} flex items-center justify-center`}>
              <Icon className={`w-6 h-6 ${color}`} />
            </div>
            {trend !== undefined && (
              <div className={`flex items-center gap-1 text-sm font-medium ${trend >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                {trend >= 0 ? <TrendingUp className='w-4 h-4' /> : <TrendingDown className='w-4 h-4' />}
                {Math.abs(trend)}%
              </div>
            )}
          </div>
          <div className='text-2xl font-bold'>{value}</div>
          <div className='text-sm text-muted-foreground mt-1'>{label}</div>
        </div>
      </Card>
    </motion.div>
  )
}
"""

FRONTEND_COMPONENTS["components/shared/ChartCard.tsx"] = """'use client'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { LucideIcon } from 'lucide-react'
import { ReactNode } from 'react'

export function ChartCard({ title, icon: Icon, iconColor = 'text-green-500', children, delay = 0, action }: {
  title: string; icon: LucideIcon; iconColor?: string; children: ReactNode; delay?: number; action?: ReactNode
}) {
  return (
    <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.4, delay }}>
      <Card>
        <CardHeader className='flex flex-row items-center justify-between'>
          <CardTitle className='flex items-center gap-2 text-lg'>
            <Icon className={`w-5 h-5 ${iconColor}`} />
            {title}
          </CardTitle>
          {action}
        </CardHeader>
        <CardContent>{children}</CardContent>
      </Card>
    </motion.div>
  )
}
"""

FRONTEND_COMPONENTS["components/shared/FileUpload.tsx"] = """'use client'
import { UploadCloud, File as FileIcon, X } from 'lucide-react'
import { useState, useRef } from 'react'
import { Button } from '@/components/ui/button'

export function FileUpload({ accept = '*', maxSize = 10, onUpload, label = 'آپلود فایل' }: {
  accept?: string; maxSize?: number; onUpload: (file: File) => Promise<void>; label?: string
}) {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = (f: File) => {
    if (f.size > maxSize * 1024 * 1024) return
    setFile(f)
  }

  const handleUpload = async () => {
    if (!file) return
    setLoading(true)
    try { await onUpload(file); setFile(null) } finally { setLoading(false) }
  }

  return (
    <div className='space-y-3'>
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]) }}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${dragOver ? 'border-green-500 bg-green-500/5' : 'border-border hover:border-green-500/50'}`}
      >
        <UploadCloud className='w-10 h-10 mx-auto mb-3 text-green-500' />
        <p className='text-sm font-medium'>{label}</p>
        <p className='text-xs text-muted-foreground mt-1'>حداکثر {maxSize}MB</p>
        <input ref={inputRef} type='file' accept={accept} className='hidden' onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])} />
      </div>
      {file && (
        <div className='flex items-center justify-between p-3 rounded-lg border border-border bg-muted/30'>
          <div className='flex items-center gap-2'>
            <FileIcon className='w-5 h-5 text-green-500' />
            <div><div className='text-sm font-medium'>{file.name}</div><div className='text-xs text-muted-foreground'>{(file.size / 1024).toFixed(1)} KB</div></div>
          </div>
          <div className='flex gap-2'>
            <Button size='sm' onClick={handleUpload} disabled={loading}>{loading ? 'در حال آپلود...' : 'آپلود'}</Button>
            <Button size='sm' variant='ghost' onClick={() => setFile(null)}><X className='w-4 h-4' /></Button>
          </div>
        </div>
      )}
    </div>
  )
}
"""


# ============================================================
#  FRONTEND PAGES
# ============================================================

FRONTEND_PAGES = {}

FRONTEND_PAGES["app/accounting/page.tsx"] = """'use client'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Wallet, TrendingUp, TrendingDown, Receipt, DollarSign, FileText, Download } from 'lucide-react'
import { AreaChart, Area, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { PageHeader } from '@/components/shared/PageHeader'
import { StatCard } from '@/components/shared/StatCard'
import { ChartCard } from '@/components/shared/ChartCard'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

export default function AccountingDashboard() {
  const [summary, setSummary] = useState<any>(null)
  const [chart, setChart] = useState<any>(null)
  const [cats, setCats] = useState<any[]>([])
  const [txs, setTxs] = useState<any[]>([])

  useEffect(() => {
    fetch('/api/accounting/summary').then(r => r.json()).then(setSummary)
    fetch('/api/accounting/charts/income-expense').then(r => r.json()).then(setChart)
    fetch('/api/accounting/charts/category-distribution').then(r => r.json()).then(setCats)
    fetch('/api/accounting/transactions?limit=5').then(r => r.json()).then(d => setTxs(d.transactions || []))
  }, [])

  const data = chart ? chart.labels.map((l: string, i: number) => ({
    name: l, 'درآمد': chart.income[i], 'هزینه': chart.expense[i], 'سود': chart.profit[i]
  })) : []

  const typeColors: Record<string, string> = { income: 'text-green-600', expense: 'text-red-600', transfer: 'text-blue-600', eco_reward: 'text-purple-600', carbon_credit: 'text-orange-600' }
  const typeLabels: Record<string, string> = { income: 'درآمد', expense: 'هزینه', transfer: 'انتقال', eco_reward: 'پاداش ECO', carbon_credit: 'اعتبار کربن' }

  return (
    <div className='container mx-auto px-4 py-8'>
      <PageHeader title='حسابداری' description='مدیریت مالی و گزارش‌گیری Econojin' icon={Wallet} />
      <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8'>
        <StatCard label='کل درآمد' value={summary ? `$${summary.total_income.toLocaleString()}` : '...'} icon={TrendingUp} color='text-green-500' bgColor='bg-green-500/10' trend={12.5} delay={0} />
        <StatCard label='کل هزینه' value={summary ? `$${summary.total_expense.toLocaleString()}` : '...'} icon={TrendingDown} color='text-red-500' bgColor='bg-red-500/10' trend={-5.2} delay={0.1} />
        <StatCard label='سود خالص' value={summary ? `$${summary.net_profit.toLocaleString()}` : '...'} icon={DollarSign} color='text-blue-500' bgColor='bg-blue-500/10' trend={18.3} delay={0.2} />
        <StatCard label='پاداش ECO' value={summary ? `${summary.eco_rewards_distributed} ECO` : '...'} icon={Receipt} color='text-purple-500' bgColor='bg-purple-500/10' trend={8.7} delay={0.3} />
      </div>
      <div className='grid lg:grid-cols-2 gap-6 mb-8'>
        <ChartCard title='درآمد و هزینه' icon={TrendingUp} delay={0.4}>
          <ResponsiveContainer width='100%' height={300}>
            <AreaChart data={data}>
              <defs>
                <linearGradient id='g1' x1='0' y1='0' x2='0' y2='1'><stop offset='5%' stopColor='#22c55e' stopOpacity={0.8} /><stop offset='95%' stopColor='#22c55e' stopOpacity={0} /></linearGradient>
                <linearGradient id='g2' x1='0' y1='0' x2='0' y2='1'><stop offset='5%' stopColor='#ef4444' stopOpacity={0.6} /><stop offset='95%' stopColor='#ef4444' stopOpacity={0} /></linearGradient>
              </defs>
              <CartesianGrid strokeDasharray='3 3' stroke='#e5e7eb' />
              <XAxis dataKey='name' tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ fontSize: '12px', borderRadius: '8px' }} />
              <Legend wrapperStyle={{ fontSize: '12px' }} />
              <Area type='monotone' dataKey='درآمد' stroke='#22c55e' fill='url(#g1)' strokeWidth={2} />
              <Area type='monotone' dataKey='هزینه' stroke='#ef4444' fill='url(#g2)' strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title='توزیع دسته‌بندی' icon={FileText} delay={0.5}>
          <ResponsiveContainer width='100%' height={300}>
            <PieChart>
              <Pie data={cats} dataKey='value' nameKey='name' cx='50%' cy='50%' outerRadius={100} innerRadius={60} label={(e) => `${e.value}%`}>
                {cats.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Pie>
              <Tooltip contentStyle={{ fontSize: '12px', borderRadius: '8px' }} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
      <Card>
        <CardHeader className='flex flex-row items-center justify-between'>
          <CardTitle className='flex items-center gap-2'><Receipt className='w-5 h-5 text-green-500' /> تراکنش‌های اخیر</CardTitle>
          <Button variant='outline' size='sm'><Download className='w-4 h-4 ml-2' /> خروجی</Button>
        </CardHeader>
        <CardContent>
          <div className='overflow-x-auto'>
            <table className='w-full text-sm'>
              <thead className='bg-muted/50 text-xs text-muted-foreground'>
                <tr><th className='p-3 text-right'>شناسه</th><th className='p-3 text-right'>نوع</th><th className='p-3 text-right'>توضیحات</th><th className='p-3 text-right'>مبلغ</th><th className='p-3 text-right'>تاریخ</th></tr>
              </thead>
              <tbody>
                {txs.map((tx, i) => (
                  <motion.tr key={tx.id} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }} className='border-t border-border hover:bg-muted/20'>
                    <td className='p-3 font-mono text-xs'>{tx.id}</td>
                    <td className='p-3'><Badge variant='outline' className={typeColors[tx.type] || ''}>{typeLabels[tx.type] || tx.type}</Badge></td>
                    <td className='p-3'>{tx.description}</td>
                    <td className={`p-3 font-bold ${tx.type === 'expense' ? 'text-red-600' : 'text-green-600'}`}>{tx.type === 'expense' ? '-' : '+'}{tx.amount.toLocaleString()} {tx.currency}</td>
                    <td className='p-3 text-xs text-muted-foreground'>{new Date(tx.date).toLocaleDateString('fa-IR')}</td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
"""

FRONTEND_PAGES["app/accounting/transactions/page.tsx"] = """'use client'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Receipt, Search, Filter, Download, Plus } from 'lucide-react'
import { PageHeader } from '@/components/shared/PageHeader'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'

export default function TransactionsPage() {
  const [txs, setTxs] = useState([])
  const [search, setSearch] = useState('')

  useEffect(() => {
    fetch('/api/accounting/transactions?limit=50').then(r => r.json()).then(d => setTxs(d.transactions || []))
  }, [])

  const filtered = txs.filter((t: any) => t.description.includes(search) || t.id.includes(search))

  return (
    <div className='container mx-auto px-4 py-8'>
      <PageHeader title='تراکنش‌ها' description='مدیریت کامل تراکنش‌های مالی' icon={Receipt} />
      <Card className='mb-6'><CardContent className='p-4'>
        <div className='flex flex-wrap gap-3'>
          <div className='relative flex-1 min-w-[200px]'>
            <Search className='absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground' />
            <Input placeholder='جستجو...' value={search} onChange={e => setSearch(e.target.value)} className='pr-10' />
          </div>
          <Button variant='outline'><Filter className='w-4 h-4 ml-2' /> فیلتر</Button>
          <Button variant='outline'><Download className='w-4 h-4 ml-2' /> خروجی</Button>
          <Button className='bg-green-600 hover:bg-green-700'><Plus className='w-4 h-4 ml-2' /> تراکنش جدید</Button>
        </div>
      </CardContent></Card>
      <Card><CardContent className='p-0'>
        <div className='overflow-x-auto'>
          <table className='w-full text-sm'>
            <thead className='bg-muted/50 text-xs text-muted-foreground'>
              <tr><th className='p-3 text-right'>شناسه</th><th className='p-3 text-right'>نوع</th><th className='p-3 text-right'>توضیحات</th><th className='p-3 text-right'>مبلغ</th><th className='p-3 text-right'>تاریخ</th><th className='p-3 text-right'>وضعیت</th></tr>
            </thead>
            <tbody>
              {filtered.map((tx: any, i: number) => (
                <motion.tr key={tx.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.03 }} className='border-t border-border hover:bg-muted/20'>
                  <td className='p-3 font-mono text-xs'>{tx.id}</td>
                  <td className='p-3'><Badge variant='outline'>{tx.type}</Badge></td>
                  <td className='p-3'>{tx.description}</td>
                  <td className={`p-3 font-bold ${tx.type === 'expense' ? 'text-red-600' : 'text-green-600'}`}>{tx.type === 'expense' ? '-' : '+'}{tx.amount.toLocaleString()} {tx.currency}</td>
                  <td className='p-3 text-xs text-muted-foreground'>{new Date(tx.date).toLocaleDateString('fa-IR')}</td>
                  <td className='p-3'><Badge variant='outline' className='text-green-600'>{tx.status}</Badge></td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent></Card>
    </div>
  )
}
"""

FRONTEND_PAGES["app/accounting/invoices/page.tsx"] = """'use client'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { FileText, Plus, Download, Eye } from 'lucide-react'
import { PageHeader } from '@/components/shared/PageHeader'
import { StatCard } from '@/components/shared/StatCard'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState([])
  useEffect(() => { fetch('/api/accounting/invoices').then(r => r.json()).then(d => setInvoices(d.invoices || [])) }, [])

  const paid = invoices.filter((i: any) => i.status === 'paid').reduce((s: number, i: any) => s + i.total, 0)
  const pending = invoices.filter((i: any) => i.status === 'pending').reduce((s: number, i: any) => s + i.total, 0)

  return (
    <div className='container mx-auto px-4 py-8'>
      <PageHeader title='فاکتورها' description='مدیریت فاکتورها و پرداخت‌ها' icon={FileText} />
      <div className='grid grid-cols-1 md:grid-cols-3 gap-4 mb-8'>
        <StatCard label='کل فاکتورها' value={invoices.length} icon={FileText} color='text-blue-500' bgColor='bg-blue-500/10' delay={0} />
        <StatCard label='پرداخت‌شده' value={`$${paid.toLocaleString()}`} icon={Download} color='text-green-500' bgColor='bg-green-500/10' delay={0.1} />
        <StatCard label='در انتظار' value={`$${pending.toLocaleString()}`} icon={Eye} color='text-yellow-500' bgColor='bg-yellow-500/10' delay={0.2} />
      </div>
      <div className='flex justify-end mb-4'><Button className='bg-green-600 hover:bg-green-700'><Plus className='w-4 h-4 ml-2' /> فاکتور جدید</Button></div>
      <Card>
        <CardHeader><CardTitle>لیست فاکتورها</CardTitle></CardHeader>
        <CardContent>
          <div className='overflow-x-auto'>
            <table className='w-full text-sm'>
              <thead className='bg-muted/50 text-xs text-muted-foreground'>
                <tr><th className='p-3 text-right'>شماره</th><th className='p-3 text-right'>مشتری</th><th className='p-3 text-right'>کل</th><th className='p-3 text-right'>وضعیت</th><th className='p-3 text-right'>سررسید</th><th className='p-3 text-right'>عملیات</th></tr>
              </thead>
              <tbody>
                {invoices.map((inv: any, i: number) => (
                  <motion.tr key={inv.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.05 }} className='border-t border-border hover:bg-muted/20'>
                    <td className='p-3 font-mono text-xs'>{inv.number}</td>
                    <td className='p-3 font-medium'>{inv.client}</td>
                    <td className='p-3 font-bold'>${inv.total.toLocaleString()}</td>
                    <td className='p-3'><Badge variant='outline' className={inv.status === 'paid' ? 'text-green-600 border-green-500/30' : 'text-yellow-600 border-yellow-500/30'}>{inv.status === 'paid' ? '✓ پرداخت‌شده' : '⏳ در انتظار'}</Badge></td>
                    <td className='p-3 text-xs text-muted-foreground'>{new Date(inv.due_date).toLocaleDateString('fa-IR')}</td>
                    <td className='p-3'><div className='flex gap-1'><Button size='sm' variant='ghost'><Eye className='w-4 h-4' /></Button><Button size='sm' variant='ghost'><Download className='w-4 h-4' /></Button></div></td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
"""

FRONTEND_PAGES["app/simulator/page.tsx"] = """'use client'
import { motion } from 'framer-motion'
import { Leaf, Droplets, Bird, Satellite, Brain } from 'lucide-react'
import { PageHeader } from '@/components/shared/PageHeader'
import { Card, CardContent } from '@/components/ui/card'

const sims = [
  { title: 'شبیه‌ساز کربن', desc: 'محاسبه جذب CO₂ و پاداش ECO', icon: Leaf, color: 'from-green-500 to-emerald-600', href: '/simulator/carbon' },
  { title: 'شبیه‌ساز آب', desc: 'محاسبه ذخیره و کیفیت آب', icon: Droplets, color: 'from-blue-500 to-cyan-600', href: '/simulator/water' },
  { title: 'شبیه‌ساز تنوع زیستی', desc: 'برآورد گونه‌ها و شاخص تنوع', icon: Bird, color: 'from-purple-500 to-pink-600', href: '/simulator/biodiversity' },
  { title: 'پایش ماهواره‌ای', desc: 'تحلیل NDVI/NDWI از Sentinel-2', icon: Satellite, color: 'from-orange-500 to-red-600', href: '/monitoring/satellite' },
  { title: 'تحلیل هوش مصنوعی', desc: 'پیش‌بینی و تشخیص با ML', icon: Brain, color: 'from-indigo-500 to-purple-600', href: '/monitoring/ai' },
]

export default function SimulatorDashboard() {
  return (
    <div className='container mx-auto px-4 py-8'>
      <PageHeader title='شبیه‌سازها' description='ابزارهای شبیه‌سازی و پایش بوم‌شناختی' icon={Leaf} />
      <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'>
        {sims.map((sim, i) => {
          const Icon = sim.icon
          return (
            <motion.div key={i} initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }} whileHover={{ y: -8, scale: 1.02 }}>
              <a href={sim.href}>
                <Card className='overflow-hidden cursor-pointer h-full'>
                  <div className={`h-32 bg-gradient-to-br ${sim.color} flex items-center justify-center'><Icon className='w-16 h-16 text-white' /></div>
                  <CardContent className='p-6'>
                    <h3 className='text-xl font-bold mb-2'>{sim.title}</h3>
                    <p className='text-sm text-muted-foreground'>{sim.desc}</p>
                    <div className='mt-4 text-green-600 text-sm font-medium'>شروع شبیه‌سازی ←</div>
                  </CardContent>
                </Card>
              </a>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
"""

FRONTEND_PAGES["app/simulator/carbon/page.tsx"] = """'use client'
import { useState } from 'react'
import { motion } from 'framer-motion'
import { Leaf, Play, Download, TrendingUp } from 'lucide-react'
import { AreaChart, Area, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { PageHeader } from '@/components/shared/PageHeader'
import { StatCard } from '@/components/shared/StatCard'
import { ChartCard } from '@/components/shared/ChartCard'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

export default function CarbonSimulator() {
  const [params, setParams] = useState({ area_hectares: 100, forest_type: 'rainforest', years: 10 })
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const run = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/simulator/carbon/run', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(params) })
      setResult(await res.json())
    } finally { setLoading(false) }
  }

  const chartData = result?.chart_data?.labels?.map((label: string, i: number) => ({
    name: label, 'جذب سالانه': result.chart_data.annual[i], 'تجمعی': result.chart_data.cumulative[i]
  })) || []

  return (
    <div className='container mx-auto px-4 py-8'>
      <PageHeader title='شبیه‌ساز کربن' description='محاسبه جذب CO₂ و پاداش ECO' icon={Leaf} color='text-green-500' />
      <div className='grid lg:grid-cols-3 gap-6 mb-8'>
        <Card className='lg:col-span-1'>
          <CardHeader><CardTitle>پارامترها</CardTitle></CardHeader>
          <CardContent className='space-y-4'>
            <div className='space-y-2'><Label>مساحت (هکتار)</Label><Input type='number' value={params.area_hectares} onChange={e => setParams({ ...params, area_hectares: +e.target.value })} /></div>
            <div className='space-y-2'><Label>نوع جنگل</Label>
              <Select value={params.forest_type} onValueChange={v => setParams({ ...params, forest_type: v })}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value='rainforest'>🌴 جنگل بارانی</SelectItem>
                  <SelectItem value='temperate'>🌳 جنگل معتدل</SelectItem>
                  <SelectItem value='mangrove'>🌊 جنگل حرا</SelectItem>
                  <SelectItem value='grassland'>🌾 مرتع</SelectItem>
                  <SelectItem value='boreal'>🌲 جنگل شمالی</SelectItem>
                  <SelectItem value='agroforestry'>🌱 آگروفارستری</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className='space-y-2'><Label>مدت زمان (سال)</Label><Input type='number' value={params.years} onChange={e => setParams({ ...params, years: +e.target.value })} /></div>
            <Button className='w-full bg-green-600 hover:bg-green-700' onClick={run} disabled={loading}><Play className='w-4 h-4 ml-2' />{loading ? 'در حال اجرا...' : 'اجرای شبیه‌سازی'}</Button>
          </CardContent>
        </Card>
        <div className='lg:col-span-2 space-y-6'>
          {result ? (
            <>
              <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
                <StatCard label='کل جذب CO₂' value={`${result.total_sequestration.toLocaleString()} تن`} icon={Leaf} color='text-green-500' bgColor='bg-green-500/10' delay={0} />
                <StatCard label='پاداش ECO' value={`${result.total_eco_reward.toLocaleString()} ECO`} icon={TrendingUp} color='text-purple-500' bgColor='bg-purple-500/10' delay={0.1} />
                <StatCard label='ارزش USD' value={`$${result.total_value_usd.toLocaleString()}`} icon={Download} color='text-blue-500' bgColor='bg-blue-500/10' delay={0.2} />
              </div>
              <ChartCard title='جذب کربن در طول زمان' icon={TrendingUp}>
                <ResponsiveContainer width='100%' height={350}>
                  <AreaChart data={chartData}>
                    <defs><linearGradient id='cg' x1='0' y1='0' x2='0' y2='1'><stop offset='5%' stopColor='#22c55e' stopOpacity={0.8} /><stop offset='95%' stopColor='#22c55e' stopOpacity={0} /></linearGradient></defs>
                    <CartesianGrid strokeDasharray='3 3' stroke='#e5e7eb' />
                    <XAxis dataKey='name' tick={{ fontSize: 11 }} /><YAxis tick={{ fontSize: 11 }} />
                    <Tooltip contentStyle={{ fontSize: '12px', borderRadius: '8px' }} /><Legend wrapperStyle={{ fontSize: '12px' }} />
                    <Area type='monotone' dataKey='جذب سالانه' stroke='#22c55e' fill='url(#cg)' strokeWidth={2} />
                    <Line type='monotone' dataKey='تجمعی' stroke='#3b82f6' strokeWidth={2} dot={false} />
                  </AreaChart>
                </ResponsiveContainer>
              </ChartCard>
              <Card>
                <CardHeader><CardTitle>جزئیات سالانه</CardTitle></CardHeader>
                <CardContent>
                  <div className='overflow-x-auto max-h-80 overflow-y-auto'>
                    <table className='w-full text-sm'>
                      <thead className='bg-muted/50 text-xs text-muted-foreground sticky top-0'>
                        <tr><th className='p-2 text-right'>سال</th><th className='p-2 text-right'>جذب سالانه</th><th className='p-2 text-right'>تجمعی</th><th className='p-2 text-right'>پاداش</th><th className='p-2 text-right'>USD</th></tr>
                      </thead>
                      <tbody>
                        {result.yearly_data.map((y: any, i: number) => (
                          <motion.tr key={i} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.03 }} className='border-t border-border'>
                            <td className='p-2'>{y.year}</td><td className='p-2 font-bold text-green-600'>{y.annual_sequestration.toLocaleString()} تن</td>
                            <td className='p-2'>{y.cumulative.toLocaleString()} تن</td><td className='p-2 text-purple-600'>{y.eco_reward.toLocaleString()}</td><td className='p-2 text-blue-600'>${y.carbon_value_usd.toLocaleString()}</td>
                          </motion.tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card className='flex items-center justify-center min-h-[400px]'><CardContent className='text-center'><Leaf className='w-16 h-16 mx-auto mb-4 text-green-500 opacity-50' /><p className='text-muted-foreground'>پارامترها را تنظیم و شبیه‌سازی را اجرا کنید</p></CardContent></Card>
          )}
        </div>
      </div>
    </div>
  )
}
"""

FRONTEND_PAGES["app/monitoring/satellite/page.tsx"] = """'use client'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Satellite, MapPin, Activity, AlertTriangle } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { PageHeader } from '@/components/shared/PageHeader'
import { StatCard } from '@/components/shared/StatCard'
import { ChartCard } from '@/components/shared/ChartCard'
import { FileUpload } from '@/components/shared/FileUpload'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

export default function SatelliteMonitoring() {
  const [params, setParams] = useState({ project_id: 'amazon-north', lat: -3.4653, lng: -62.2159, area_hectares: 1000, start_date: '2026-06-01', end_date: '2026-07-14' })
  const [result, setResult] = useState<any>(null)
  const [alerts, setAlerts] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  const analyze = async () => {
    setLoading(true)
    try { const res = await fetch('/api/monitoring/satellite/analyze', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(params) }); setResult(await res.json()) } finally { setLoading(false) }
  }

  useEffect(() => { fetch('/api/monitoring/alerts').then(r => r.json()).then(d => setAlerts(d.alerts || [])) }, [])

  const chartData = result?.chart_data?.labels?.map((label: string, i: number) => ({
    name: label, NDVI: result.chart_data.ndvi[i], NDWI: result.chart_data.ndwi[i], 'زیست‌توده': result.chart_data.biomass[i]
  })) || []

  return (
    <div className='container mx-auto px-4 py-8'>
      <PageHeader title='پایش ماهواره‌ای' description='تحلیل داده‌های Sentinel-2 و Landsat' icon={Satellite} color='text-orange-500' />
      {alerts.length > 0 && (
        <Card className='mb-6 border-red-500/30'>
          <CardHeader><CardTitle className='flex items-center gap-2 text-red-600'><AlertTriangle className='w-5 h-5' /> هشدارهای فعال ({alerts.length})</CardTitle></CardHeader>
          <CardContent className='space-y-2'>
            {alerts.map((a, i) => (
              <motion.div key={i} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }} className='flex items-center justify-between p-3 rounded-lg border border-border'>
                <div className='flex items-center gap-3'>
                  <Badge variant='outline' className={a.severity === 'high' ? 'text-red-600 border-red-500/30' : 'text-yellow-600 border-yellow-500/30'}>{a.severity === 'high' ? '🔴 بحرانی' : '🟡 متوسط'}</Badge>
                  <div><div className='text-sm font-medium'>{a.message}</div><div className='text-xs text-muted-foreground'>{a.type}</div></div>
                </div>
              </motion.div>
            ))}
          </CardContent>
        </Card>
      )}
      <div className='grid lg:grid-cols-3 gap-6'>
        <Card>
          <CardHeader><CardTitle className='flex items-center gap-2'><MapPin className='w-5 h-5' /> پارامترها</CardTitle></CardHeader>
          <CardContent className='space-y-4'>
            <div className='space-y-2'><Label>شناسه پروژه</Label><Input value={params.project_id} onChange={e => setParams({ ...params, project_id: e.target.value })} /></div>
            <div className='grid grid-cols-2 gap-2'>
              <div className='space-y-2'><Label>عرض جغرافیایی</Label><Input type='number' step='0.0001' value={params.lat} onChange={e => setParams({ ...params, lat: +e.target.value })} /></div>
              <div className='space-y-2'><Label>طول جغرافیایی</Label><Input type='number' step='0.0001' value={params.lng} onChange={e => setParams({ ...params, lng: +e.target.value })} /></div>
            </div>
            <div className='space-y-2'><Label>مساحت (هکتار)</Label><Input type='number' value={params.area_hectares} onChange={e => setParams({ ...params, area_hectares: +e.target.value })} /></div>
            <Button className='w-full bg-orange-600 hover:bg-orange-700' onClick={analyze} disabled={loading}><Satellite className='w-4 h-4 ml-2' />{loading ? 'در حال تحلیل...' : 'تحلیل ماهواره‌ای'}</Button>
          </CardContent>
        </Card>
        <div className='lg:col-span-2 space-y-6'>
          {result && (
            <>
              <div className='grid grid-cols-2 md:grid-cols-4 gap-4'>
                <StatCard label='NDVI' value={result.indices.ndvi.avg} icon={Activity} color='text-green-500' bgColor='bg-green-500/10' delay={0} />
                <StatCard label='NDWI' value={result.indices.ndwi.avg} icon={Activity} color='text-blue-500' bgColor='bg-blue-500/10' delay={0.1} />
                <StatCard label='زیست‌توده (تن)' value={result.biomass_estimate.total_tons.toLocaleString()} icon={Activity} color='text-purple-500' bgColor='bg-purple-500/10' delay={0.2} />
                <StatCard label='امتیاز سلامت' value={`${result.health_score}/100`} icon={Activity} color='text-emerald-500' bgColor='bg-emerald-500/10' delay={0.3} />
              </div>
              <ChartCard title='روند شاخص‌های بوم‌شناختی' icon={Activity}>
                <ResponsiveContainer width='100%' height={300}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray='3 3' stroke='#e5e7eb' />
                    <XAxis dataKey='name' tick={{ fontSize: 10 }} /><YAxis tick={{ fontSize: 10 }} />
                    <Tooltip contentStyle={{ fontSize: '12px', borderRadius: '8px' }} /><Legend wrapperStyle={{ fontSize: '12px' }} />
                    <Line type='monotone' dataKey='NDVI' stroke='#22c55e' strokeWidth={2} />
                    <Line type='monotone' dataKey='NDWI' stroke='#3b82f6' strokeWidth={2} />
                    <Line type='monotone' dataKey='زیست‌توده' stroke='#a855f7' strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </ChartCard>
            </>
          )}
        </div>
      </div>
      <Card className='mt-6'>
        <CardHeader><CardTitle>آپلود تصویر ماهواره‌ای</CardTitle></CardHeader>
        <CardContent><FileUpload accept='image/*' onUpload={async (file) => { const fd = new FormData(); fd.append('file', file); await fetch('/api/monitoring/satellite/upload', { method: 'POST', body: fd }) }} label='تصویر ماهواره‌ای را آپلود کنید' /></CardContent>
      </Card>
    </div>
  )
}
"""

FRONTEND_PAGES["app/monitoring/ai/page.tsx"] = """'use client'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Brain, Sparkles, TrendingUp, Lightbulb, AlertCircle } from 'lucide-react'
import { PageHeader } from '@/components/shared/PageHeader'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

export default function AIAnalysisPage() {
  const [models, setModels] = useState([])
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => { fetch('/api/monitoring/ai/models').then(r => r.json()).then(setModels) }, [])

  const analyze = async () => {
    setLoading(true)
    try { const res = await fetch('/api/monitoring/ai/analyze', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ project_id: 'amazon-north', data_type: 'ndvi', timeframe: '30d' }) }); setResult(await res.json()) } finally { setLoading(false) }
  }

  return (
    <div className='container mx-auto px-4 py-8'>
      <PageHeader title='تحلیل هوش مصنوعی' description='پیش‌بینی و تشخیص با ماشین لرنینگ' icon={Brain} color='text-purple-500' />
      <div className='grid lg:grid-cols-2 gap-6 mb-8'>
        <Card>
          <CardHeader><CardTitle className='flex items-center gap-2'><Sparkles className='w-5 h-5 text-purple-500' /> مدل‌های AI</CardTitle></CardHeader>
          <CardContent className='space-y-3'>
            {models.map((m: any, i) => (
              <motion.div key={m.id} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }} className='flex items-center justify-between p-3 rounded-lg border border-border'>
                <div><div className='font-medium text-sm'>{m.name}</div></div>
                <Badge variant='outline' className='text-green-600'>{(m.accuracy * 100).toFixed(0)}٪ دقت</Badge>
              </motion.div>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>اجرای تحلیل</CardTitle></CardHeader>
          <CardContent>
            <Button className='w-full bg-purple-600 hover:bg-purple-700 mb-4' onClick={analyze} disabled={loading}><Brain className='w-4 h-4 ml-2' />{loading ? 'در حال تحلیل...' : 'تحلیل با AI'}</Button>
            {result && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className='space-y-4'>
                <div className='p-4 rounded-lg bg-purple-500/10 border border-purple-500/20'><p className='text-sm'>{result.summary}</p></div>
                {result.insights?.map((ins: any, i: number) => (
                  <div key={i} className='flex items-start gap-2 p-2 text-sm'>
                    <Badge variant='outline' className={ins.type === 'positive' ? 'text-green-600' : ins.type === 'warning' ? 'text-yellow-600' : 'text-blue-600'}>{ins.type}</Badge>
                    <span className='flex-1'>{ins.message}</span><span className='text-xs text-muted-foreground'>{(ins.confidence * 100).toFixed(0)}٪</span>
                  </div>
                ))}
                {result.recommendations?.map((rec: string, i: number) => (
                  <div key={i} className='text-sm p-2 rounded bg-muted/30 mb-1'>• {rec}</div>
                ))}
              </motion.div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
"""


# ============================================================
#  MAIN
# ============================================================

def main():
    C.enable_windows()
    force = "--force" in sys.argv

    print(f"\n{C.MAGENTA}{C.BOLD}╔{'═'*58}╗{C.RESET}")
    print(f"{C.MAGENTA}{C.BOLD}║  🚀 Econojin Platform Builder v2.0{' '*18}║{C.RESET}")
    print(f"{C.MAGENTA}{C.BOLD}║  مسیر: {str(PROJECT):<51}║{C.RESET}")
    print(f"{C.MAGENTA}{C.BOLD}╚{'═'*58}╝{C.RESET}")

    if not PROJECT.exists():
        print(f"{C.RED}❌ مسیر پروژه وجود ندارد!{C.RESET}")
        return

    created = 0
    skipped = 0

    # Backend
    print(f"\n{C.CYAN}{C.BOLD}━━━ Backend Routes ━━━{C.RESET}")
    for rel_path, content in BACKEND_FILES.items():
        if write_file(PROJECT / rel_path, content, force): created += 1
        else: skipped += 1

    # Components
    print(f"\n{C.CYAN}{C.BOLD}━━━ Shared Components ━━━{C.RESET}")
    for rel_path, content in FRONTEND_COMPONENTS.items():
        if write_file(WEB / "src" / rel_path, content, force): created += 1
        else: skipped += 1

    # Pages
    print(f"\n{C.CYAN}{C.BOLD}━━━ Frontend Pages ━━━{C.RESET}")
    for rel_path, content in FRONTEND_PAGES.items():
        if write_file(WEB / "src" / rel_path, content, force): created += 1
        else: skipped += 1

    # Summary
    print(f"\n{C.MAGENTA}{C.BOLD}{'━'*58}{C.RESET}")
    print(f"  {C.GREEN}✓{C.RESET} فایل‌های ایجاد شده: {created}")
    print(f"  {C.YELLOW}⚠{C.RESET} فایل‌های موجود (رد شده): {skipped}")

    print(f"""
{C.CYAN}📝 مراحل بعدی:{C.RESET}

  ۱. ثبت routes در apps/main.py:
     from apps.api.routes import accounting, simulator, monitoring
     app.include_router(accounting.router)
     app.include_router(simulator.router)
     app.include_router(monitoring.router)

  ۲. نصب پکیج‌ها (اگه نصب نیستن):
     cd apps/web
     pnpm add recharts framer-motion lucide-react

  ۳. تست صفحات:
     /accounting
     /accounting/transactions
     /accounting/invoices
     /simulator
     /simulator/carbon
     /monitoring/satellite
     /monitoring/ai

  ۴. برای بازنویسی فایل‌های موجود:
     python platform_builder.py --force
""")

    # گزارش
    report_dir = PROJECT / "analysis_reports"
    report_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(report_dir / f"platform_builder_{ts}.json", "w", encoding="utf-8") as f:
        json.dump({"created": created, "skipped": skipped, "timestamp": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
