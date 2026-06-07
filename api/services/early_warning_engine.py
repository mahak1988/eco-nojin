# api/services/early_warning_engine.py
"""
سیستم هشدار زودهنگام هیبریدی (Hybrid Early Warning System)
ترکیب داده‌های IoT، ماهواره‌ای و پیش‌بینی‌های هواشناسی
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import async_session
from api.modules.iot.models import SensorReading, Sensor
from api.modules.maintenance.models import EarlyWarningAlert, MaintenanceWorkOrder

logger = logging.getLogger(__name__)


class EarlyWarningEngine:
    """موتور هشدار زودهنگام هیبریدی"""
    
    def __init__(self):
        self.running = False
        self.check_interval = 300  # 5 minutes
    
    async def start(self):
        """شروع پایش مداوم"""
        self.running = True
        logger.info("🚨 Early Warning Engine started")
        
        while self.running:
            try:
                await self._check_all_alerts()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"❌ EWS error: {e}")
                await asyncio.sleep(60)
    
    async def _check_all_alerts(self):
        """بررسی تمام شرایط هشدار"""
        async with async_session() as session:
            # 1. بررسی هشدارهای سیلاب
            await self._check_flood_risk(session)
            
            # 2. بررسی هشدارهای خشکسالی
            await self._check_drought_risk(session)
            
            # 3. بررسی خرابی سازه‌ها
            await self._check_structure_damage(session)
            
            # 4. بررسی تنش آبی
            await self._check_water_stress(session)
            
            await session.commit()
    
    async def _check_flood_risk(self, session: AsyncSession):
        """بررسی ریسک سیلاب"""
        # دریافت آخرین خوانش باران‌سنج‌ها
        query = (
            select(SensorReading)
            .where(SensorReading.sensor_code.like('RAIN-%'))
            .order_by(SensorReading.timestamp.desc())
            .limit(10)
        )
        result = await session.execute(query)
        rain_readings = result.scalars().all()
        
        for reading in rain_readings:
            if reading.value and reading.value > 50:  # > 50mm/hr
                # ایجاد هشدار
                alert = EarlyWarningAlert(
                    alert_type="flood",
                    severity="critical" if reading.value > 100 else "warning",
                    title=f"هشدار سیلاب - بارش شدید {reading.value}mm/hr",
                    description=f"بارش شدید با شدت {reading.value} میلی‌متر بر ساعت detected. احتمال سیلاب در 2-6 ساعت آینده.",
                    affected_area="حوضه آبریز پایین‌دست",
                    trigger_data={
                        "sensor_code": reading.sensor_code,
                        "rainfall_mm_hr": reading.value,
                        "timestamp": reading.timestamp.isoformat()
                    },
                    confidence_level=0.85,
                    expected_impact_at=datetime.utcnow() + timedelta(hours=3),
                    expires_at=datetime.utcnow() + timedelta(hours=12),
                    recommended_actions=[
                        "تخلیه مناطق低洼",
                        "باز کردن مسیرهای آب",
                        "آماده‌باش تیم‌های امداد",
                        "هشدار به کشاورزان پایین‌دست"
                    ]
                )
                session.add(alert)
                logger.warning(f"🌊 Flood alert generated: {reading.value}mm/hr")
                
                # تولید خودکار دستور کار
                await self._generate_flood_work_order(session, alert)
    
    async def _check_drought_risk(self, session: AsyncSession):
        """بررسی ریسک خشکسالی"""
        # دریافت میانگین رطوبت خاک 7 روز اخیر
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        query = (
            select(SensorReading)
            .where(
                SensorReading.sensor_code.like('TDR-%'),
                SensorReading.timestamp >= seven_days_ago
            )
        )
        result = await session.execute(query)
        moisture_readings = result.scalars().all()
        
        if moisture_readings:
            avg_moisture = sum(r.value for r in moisture_readings if r.value) / len(moisture_readings)
            
            if avg_moisture < 15:  # رطوبت خیلی کم
                alert = EarlyWarningAlert(
                    alert_type="drought",
                    severity="warning" if avg_moisture < 15 else "critical",
                    title=f"هشدار خشکسالی - رطوبت خاک {avg_moisture:.1f}%",
                    description=f"میانگین رطوبت خاک در 7 روز اخیر {avg_moisture:.1f}% بوده که نشان‌دهنده تنش آبی شدید است.",
                    affected_area="مناطق کشاورزی",
                    trigger_data={
                        "avg_moisture_percent": avg_moisture,
                        "period_days": 7,
                        "sensor_count": len(moisture_readings)
                    },
                    confidence_level=0.75,
                    expected_impact_at=datetime.utcnow() + timedelta(days=14),
                    expires_at=datetime.utcnow() + timedelta(days=30),
                    recommended_actions=[
                        "کاهش آبیاری غیرضروری",
                        "استفاده از روش‌های حفظ رطوبت",
                        "تغییر الگوی کشت",
                        "فعال‌سازی منابع آب جایگزین"
                    ]
                )
                session.add(alert)
                logger.warning(f"🏜️ Drought alert: moisture {avg_moisture:.1f}%")
    
    async def _check_structure_damage(self, session: AsyncSession):
        """بررسی خرابی سازه‌ها"""
        # بررسی تغییرات ناگهانی در داده‌های فلوم‌ها
        query = (
            select(SensorReading)
            .where(SensorReading.sensor_code.like('FLUME-%'))
            .order_by(SensorReading.timestamp.desc())
            .limit(20)
        )
        result = await session.execute(query)
        flume_readings = result.scalars().all()
        
        # بررسی نوسانات شدید
        if len(flume_readings) >= 2:
            recent = [r.value for r in flume_readings[:5] if r.value]
            older = [r.value for r in flume_readings[5:10] if r.value]
            
            if recent and older:
                avg_recent = sum(recent) / len(recent)
                avg_older = sum(older) / len(older)
                
                change_percent = abs(avg_recent - avg_older) / avg_older * 100
                
                if change_percent > 50:  # تغییر بیش از 50%
                    alert = EarlyWarningAlert(
                        alert_type="structure_damage",
                        severity="critical",
                        title=f"احتمال خرابی سازه - تغییر {change_percent:.0f}% در دبی",
                        description=f"تغییر ناگهانی {change_percent:.0f}% در دبی اندازه‌گیری شده. احتمال گرفتگی یا خرابی سازه.",
                        affected_area="سازه‌های آبخیزداری",
                        trigger_data={
                            "change_percent": change_percent,
                            "recent_avg": avg_recent,
                            "older_avg": avg_older
                        },
                        confidence_level=0.70,
                        expected_impact_at=datetime.utcnow() + timedelta(hours=6),
                        expires_at=datetime.utcnow() + timedelta(hours=24),
                        recommended_actions=[
                            "بازرسی فوری سازه",
                            "بررسی گرفتگی احتمالی",
                            "آماده‌سازی تجهیزات تعمیر",
                            "تخلیه احتیاطی آب بالا‌دست"
                        ]
                    )
                    session.add(alert)
                    logger.warning(f"🏗️ Structure damage alert: {change_percent:.0f}% change")
                    
                    # تولید خودکار دستور کار بازرسی
                    await self._generate_inspection_work_order(session, alert)
    
    async def _check_water_stress(self, session: AsyncSession):
        """بررسی تنش آبی"""
        # مقایسه دبی ورودی و خروجی
        inflow_query = (
            select(SensorReading)
            .where(SensorReading.sensor_code == 'FLUME-001')
            .order_by(SensorReading.timestamp.desc())
            .limit(1)
        )
        outflow_query = (
            select(SensorReading)
            .where(SensorReading.sensor_code == 'FLUME-002')
            .order_by(SensorReading.timestamp.desc())
            .limit(1)
        )
        
        inflow_result = await session.execute(inflow_query)
        outflow_result = await session.execute(outflow_query)
        
        inflow = inflow_result.scalar_one_or_none()
        outflow = outflow_result.scalar_one_or_none()
        
        if inflow and outflow and inflow.value and outflow.value:
            loss_percent = (inflow.value - outflow.value) / inflow.value * 100
            
            if loss_percent > 30:  # تلفات بیش از 30%
                alert = EarlyWarningAlert(
                    alert_type="water_stress",
                    severity="warning",
                    title=f"تنش آبی - تلفات {loss_percent:.0f}%",
                    description=f"تلفات آب بین ورودی و خروجی {loss_percent:.0f}% است که نشان‌دهنده نشت یا تبخیر شدید است.",
                    affected_area="شبکه آبرسانی",
                    trigger_data={
                        "inflow_m3s": inflow.value,
                        "outflow_m3s": outflow.value,
                        "loss_percent": loss_percent
                    },
                    confidence_level=0.80,
                    expected_impact_at=datetime.utcnow() + timedelta(days=7),
                    expires_at=datetime.utcnow() + timedelta(days=14),
                    recommended_actions=[
                        "بررسی نشتی احتمالی",
                        "عایق‌بندی کانال‌ها",
                        "بهینه‌سازی مصرف",
                        "تعمیرات فوری"
                    ]
                )
                session.add(alert)
                logger.warning(f"💧 Water stress alert: {loss_percent:.0f}% loss")
    
    async def _generate_flood_work_order(self, session: AsyncSession, alert: EarlyWarningAlert):
        """تولید خودکار دستور کار برای سیلاب"""
        work_order = MaintenanceWorkOrder(
            work_order_number=f"WO-FLOOD-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            title="اقدامات فوری پیشگیری از سیلاب",
            description=f"هشدار سیلاب با شدت {alert.trigger_data.get('rainfall_mm_hr', 0)}mm/hr. اقدامات فوری لازم است.",
            work_type="emergency_prevention",
            priority="urgent",
            structure_name="حوضه آبریز پایین‌دست",
            created_by="auto_ews",
            due_date=datetime.utcnow() + timedelta(hours=2),
            alert_id=alert.id,
            required_tools=["بیل", "کیسه شن", "پمپ آب", "بی‌سیم"],
            required_materials=["کیسه شن 500 عدد", "لوله PVC 10 متر"],
            estimated_duration_hours=4,
            estimated_cost=5000000  # 5 میلیون تومان
        )
        session.add(work_order)
        await session.flush()
        
        alert.auto_generated_work_orders = [work_order.id]
        logger.info(f"📝 Flood work order generated: {work_order.work_order_number}")
    
    async def _generate_inspection_work_order(self, session: AsyncSession, alert: EarlyWarningAlert):
        """تولید خودکار دستور کار بازرسی"""
        work_order = MaintenanceWorkOrder(
            work_order_number=f"WO-INSP-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            title="بازرسی فوری سازه",
            description=f"تغییر ناگهانی در دبی detected. بازرسی فوری برای بررسی علت لازم است.",
            work_type="inspection",
            priority="high",
            structure_name="سازه آبخیزداری",
            created_by="auto_ews",
            due_date=datetime.utcnow() + timedelta(hours=6),
            alert_id=alert.id,
            required_tools=["دوربین", "متر لیزری", "چراغ قوه", "دفترچه بازرسی"],
            estimated_duration_hours=2,
            estimated_cost=500000  # 500 هزار تومان
        )
        session.add(work_order)
        await session.flush()
        
        alert.auto_generated_work_orders = [work_order.id]
        logger.info(f"📝 Inspection work order generated: {work_order.work_order_number}")
    
    def stop(self):
        """توقف موتور"""
        self.running = False
        logger.info("🛑 Early Warning Engine stopped")


# Singleton instance
ews_engine = EarlyWarningEngine()
