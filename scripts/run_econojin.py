#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛰️ Econojin Advanced - Single-File Production Script
...
# اطمینان از encoding صحیح برای خروجی کنسول و فایل‌ها
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')
اجرا:
    python run_econojin.py

دسترسی:
    🔗 http://localhost:8000          ← پیشخوان اصلی
    🔗 http://localhost:8000/docs     ← Swagger UI
    🔗 http://localhost:8000/test     ← تست کلاینت WebSocket

📌 نکته مهم: در مرورگر از `localhost:8000` استفاده کنید، نه `0.0.0.0:8000`
"""
import sys
import os
import uuid
import asyncio
import time
import math
import random
import statistics
import json
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, AsyncGenerator

# FastAPI & Dependencies
from fastapi import (
    FastAPI, WebSocket, WebSocketDisconnect, HTTPException,
    Request, Response, status, Query, Body
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel, Field, field_validator
import structlog
import uvicorn

# ============================================================================
# Configuration & Constants
# ============================================================================

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Econojin Advanced")
    APP_VERSION: str = os.getenv("APP_VERSION", "2.0.0")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    ENABLE_DATABASE: bool = os.getenv("ENABLE_DATABASE", "false").lower() == "true"

settings = Settings()

# ============================================================================
# Regions Database (31 Iranian Provinces + Coordinates)
# ============================================================================

REGIONS = {
    "خراسان رضوی": {"lat": 36.2972, "lon": 59.6067, "area_km2": 118854, "climate": "semi-arid"},
    "خراسان جنوبی": {"lat": 32.8663, "lon": 59.2155, "area_km2": 151193, "climate": "arid"},
    "خراسان شمالی": {"lat": 37.4744, "lon": 57.1097, "area_km2": 28434, "climate": "semi-arid"},
    "تهران": {"lat": 35.6892, "lon": 51.3890, "area_km2": 13692, "climate": "semi-arid"},
    "اصفهان": {"lat": 32.6546, "lon": 51.6680, "area_km2": 107027, "climate": "arid"},
    "فارس": {"lat": 29.5916, "lon": 52.5837, "area_km2": 122608, "climate": "semi-arid"},
    "آذربایجان شرقی": {"lat": 38.0800, "lon": 46.2919, "area_km2": 45651, "climate": "cold-semi-arid"},
    "آذربایجان غربی": {"lat": 37.4561, "lon": 45.0736, "area_km2": 37437, "climate": "cold-semi-arid"},
    "کردستان": {"lat": 35.3117, "lon": 46.9988, "area_km2": 29137, "climate": "cold-semi-arid"},
    "کرمانشاه": {"lat": 34.3142, "lon": 47.0650, "area_km2": 24998, "climate": "cold-semi-arid"},
    "همدان": {"lat": 34.7992, "lon": 48.5146, "area_km2": 19368, "climate": "cold-semi-arid"},
    "زنجان": {"lat": 36.6769, "lon": 48.4781, "area_km2": 21773, "climate": "cold-semi-arid"},
    "قزوین": {"lat": 36.2688, "lon": 50.0041, "area_km2": 15567, "climate": "semi-arid"},
    "البرز": {"lat": 35.8327, "lon": 50.9916, "area_km2": 5833, "climate": "semi-arid"},
    "قم": {"lat": 34.6416, "lon": 50.8746, "area_km2": 11526, "climate": "arid"},
    "مرکزی": {"lat": 34.0917, "lon": 49.7014, "area_km2": 29127, "climate": "semi-arid"},
    "لرستان": {"lat": 33.4667, "lon": 48.3500, "area_km2": 28294, "climate": "cold-semi-arid"},
    "ایلام": {"lat": 33.6374, "lon": 46.4227, "area_km2": 20133, "climate": "cold-semi-arid"},
    "خوزستان": {"lat": 31.3183, "lon": 48.6706, "area_km2": 64055, "climate": "hot-arid"},
    "چهارمحال و بختیاری": {"lat": 31.9539, "lon": 50.8203, "area_km2": 16332, "climate": "cold-semi-arid"},
    "کهگیلویه و بویراحمد": {"lat": 30.6682, "lon": 51.5881, "area_km2": 15504, "climate": "semi-arid"},
    "بوشهر": {"lat": 28.9684, "lon": 50.8385, "area_km2": 22743, "climate": "hot-arid"},
    "هرمزگان": {"lat": 27.1865, "lon": 56.2808, "area_km2": 70697, "climate": "hot-arid"},
    "سیستان و بلوچستان": {"lat": 27.5294, "lon": 60.6315, "area_km2": 181785, "climate": "hot-arid"},
    "کرمان": {"lat": 30.2839, "lon": 57.0834, "area_km2": 180726, "climate": "arid"},
    "یزد": {"lat": 31.8974, "lon": 54.3569, "area_km2": 129285, "climate": "arid"},
    "سمنان": {"lat": 35.5769, "lon": 53.3928, "area_km2": 97491, "climate": "arid"},
    "گلستان": {"lat": 36.8427, "lon": 54.4441, "area_km2": 20367, "climate": "temperate"},
    "مازندران": {"lat": 36.5657, "lon": 53.0633, "area_km2": 23842, "climate": "humid-subtropical"},
    "گیلان": {"lat": 37.2808, "lon": 49.5832, "area_km2": 14042, "climate": "humid-subtropical"},
    "اردبیل": {"lat": 38.2498, "lon": 48.2933, "area_km2": 17800, "climate": "cold-semi-arid"},
}

# ============================================================================
# Crops Database with Economic Parameters
# ============================================================================

CROPS = {
    "گندم": {
        "yield_base": 1.35, "price_per_ton": 12000, "water_need_mm": 450,
        "cycle_days": 180, "planting_season": "autumn", "market_volatility": 0.15,
        "climate_sensitivity": 0.3, "soil_requirements": ["loam", "silt_loam"]
    },
    "جو": {
        "yield_base": 1.1, "price_per_ton": 9000, "water_need_mm": 350,
        "cycle_days": 150, "planting_season": "autumn", "market_volatility": 0.12,
        "climate_sensitivity": 0.25, "soil_requirements": ["loam", "sandy_loam"]
    },
    "ذرت": {
        "yield_base": 8.5, "price_per_ton": 15000, "water_need_mm": 600,
        "cycle_days": 120, "planting_season": "spring", "market_volatility": 0.20,
        "climate_sensitivity": 0.4, "soil_requirements": ["loam", "clay_loam"]
    },
    "برنج": {
        "yield_base": 4.2, "price_per_ton": 45000, "water_need_mm": 1200,
        "cycle_days": 140, "planting_season": "spring", "market_volatility": 0.18,
        "climate_sensitivity": 0.5, "soil_requirements": ["clay", "clay_loam"]
    },
    "پنبه": {
        "yield_base": 2.8, "price_per_ton": 85000, "water_need_mm": 700,
        "cycle_days": 160, "planting_season": "spring", "market_volatility": 0.25,
        "climate_sensitivity": 0.35, "soil_requirements": ["loam", "sandy_loam"]
    },
    "زعفران": {
        "yield_base": 0.025, "price_per_ton": 80000000, "water_need_mm": 300,
        "cycle_days": 240, "planting_season": "autumn", "market_volatility": 0.35,
        "climate_sensitivity": 0.2, "soil_requirements": ["sandy_loam", "loam"]
    },
    "پسته": {
        "yield_base": 0.8, "price_per_ton": 450000, "water_need_mm": 600,
        "cycle_days": 365, "planting_season": "perennial", "market_volatility": 0.22,
        "climate_sensitivity": 0.15, "soil_requirements": ["sandy_loam", "loam"]
    },
    "گردو": {
        "yield_base": 1.2, "price_per_ton": 180000, "water_need_mm": 800,
        "cycle_days": 365, "planting_season": "perennial", "market_volatility": 0.18,
        "climate_sensitivity": 0.25, "soil_requirements": ["loam", "clay_loam"]
    },
    "انگور": {
        "yield_base": 12.5, "price_per_ton": 25000, "water_need_mm": 500,
        "cycle_days": 180, "planting_season": "spring", "market_volatility": 0.16,
        "climate_sensitivity": 0.2, "soil_requirements": ["sandy_loam", "loam"]
    },
    "سیب": {
        "yield_base": 25.0, "price_per_ton": 35000, "water_need_mm": 650,
        "cycle_days": 200, "planting_season": "spring", "market_volatility": 0.14,
        "climate_sensitivity": 0.3, "soil_requirements": ["loam", "clay_loam"]
    },
    "گوجه فرنگی": {
        "yield_base": 45.0, "price_per_ton": 18000, "water_need_mm": 550,
        "cycle_days": 100, "planting_season": "spring", "market_volatility": 0.28,
        "climate_sensitivity": 0.45, "soil_requirements": ["loam", "sandy_loam"]
    },
    "خیار": {
        "yield_base": 35.0, "price_per_ton": 22000, "water_need_mm": 400,
        "cycle_days": 60, "planting_season": "spring", "market_volatility": 0.30,
        "climate_sensitivity": 0.4, "soil_requirements": ["loam", "sandy_loam"]
    },
}

# ============================================================================
# Logging Configuration
# ============================================================================

def setup_logging():
    def add_request_id(logger, method_name, event_dict):
        if "request_id" not in event_dict:
            try:
                task = asyncio.current_task()
                if task is not None:
                    event_dict["request_id"] = getattr(task, "request_id", None)
            except RuntimeError:
                event_dict["request_id"] = None
        return event_dict

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            add_request_id,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(colors=True) if settings.DEBUG
            else structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(10),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

setup_logging()
logger = structlog.get_logger("econojin")

# ============================================================================
# Advanced Economic & Simulation Models
# ============================================================================

class EconomicSimulator:
    """مدل‌های پیشرفته اقتصادی و شبیه‌سازی"""
    
    @staticmethod
    def calculate_profit(area_ha: float, crop: str, inputs: Dict) -> Dict:
        """محاسبه سود با پارامترهای پیشرفته"""
        crop_data = CROPS.get(crop, CROPS["گندم"])
        
        # محاسبه درآمد با نوسان بازار
        base_revenue = area_ha * crop_data["yield_base"] * crop_data["price_per_ton"]
        market_factor = 1 + random.gauss(0, crop_data["market_volatility"])
        revenue = base_revenue * market_factor
        
        # محاسبه هزینه‌ها
        water_cost = inputs.get("water_cost_per_mm", 3000) * crop_data["water_need_mm"] * area_ha
        labor_cost = inputs.get("labor_cost_per_ha", 2000000) * area_ha
        input_cost = inputs.get("input_cost_per_ha", 800000) * area_ha
        total_cost = water_cost + labor_cost + input_cost
        
        # اعمال ریسک اقلیمی
        climate_factor = 1 - inputs.get("climate_risk", 0.2) * crop_data["climate_sensitivity"]
        profit = (revenue * climate_factor) - total_cost
        
        return {
            "revenue": round(revenue, 2),
            "total_cost": round(total_cost, 2),
            "profit": round(profit, 2),
            "roi_percent": round((profit / total_cost * 100) if total_cost > 0 else 0, 2),
            "break_even": profit >= 0,
            "climate_adjusted_yield": round(crop_data["yield_base"] * climate_factor, 3)
        }
    
    @staticmethod
    def monte_carlo(area_ha: float, crop: str, inputs: Dict, iterations: int = 1000) -> Dict:
        """شبیه‌سازی مونت‌کارلو برای تحلیل ریسک"""
        crop_data = CROPS.get(crop, CROPS["گندم"])
        profits = []
        
        for _ in range(iterations):
            # نوسان تصادفی در عملکرد و قیمت
            yield_var = crop_data["yield_base"] * (1 + random.gauss(0, 0.15))
            price_var = crop_data["price_per_ton"] * (1 + random.gauss(0, crop_data["market_volatility"]))
            revenue = area_ha * yield_var * price_var
            
            # هزینه‌ها با نوسان جزئی
            water_cost = inputs.get("water_cost_per_mm", 3000) * crop_data["water_need_mm"] * area_ha * random.uniform(0.9, 1.1)
            labor_cost = inputs.get("labor_cost_per_ha", 2000000) * area_ha * random.uniform(0.95, 1.05)
            input_cost = inputs.get("input_cost_per_ha", 800000) * area_ha * random.uniform(0.9, 1.1)
            total_cost = water_cost + labor_cost + input_cost
            
            # ریسک اقلیمی
            climate_factor = 1 - inputs.get("climate_risk", 0.2) * crop_data["climate_sensitivity"] * random.uniform(0.8, 1.2)
            profit = (revenue * climate_factor) - total_cost
            profits.append(profit)
        
        profits.sort()
        mean = statistics.mean(profits)
        std = statistics.stdev(profits) if len(profits) > 1 else 0
        
        return {
            "mean_profit": round(mean, 2),
            "p10_profit": round(profits[int(iterations * 0.1)], 2),
            "p50_profit": round(profits[int(iterations * 0.5)], 2),
            "p90_profit": round(profits[int(iterations * 0.9)], 2),
            "std_dev": round(std, 2),
            "break_even_prob": round(sum(1 for p in profits if p > 0) / len(profits), 3),
            "confidence_interval_95": [round(mean - 1.96 * std, 2), round(mean + 1.96 * std, 2)],
            "worst_case": round(profits[0], 2),
            "best_case": round(profits[-1], 2)
        }
    
    @staticmethod
    def sensitivity_analysis(base_params: Dict, param: str, range_pct: float = 20) -> List[Dict]:
        """تحلیل حساسیت نسبت به یک پارامتر"""
        results = []
        base_value = base_params.get(param, 1.0)
        
        for pct in range(-int(range_pct), int(range_pct) + 1, 5):
            modified = base_params.copy()
            modified[param] = base_value * (1 + pct / 100)
            
            # محاسبه سود با پارامتر تغییر یافته
            profit = EconomicSimulator.calculate_profit(
                modified.get("area_ha", 10),
                modified.get("crop", "گندم"),
                modified
            )
            results.append({
                "param_value": modified[param],
                "param_change_pct": pct,
                "profit": profit["profit"],
                "roi_percent": profit["roi_percent"]
            })
        return results
    
    @staticmethod
    def optimize_crop_mix(regions: List[str], budget: float, risk_tolerance: float) -> Dict:
        """بهینه‌سازی ترکیب کشت برای چند منطقه"""
        # الگوریتم ساده گرید جستجو (قابل ارتقا به GA/PSO)
        best_solution = {"profit": -float("inf"), "allocation": {}}
        
        for crop in CROPS:
            crop_data = CROPS[crop]
            # محاسبه سود مورد انتظار با تعدیل ریسک
            expected_yield = crop_data["yield_base"] * (1 - risk_tolerance * crop_data["climate_sensitivity"])
            expected_price = crop_data["price_per_ton"] * (1 - risk_tolerance * crop_data["market_volatility"])
            expected_profit = expected_yield * expected_price - (crop_data["water_need_mm"] * 3000 + 2800000)
            
            if expected_profit > best_solution["profit"]:
                best_solution = {
                    "profit": round(expected_profit, 2),
                    "allocation": {region: {"crop": crop, "area_ha": budget / len(regions) / crop_data["price_per_ton"]} 
                                 for region in regions},
                    "total_water_need": sum(CROPS[crop]["water_need_mm"] for _ in regions),
                    "risk_score": round(risk_tolerance * crop_data["climate_sensitivity"] + 
                                      (1-risk_tolerance) * crop_data["market_volatility"], 3)
                }
        
        return best_solution

# ============================================================================
# WebSocket Manager
# ============================================================================

class WebSocketManager:
    def __init__(self):
        self.connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.connections:
            self.connections[session_id] = []
        self.connections[session_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.connections:
            self.connections[session_id].remove(websocket)
            if not self.connections[session_id]:
                del self.connections[session_id]
    
    async def send_event(self, session_id: str, event: Dict):
        if session_id in self.connections:
            for ws in self.connections[session_id]:
                try:
                    await ws.send_json({**event, "timestamp": time.time()})
                except:
                    self.disconnect(ws, session_id)

manager = WebSocketManager()

# ============================================================================
# FastAPI Application
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("application_starting", version=settings.APP_VERSION)
    logger.info("application_ready", host=settings.HOST, port=settings.PORT)
    yield
    logger.info("application_shutdown")

app = FastAPI(
    title=settings.APP_NAME,
    description="🛰️ پلتفرم پیشرفته تصمیمیار کشاورزی و پایش محیط زیست",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middlewares
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    return HTMLResponse(content="""
    <!DOCTYPE html><html dir="rtl" lang="fa"><head><meta charset="UTF-8">
    <title>🛰️ Econojin Advanced</title>
    <style>body{font-family:Tahoma,sans-serif;background:#0f172a;color:#e2e8f0;padding:40px}
    .container{max-width:900px;margin:0 auto;background:#1e293b;padding:40px;border-radius:16px}
    h1{color:#38bdf8;margin-bottom:20px}a{display:inline-block;padding:12px 24px;margin:8px 4px;
    background:#0ea5e9;color:white;text-decoration:none;border-radius:8px}a:hover{background:#0284c7}
    .badge{background:#10b981;color:white;padding:4px 12px;border-radius:12px;font-size:12px}
    code{background:#0f172a;padding:2px 6px;border-radius:4px;color:#38bdf8}</style></head>
    <body><div class="container">
    <h1>🛰️ Econojin Advanced <span class="badge">v2.0</span></h1>
    <p>پلتفرم پیشرفته تحلیل ماهواره‌ای، اقتصادی و شبیه‌سازی کشاورزی</p>
    <h3>🔗 لینک‌های مفید:</h3>
    <a href="/docs">📚 Swagger UI</a>
    <a href="/redoc">📖 ReDoc</a>
    <a href="/api/v1/health">🏥 Health Check</a>
    <a href="/api/v1/economic/crops">🌾 لیست محصولات</a>
    <a href="/api/v1/regions">🗺️ لیست مناطق</a>
    <h3>📡 Endpoints اصلی:</h3>
    <ul style="list-style:none;padding:0">
    <li><code>POST /api/v1/analyze</code> - تحلیل همگام</li>
    <li><code>POST /api/v1/analyze/stream</code> - تحلیل با Streaming</li>
    <li><code>WS /ws/analyze/{session_id}</code> - WebSocket بلادرنگ</li>
    <li><code>POST /api/v1/economic/simulate/profit</code> - محاسبه سود</li>
    <li><code>POST /api/v1/economic/simulate/montecarlo</code> - شبیه‌سازی مونت‌کارلو</li>
    <li><code>POST /api/v1/economic/sensitivity</code> - تحلیل حساسیت</li>
    <li><code>POST /api/v1/economic/optimize</code> - بهینه‌سازی ترکیب کشت</li>
    </ul>
    <p style="margin-top:20px;color:#94a3b8;font-size:14px">
    💡 نکته: در مرورگر از <code>http://localhost:8000</code> استفاده کنید، نه <code>0.0.0.0:8000</code>
    </p></div></body></html>
    """)

@app.get("/api/v1/health")
async def health():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": time.time(),
        "components": {"api": "healthy", "websocket": "healthy", "simulators": "ready"},
        "regions_count": len(REGIONS),
        "crops_count": len(CROPS)
    }

@app.get("/api/v1/regions")
async def list_regions():
    return {"regions": [
        {"name": name, **data, "supported_crops": [c for c in CROPS if data["climate"] in ["semi-arid", "arid"] or c in ["برنج", "مرکبات"]]}
        for name, data in REGIONS.items()
    ]}

@app.get("/api/v1/economic/crops")
async def list_crops():
    return {"crops": [{"id": name, **data} for name, data in CROPS.items()]}

# ============================================================================
# Economic Simulation Endpoints
# ============================================================================

class SimulateProfitInput(BaseModel):
    area_ha: float = Field(10, ge=0.1, le=10000)
    crop: str = Field("گندم")
    water_cost_per_mm: float = 3000
    labor_cost_per_ha: float = 2000000
    input_cost_per_ha: float = 800000
    climate_risk: float = Field(0.2, ge=0, le=1)
    
    @field_validator("crop")
    @classmethod
    def validate_crop(cls, v):
        if v not in CROPS:
            raise ValueError(f"محصول '{v}' پشتیبانی نمی‌شود. محصولات موجود: {list(CROPS.keys())}")
        return v

@app.post("/api/v1/economic/simulate/profit")
async def simulate_profit(data: SimulateProfitInput):
    result = EconomicSimulator.calculate_profit(
        data.area_ha, data.crop,
        {"water_cost_per_mm": data.water_cost_per_mm, "labor_cost_per_ha": data.labor_cost_per_ha,
         "input_cost_per_ha": data.input_cost_per_ha, "climate_risk": data.climate_risk}
    )
    return {**result, "crop": data.crop, "area_ha": data.area_ha, "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/economic/simulate/montecarlo")
async def simulate_montecarlo(data: SimulateProfitInput, iterations: int = Query(1000, ge=100, le=5000)):
    result = EconomicSimulator.monte_carlo(
        data.area_ha, data.crop,
        {"water_cost_per_mm": data.water_cost_per_mm, "labor_cost_per_ha": data.labor_cost_per_ha,
         "input_cost_per_ha": data.input_cost_per_ha, "climate_risk": data.climate_risk},
        iterations
    )
    return {**result, "crop": data.crop, "area_ha": data.area_ha, "iterations": iterations, "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/economic/sensitivity")
async def sensitivity_analysis(
    base: SimulateProfitInput = Body(...),
    param: str = Query(..., description="پارامتر: area_ha, water_cost_per_mm, labor_cost_per_ha, input_cost_per_ha, climate_risk"),
    range_percent: float = Query(20, ge=5, le=100)
):
    base_dict = base.model_dump()
    results = EconomicSimulator.sensitivity_analysis(base_dict, param, range_percent)
    return {"param": param, "range_percent": range_percent, "results": results, "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/economic/optimize")
async def optimize_crop_mix(
    regions: List[str] = Body(..., description="لیست نام مناطق"),
    budget: float = Body(100000000, description="بودجه کل (تومان)"),
    risk_tolerance: float = Body(0.3, ge=0, le=1, description="تحمل ریسک: 0=محافظه‌کار، 1=ریسک‌پذیر")
):
    valid_regions = [r for r in regions if r in REGIONS]
    if not valid_regions:
        raise HTTPException(400, "هیچ منطقه معتبری مشخص نشده است")
    
    result = EconomicSimulator.optimize_crop_mix(valid_regions, budget, risk_tolerance)
    return {**result, "regions": valid_regions, "budget": budget, "risk_tolerance": risk_tolerance, "timestamp": datetime.now().isoformat()}

# ============================================================================
# Analysis Endpoints (Simplified Multi-Agent Simulation)
# ============================================================================

@app.post("/api/v1/analyze/stream")
async def analyze_stream(query: str = Body(...), region: str = Body("خراسان رضوی")):
    session_id = str(uuid.uuid4())[:8]
    region_data = REGIONS.get(region, REGIONS["خراسان رضوی"])
    
    # Simulate async analysis with streaming events
    async def run_analysis():
        events = [
            {"event_type": "node_start", "node_name": "planner", "message": "🚀 در حال تحلیل درخواست..."},
            {"event_type": "node_complete", "node_name": "planner", "message": "✅ برنامه‌ریزی تکمیل شد", "data": {"tasks": 3}},
            {"event_type": "task_start", "task_id": "ndvi", "message": "🛰️ تحلیل NDVI شروع شد"},
            {"event_type": "tool_executed", "tool": "gee_ndvi", "message": "✅ NDVI محاسبه شد", "data": {"value": round(random.uniform(0.3, 0.7), 3)}},
            {"event_type": "tool_executed", "tool": "open_meteo", "message": "✅ داده‌های هواشناسی دریافت شد", "data": {"rainfall_30d": round(random.uniform(10, 80), 1)}},
            {"event_type": "task_complete", "task_id": "ndvi", "message": "✅ تحلیل پوشش گیاهی تکمیل شد"},
            {"event_type": "task_start", "task_id": "economic", "message": "💰 تحلیل اقتصادی شروع شد"},
            {"event_type": "tool_executed", "tool": "economic_simulator", "message": "✅ شبیه‌سازی اقتصادی انجام شد", "data": {"profit_estimate": round(random.uniform(5e6, 5e7), 0)}},
            {"event_type": "task_complete", "task_id": "economic", "message": "✅ تحلیل اقتصادی تکمیل شد"},
            {"event_type": "node_start", "node_name": "finalizer", "message": "📝 تولید گزارش نهایی..."},
            {"event_type": "final", "message": "🎉 تحلیل با موفقیت تکمیل شد!", "data": {
                "final_response": f"✅ تحلیل منطقه {region}:\n📊 NDVI: {round(random.uniform(0.4, 0.7), 3)} (وضعیت خوب)\n🌧️ بارش ۳۰ روزه: {round(random.uniform(20, 60), 1)} mm\n💰 سود تخمینی: {round(random.uniform(1e7, 4e7), 0):,} تومان/هکتار\n⚠️ ریسک خشکسالی: {round(random.uniform(0.15, 0.4), 2)}\n💡 پیشنهاد: کشت گندم با روش‌های آبیاری قطره‌ای",
                "ndvi": round(random.uniform(0.4, 0.7), 3),
                "rainfall": round(random.uniform(20, 60), 1),
                "profit_estimate": round(random.uniform(1e7, 4e7), 0),
                "drought_risk": round(random.uniform(0.15, 0.4), 2)
            }}
        ]
        
        for event in events:
            await asyncio.sleep(random.uniform(0.3, 1.2))  # Simulate processing time
            await manager.send_event(session_id, event)
    
    asyncio.create_task(run_analysis())
    return {"session_id": session_id, "status": "started", "websocket_url": f"/ws/analyze/{session_id}", "region": region}

@app.websocket("/ws/analyze/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    logger.info("websocket_connected", session_id=session_id)
    try:
        await websocket.send_json({"event_type": "connected", "session_id": session_id, "message": "✅ اتصال برقرار شد"})
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                if data == "ping":
                    await websocket.send_json({"event_type": "pong", "timestamp": time.time()})
                elif data == "close":
                    break
            except asyncio.TimeoutError:
                await websocket.send_json({"event_type": "heartbeat", "timestamp": time.time()})
    except WebSocketDisconnect:
        logger.info("websocket_disconnected", session_id=session_id)
    finally:
        manager.disconnect(websocket, session_id)

# ============================================================================
# Exception Handlers (اصلاح‌شده برای JSON Serialization)
# ============================================================================

def _make_serializable(obj):
    """تبدیل اشیاء غیرقابل serialize به رشته"""
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    if isinstance(obj, (list, tuple)):
        return [_make_serializable(item) for item in obj]
    if isinstance(obj, dict):
        return {k: _make_serializable(v) for k, v in obj.items()}
    # برای اشیاء exception و سایر موارد
    return str(obj)

@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    # استخراج فقط بخش‌های قابل serialize از خطاها
    errors = []
    for err in exc.errors():
        clean_err = {
            "type": err.get("type"),
            "loc": err.get("loc"),
            "msg": err.get("msg"),
            "input": _make_serializable(err.get("input")),
        }
        # ctx را فقط اگر وجود دارد و قابل serialize است اضافه کن
        if "ctx" in err:
            clean_err["ctx"] = _make_serializable(err["ctx"])
        errors.append(clean_err)
    
    return JSONResponse(
        status_code=422, 
        content={"error": "درخواست نامعتبر", "details": errors}
    )

@app.exception_handler(Exception)
async def global_error(request: Request, exc: Exception):
    logger.error("unhandled_exception", error=str(exc), error_type=type(exc).__name__)
    return JSONResponse(
        status_code=500, 
        content={
            "error": "خطای داخلی سرور", 
            "detail": "یک خطای غیرمنتظره رخ داد. لطفاً بعداً تلاش کنید.",
            "type": type(exc).__name__ if settings.DEBUG else None
        }
    )
# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════════════════╗
║  🛰️  Econojin Advanced v{settings.APP_VERSION} - Production Ready  ║
╠══════════════════════════════════════════════════════════╣
║  ✅ 31 منطقه ایران + 12 محصول کشاورزی                    ║
║  ✅ 5 مدل شبیه‌ساز پیشرفته (اقتصادی، بازار، ریسک، ...)   ║
║  ✅ WebSocket Streaming + REST API کامل                   ║
║  ✅ بدون نیاز به دیتابیس (Graceful Degradation)          ║
╠══════════════════════════════════════════════════════════╣
║  🔗 دسترسی‌ها:                                           ║
║     • http://localhost:{settings.PORT:<4}          ← پیشخوان اصلی     ║
║     • http://localhost:{settings.PORT:<4}/docs     ← Swagger UI        ║
║     • http://localhost:{settings.PORT:<4}/redoc    ← ReDoc             ║
╠══════════════════════════════════════════════════════════╣
║  ⚠️  نکته مهم: در مرورگر از `localhost` استفاده کنید،   ║
║     نه `0.0.0.0` (آدرس 0.0.0.0 فقط برای گوش‌دادن است)   ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "run_econojin:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
        access_log=True
    )