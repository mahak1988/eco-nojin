# apps/backend-api/app/land_soil_water/analysis.py

from __future__ import annotations

from typing import Dict, List

from app.land_soil_water.schemas import (
    AnalysisDetail,
    IndicatorCode,
)


class SeverityLevel(str):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class IndicatorAssessment:
    def __init__(
        self,
        indicator: IndicatorCode,
        value: float,
        severity: str,
        message_fa: str,
        message_en: str,
    ) -> None:
        self.indicator = indicator
        self.value = value
        self.severity = severity
        self.message_fa = message_fa
        self.message_en = message_en


class AnalysisRecommendations:
    def __init__(
        self,
        overall_risk_fa: str,
        overall_risk_en: str,
        indicator_assessments: List[IndicatorAssessment],
        management_recommendations_fa: List[str],
        management_recommendations_en: List[str],
    ) -> None:
        self.overall_risk_fa = overall_risk_fa
        self.overall_risk_en = overall_risk_en
        self.indicator_assessments = indicator_assessments
        self.management_recommendations_fa = management_recommendations_fa
        self.management_recommendations_en = management_recommendations_en


# آستانه‌های اولیه مبتنی بر ادبیات UNCCD/FAO و مطالعات فرسایش؛
# در صورت نیاز می‌توان آن‌ها را در DB قابل تنظیم کرد. [file:21]
SOIL_LOSS_THRESHOLDS = {
    SeverityLevel.LOW: 2.0,        # t/ha/year
    SeverityLevel.MODERATE: 5.0,
    SeverityLevel.HIGH: 10.0,
}

EROSION_RISK_THRESHOLDS = {
    SeverityLevel.LOW: 0.2,
    SeverityLevel.MODERATE: 0.4,
    SeverityLevel.HIGH: 0.7,
}

RUNOFF_THRESHOLDS = {
    SeverityLevel.LOW: 50.0,      # mm
    SeverityLevel.MODERATE: 150.0,
    SeverityLevel.HIGH: 300.0,
}


def _classify_soil_loss(value: float) -> str:
    if value < SOIL_LOSS_THRESHOLDS[SeverityLevel.LOW]:
        return SeverityLevel.LOW
    if value < SOIL_LOSS_THRESHOLDS[SeverityLevel.MODERATE]:
        return SeverityLevel.MODERATE
    if value < SOIL_LOSS_THRESHOLDS[SeverityLevel.HIGH]:
        return SeverityLevel.HIGH
    return SeverityLevel.VERY_HIGH


def _classify_erosion_risk(value: float) -> str:
    if value < EROSION_RISK_THRESHOLDS[SeverityLevel.LOW]:
        return SeverityLevel.LOW
    if value < EROSION_RISK_THRESHOLDS[SeverityLevel.MODERATE]:
        return SeverityLevel.MODERATE
    if value < EROSION_RISK_THRESHOLDS[SeverityLevel.HIGH]:
        return SeverityLevel.HIGH
    return SeverityLevel.VERY_HIGH


def _classify_runoff(value: float) -> str:
    if value < RUNOFF_THRESHOLDS[SeverityLevel.LOW]:
        return SeverityLevel.LOW
    if value < RUNOFF_THRESHOLDS[SeverityLevel.MODERATE]:
        return SeverityLevel.MODERATE
    if value < RUNOFF_THRESHOLDS[SeverityLevel.HIGH]:
        return SeverityLevel.HIGH
    return SeverityLevel.VERY_HIGH


def _severity_rank(level: str) -> int:
    order = {
        SeverityLevel.LOW: 0,
        SeverityLevel.MODERATE: 1,
        SeverityLevel.HIGH: 2,
        SeverityLevel.VERY_HIGH: 3,
    }
    return order.get(level, 0)


def assess_analysis(detail: AnalysisDetail) -> AnalysisRecommendations:
    """تحلیل کمی شاخص‌ها و تولید توصیه‌های پایه مدیریت آب و خاک."""
    indicators_avg: Dict[IndicatorCode, float] = detail.summary.indicators_avg or {}

    assessments: List[IndicatorAssessment] = []

    # فرسایش خاک
    if IndicatorCode.SOIL_LOSS_T_HA in indicators_avg:
        value = indicators_avg[IndicatorCode.SOIL_LOSS_T_HA]
        severity = _classify_soil_loss(value)
        msg_fa = f"برآورد فرسایش خاک {value:.2f} تن در هکتار در سال است."
        msg_en = f"Estimated soil loss is {value:.2f} t/ha/year."
        assessments.append(
            IndicatorAssessment(
                indicator=IndicatorCode.SOIL_LOSS_T_HA,
                value=value,
                severity=severity,
                message_fa=msg_fa,
                message_en=msg_en,
            )
        )

    # شاخص ریسک فرسایش
    if IndicatorCode.EROSION_RISK_INDEX in indicators_avg:
        value = indicators_avg[IndicatorCode.EROSION_RISK_INDEX]
        severity = _classify_erosion_risk(value)
        msg_fa = f"شاخص ریسک فرسایش {value:.2f} (بدون‌بعد) است."
        msg_en = f"Erosion risk index is {value:.2f} (dimensionless)."
        assessments.append(
            IndicatorAssessment(
                indicator=IndicatorCode.EROSION_RISK_INDEX,
                value=value,
                severity=severity,
                message_fa=msg_fa,
                message_en=msg_en,
            )
        )

    # رواناب
    if IndicatorCode.RUNOFF_MM in indicators_avg:
        value = indicators_avg[IndicatorCode.RUNOFF_MM]
        severity = _classify_runoff(value)
        msg_fa = f"حجم رواناب سطحی تجمعی {value:.1f} میلی‌متر در دوره تحلیل است."
        msg_en = f"Cumulative surface runoff is {value:.1f} mm over the analysis period."
        assessments.append(
            IndicatorAssessment(
                indicator=IndicatorCode.RUNOFF_MM,
                value=value,
                severity=severity,
                message_fa=msg_fa,
                message_en=msg_en,
            )
        )

    # تعیین سطح ریسک کلی
    overall_level = SeverityLevel.LOW
    if assessments:
        overall_level = max(
            (a.severity for a in assessments), key=_severity_rank, default=SeverityLevel.LOW
        )

    if overall_level == SeverityLevel.LOW:
        overall_fa = "وضعیت کلی فرسایش و رواناب در این واحد در محدوده قابل قبول است."
        overall_en = "Overall erosion and runoff risk is within acceptable limits for this land unit."
    elif overall_level == SeverityLevel.MODERATE:
        overall_fa = "ریسک فرسایش و رواناب در حد متوسط است و نیاز به اقدامات حفاظتی ملایم دارد."
        overall_en = "Erosion and runoff risk is moderate and requires basic conservation measures."
    elif overall_level == SeverityLevel.HIGH:
        overall_fa = "ریسک فرسایش و رواناب بالاست و نیاز به برنامه مدیریت حفاظتی جدی دارد."
        overall_en = "Erosion and runoff risk is high and requires robust conservation management."
    else:
        overall_fa = "ریسک فرسایش و رواناب بسیار بالاست؛ این واحد در وضعیت بحرانی قرار دارد."
        overall_en = "Erosion and runoff risk is very high; this land unit is in a critical state."

    # توصیه‌های مدیریتی پایه
    recs_fa: List[str] = []
    recs_en: List[str] = []

    if overall_level in {SeverityLevel.MODERATE, SeverityLevel.HIGH, SeverityLevel.VERY_HIGH}:
        recs_fa.append(
            "تقویت پوشش گیاهی دائمی و کاهش دوره‌های خاک برهنه (افزایش پوشش گیاهی، کشت حفاظتی)."
        )
        recs_en.append(
            "Increase permanent vegetative cover and minimize bare soil periods (conservation tillage, cover crops)."
        )

    if _severity_rank(overall_level) >= _severity_rank(SeverityLevel.HIGH):
        recs_fa.append(
            "استفاده از عملیات عمرانی حفاظتی مانند کشت روی خطوط تراز، بانکت و تراس‌بندی در شیب‌های بالا."
        )
        recs_en.append(
            "Implement structural measures such as contour farming, bunds, and terracing on steeper slopes."
        )

    if IndicatorCode.SOIL_WATER_CONTENT_MM in indicators_avg:
        swc = indicators_avg[IndicatorCode.SOIL_WATER_CONTENT_MM]
        if swc < 50:
            recs_fa.append(
                "افزایش ذخیره رطوبت خاک از طریق مالچ‌پاشی، افزایش ماده آلی و مدیریت بقایای گیاهی."
            )
            recs_en.append(
                "Improve soil water storage through mulching, increasing organic matter, and residue management."
            )

    if IndicatorCode.INFILTRATION_MM in indicators_avg:
        infil = indicators_avg[IndicatorCode.INFILTRATION_MM]
        if infil < RUNOFF_THRESHOLDS[SeverityLevel.MODERATE]:
            recs_fa.append(
                "افزایش نفوذ آب با کاهش تراکم خاک، شخم حداقلی و ایجاد ریزساختارهای سطحی مناسب."
            )
            recs_en.append(
                "Enhance infiltration by reducing soil compaction, applying minimum tillage, and improving surface micro-relief."
            )

    return AnalysisRecommendations(
        overall_risk_fa=overall_fa,
        overall_risk_en=overall_en,
        indicator_assessments=assessments,
        management_recommendations_fa=recs_fa,
        management_recommendations_en=recs_en,
    )