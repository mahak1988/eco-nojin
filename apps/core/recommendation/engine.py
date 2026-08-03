"""ARE — Adaptive Recommendation Engine (ENOS-ISA).

Every data point → action + scenario + prevention + confidence.
Farmer-facing text is free and simple language.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, List, Optional


class ActionPriority(str, Enum):
    CRITICAL = "critical"
    URGENT = "urgent"
    IMPORTANT = "important"
    ROUTINE = "routine"
    INFORMATIONAL = "info"


@dataclass
class Recommendation:
    action: str
    scientific_basis: str
    scenario_if_action: str
    scenario_if_no_action: str
    prevention: str
    priority: str
    confidence: float
    data_sources: List[str]
    simple_explanation: str
    estimated_impact: str
    cost_estimate: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AdaptiveRecommendationEngine:
    def generate_recommendations(
        self,
        farm_profile: Dict[str, Any],
        data_input: Dict[str, Any],
        model_output: Dict[str, Any],
        weather_forecast: Dict[str, Any],
        language: str = "fa",
    ) -> List[Recommendation]:
        out: List[Recommendation] = []
        irr = self._irrigation(farm_profile, model_output, weather_forecast)
        if irr:
            out.append(irr)
        drought = self._drought(model_output)
        if drought:
            out.append(drought)
        order = {
            ActionPriority.CRITICAL.value: 0,
            ActionPriority.URGENT.value: 1,
            ActionPriority.IMPORTANT.value: 2,
            ActionPriority.ROUTINE.value: 3,
            ActionPriority.INFORMATIONAL.value: 4,
        }
        out.sort(key=lambda r: order.get(r.priority, 9))
        return out

    def _irrigation(
        self,
        farm_profile: Dict[str, Any],
        model_output: Dict[str, Any],
        weather_forecast: Dict[str, Any],
    ) -> Optional[Recommendation]:
        sm = model_output.get("soil_moisture_vwc")
        if sm is None:
            return None
        sm = float(sm)
        fc = float(farm_profile.get("field_capacity", 0.30))
        pwp = float(farm_profile.get("wilting_point", 0.15))
        p = float(farm_profile.get("depletion_fraction", 0.55))
        critical = pwp + p * (fc - pwp)
        conf = float(model_output.get("confidence", 0.75))
        rain3 = float(sum(weather_forecast.get("precipitation_3d", [0, 0, 0])[:3]))

        if sm < pwp:
            return Recommendation(
                action="آبیاری فوری و سنگین (حداقل ۴۰ میلی‌متر) در ۶ ساعت آینده",
                scientific_basis=f"θ={sm:.3f} < θ_PWP={pwp:.3f}",
                scenario_if_action="احیای گیاه در ۲۴–۴۸ ساعت؛ کاهش عملکرد محدود",
                scenario_if_no_action="خسارت شدید تا غیرقابل جبران",
                prevention="پایش روزانه رطوبت خاک",
                priority=ActionPriority.CRITICAL.value,
                confidence=conf,
                data_sources=["soil_moisture"],
                simple_explanation="گیاه در حال خشک شدن است — فوراً آبیاری کنید",
                estimated_impact="جلوگیری از ۵۰–۸۰٪ خسارت",
                cost_estimate="رایگان (فقط آب)",
            )
        if sm < critical:
            if rain3 > 15:
                return Recommendation(
                    action="آبیاری را ۲–۳ روز به تعویق بیندازید — بارش پیش‌بینی شده",
                    scientific_basis=f"θ={sm:.3f} نزدیک θ_crit={critical:.3f}؛ بارش۳روز={rain3:.0f}mm",
                    scenario_if_action="صرفه‌جویی آب",
                    scenario_if_no_action="بدون خسارت در صورت تحقق بارش",
                    prevention="همیشه پیش‌بینی هوا را قبل از آبیاری ببینید",
                    priority=ActionPriority.IMPORTANT.value,
                    confidence=min(0.85, conf + 0.05),
                    data_sources=["soil_moisture", "weather_forecast"],
                    simple_explanation="باران می‌آید — آبیاری نکنید",
                    estimated_impact="صرفه‌جویی ۲۰–۳۰mm آب",
                    cost_estimate="رایگان",
                )
            return Recommendation(
                action="آبیاری در ۱–۳ روز آینده بر اساس حجم محاسبه شده",
                scientific_basis=f"θ={sm:.3f} < θ_crit={critical:.3f}",
                scenario_if_action="حفظ عملکرد",
                scenario_if_no_action="شروع تنش آبی و کاهش عملکرد",
                prevention="آبیاری بر اساس رطوبت خاک نه تقویم ثابت",
                priority=ActionPriority.URGENT.value,
                confidence=conf,
                data_sources=["soil_moisture", "et0"],
                simple_explanation="زمین تشنه است — به‌زودی آبیاری کنید",
                estimated_impact="جلوگیری از ۱۰–۲۰٪ کاهش عملکرد",
                cost_estimate="رایگان (فقط آب)",
            )
        if sm > fc:
            return Recommendation(
                action="آبیاری را متوقف کنید — خطر اشباع و بیماری قارچی",
                scientific_basis=f"θ={sm:.3f} > θ_FC={fc:.3f}",
                scenario_if_action="کاهش بیماری و هدررفت کود",
                scenario_if_no_action="افزایش بیماری قارچی",
                prevention="آبیاری بر اساس رطوبت + زهکش",
                priority=ActionPriority.URGENT.value,
                confidence=conf,
                data_sources=["soil_moisture"],
                simple_explanation="زمین خیلی خیس است — آبیاری نکنید",
                estimated_impact="جلوگیری از بیماری",
                cost_estimate="رایگان",
            )
        return Recommendation(
            action="شرایط بهینه — آبیاری لازم نیست؛ پایش تا ۳ روز",
            scientific_basis=f"θ={sm:.3f} در بازه [{critical:.3f}, {fc:.3f}]",
            scenario_if_action="N/A",
            scenario_if_no_action="عملکرد بهینه",
            prevention="ادامه پایش",
            priority=ActionPriority.INFORMATIONAL.value,
            confidence=conf,
            data_sources=["soil_moisture"],
            simple_explanation="همه‌چیز خوب است — فعلاً آبیاری نکنید",
            estimated_impact="حفظ عملکرد",
            cost_estimate="رایگان",
        )

    def _drought(self, model_output: Dict[str, Any]) -> Optional[Recommendation]:
        spi = model_output.get("spi_3month")
        if spi is None:
            return None
        spi_f = float(spi)
        if spi_f > -1.5:
            return None
        return Recommendation(
            action="خشکسالی شدید — بیمه پارامتریک و بازنگری الگوی کشت",
            scientific_basis=f"SPI_3m={spi_f:.2f}",
            scenario_if_action="کاهش خسارت و دسترسی به غرامت",
            scenario_if_no_action="خسارت سنگین",
            prevention="تنوع کشت + ذخیره آب + بیمه",
            priority=ActionPriority.CRITICAL.value,
            confidence=0.85,
            data_sources=["spi"],
            simple_explanation="خشکسالی شدید — اقدامات اضطراری",
            estimated_impact="کاهش خسارت ۶۰–۸۰٪",
            cost_estimate="رایگان (بیمه پارامتریک در صورت پوشش)",
        )
