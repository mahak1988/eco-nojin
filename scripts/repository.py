"""
لایه Repository برای عملیات دیتابیس
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy.dialects.postgresql import insert
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import structlog

from api.database import FieldAnalysis, MRVReport, FieldObservation

logger = structlog.get_logger()


class AnalysisRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save_analysis(self, data: Dict[str, Any]) -> FieldAnalysis:
        """ذخیره نتیجه تحلیل"""
        analysis = FieldAnalysis(
            session_id=data["session_id"],
            region=data["region"],
            query=data["query"],
            ndvi_avg=data.get("ndvi_avg"),
            ndvi_health=data.get("ndvi_health"),
            erosion_rate=data.get("erosion_rate"),
            erosion_severity=data.get("erosion_severity"),
            predicted_yield=data.get("predicted_yield"),
            irrigation_need=data.get("irrigation_need"),
            rainfall_30d=data.get("rainfall_30d"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            geom=func.ST_SetSRID(
                func.ST_MakePoint(data["longitude"], data["latitude"]),
                4326
            ) if data.get("latitude") and data.get("longitude") else None,
            quality_score=data.get("quality_score", 0.0),
            tools_used=data.get("tools_used", []),
            full_response=data.get("full_response"),
            execution_time_ms=data.get("execution_time_ms", 0.0)
        )
        self.session.add(analysis)
        await self.session.flush()
        logger.info("analysis_saved", id=analysis.id, region=analysis.region)
        return analysis
    
    async def get_recent(self, region: Optional[str] = None, limit: int = 20) -> List[FieldAnalysis]:
        """دریافت تحلیل‌های اخیر"""
        query = select(FieldAnalysis).order_by(desc(FieldAnalysis.created_at)).limit(limit)
        if region:
            query = query.where(FieldAnalysis.region == region)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_ndvi_timeseries(self, region: str, days: int = 180) -> List[Dict]:
        """سری زمانی NDVI برای یک منطقه"""
        since = datetime.utcnow() - timedelta(days=days)
        query = (
            select(
                FieldAnalysis.created_at,
                FieldAnalysis.ndvi_avg,
                FieldAnalysis.ndvi_health
            )
            .where(FieldAnalysis.region == region)
            .where(FieldAnalysis.created_at >= since)
            .where(FieldAnalysis.ndvi_avg.isnot(None))
            .order_by(FieldAnalysis.created_at)
        )
        result = await self.session.execute(query)
        return [
            {"date": row[0].isoformat(), "ndvi": row[1], "health": row[2]}
            for row in result.all()
        ]
    
    async def get_erosion_hotspots(self, threshold: float = 25.0) -> List[FieldAnalysis]:
        """نقاط بحرانی فرسایش (برای نمایش روی نقشه)"""
        query = (
            select(FieldAnalysis)
            .where(FieldAnalysis.erosion_rate >= threshold)
            .order_by(desc(FieldAnalysis.erosion_rate))
            .limit(50)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def aggregate_by_region(self) -> List[Dict]:
        """آمار تجمیعی هر منطقه (برای داشبورد)"""
        query = (
            select(
                FieldAnalysis.region,
                func.count(FieldAnalysis.id).label("total_analyses"),
                func.avg(FieldAnalysis.ndvi_avg).label("avg_ndvi"),
                func.avg(FieldAnalysis.erosion_rate).label("avg_erosion"),
                func.avg(FieldAnalysis.predicted_yield).label("avg_yield")
            )
            .group_by(FieldAnalysis.region)
            .order_by(desc("total_analyses"))
        )
        result = await self.session.execute(query)
        return [
            {
                "region": row[0],
                "total_analyses": row[1],
                "avg_ndvi": round(row[2] or 0, 3),
                "avg_erosion": round(row[3] or 0, 2),
                "avg_yield": round(row[4] or 0, 2)
            }
            for row in result.all()
        ]