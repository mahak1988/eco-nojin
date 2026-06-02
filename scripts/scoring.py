# -*- coding: utf-8 -*-
"""
Impact Scoring - سیستم امتیازدهی تأثیر اکوسیستمی
محاسبه امتیاز جامع بر اساس چندین فاکتور
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.core.logger import UnifiedLogger

logger = UnifiedLogger.get_logger(__name__)


@dataclass
class ImpactScore:
    """امتیاز تأثیر اکوسیستمی"""
    total_score: float  # 0-100
    carbon_score: float  # 0-100
    biodiversity_score: float  # 0-100
    water_score: float  # 0-100
    soil_score: float  # 0-100
    community_score: float  # 0-100
    verification_score: float  # 0-100
    
    # رتبه
    grade: str  # A+, A, B, C, D, F
    percentile: float  # موقعیت در بین همه فعالیت‌ها
    
    # پاداش
    bonus_multiplier: float  # ضریب پاداش
    
    def to_dict(self) -> Dict:
        return {
            "total_score": round(self.total_score, 2),
            "components": {
                "carbon": round(self.carbon_score, 2),
                "biodiversity": round(self.biodiversity_score, 2),
                "water": round(self.water_score, 2),
                "soil": round(self.soil_score, 2),
                "community": round(self.community_score, 2),
                "verification": round(self.verification_score, 2),
            },
            "grade": self.grade,
            "percentile": round(self.percentile, 2),
            "bonus_multiplier": round(self.bonus_multiplier, 2),
        }


class ImpactScorer:
    """
    سیستم امتیازدهی جامع تأثیر اکوسیستمی
    
    امتیاز بر اساس ۶ فاکتور اصلی:
    1. Carbon (40%) - جذب کربن
    2. Biodiversity (15%) - تنوع زیستی
    3. Water (15%) - تأثیر بر منابع آب
    4. Soil (10%) - کیفیت خاک
    5. Community (10%) - تأثیر اجتماعی
    6. Verification (10%) - سطح اعتبارسنجی
    """
    
    WEIGHTS = {
        "carbon": 0.40,
        "biodiversity": 0.15,
        "water": 0.15,
        "soil": 0.10,
        "community": 0.10,
        "verification": 0.10,
    }
    
    # گونه‌های بومی امتیاز بالاتر
    NATIVE_SPECIES_BONUS = {
        "quercus_persica": 1.3,      # بلوط ایرانی
        "amygdalus_scoparia": 1.25,  # بادام کوهی
        "pistacia_atlantica": 1.25,  # بنه
        "juniperus_excelsa": 1.2,    # ارس
    }
    
    GRADE_THRESHOLDS = [
        (95, "A+"), (90, "A"), (85, "A-"),
        (80, "B+"), (75, "B"), (70, "B-"),
        (65, "C+"), (60, "C"), (55, "C-"),
        (50, "D"), (0, "F"),
    ]
    
    def __init__(self):
        self.historical_scores: List[ImpactScore] = []
    
    def calculate(
        self,
        carbon_kg: float,
        activity_type: str,
        area_hectares: float,
        species: Optional[str] = None,
        location: Optional[Dict] = None,
        verification_sources: Optional[List[str]] = None,
        community_validators: int = 0,
        biodiversity_index: float = 0.5,
        soil_improvement: float = 0.0,
        water_impact_liters: float = 0.0,
    ) -> ImpactScore:
        """محاسبه امتیاز جامع تأثیر"""
        
        logger.info(f"Calculating impact score for {activity_type}")
        
        # 1) Carbon Score (0-100)
        carbon_score = self._score_carbon(carbon_kg, area_hectares, species)
        
        # 2) Biodiversity Score
        biodiversity_score = self._score_biodiversity(
            activity_type, species, biodiversity_index
        )
        
        # 3) Water Score
        water_score = self._score_water(water_impact_liters, activity_type)
        
        # 4) Soil Score
        soil_score = self._score_soil(soil_improvement, activity_type)
        
        # 5) Community Score
        community_score = self._score_community(community_validators, activity_type)
        
        # 6) Verification Score
        verification_score = self._score_verification(verification_sources or [])
        
        # محاسبه امتیاز کل (وزن‌دار)
        total = (
            carbon_score * self.WEIGHTS["carbon"] +
            biodiversity_score * self.WEIGHTS["biodiversity"] +
            water_score * self.WEIGHTS["water"] +
            soil_score * self.WEIGHTS["soil"] +
            community_score * self.WEIGHTS["community"] +
            verification_score * self.WEIGHTS["verification"]
        )
        
        # تعیین رتبه
        grade = self._calculate_grade(total)
        
        # محاسبه percentile (مقایسه با تاریخچه)
        percentile = self._calculate_percentile(total)
        
        # محاسبه bonus multiplier
        bonus = self._calculate_bonus(total, grade)
        
        score = ImpactScore(
            total_score=total,
            carbon_score=carbon_score,
            biodiversity_score=biodiversity_score,
            water_score=water_score,
            soil_score=soil_score,
            community_score=community_score,
            verification_score=verification_score,
            grade=grade,
            percentile=percentile,
            bonus_multiplier=bonus,
        )
        
        self.historical_scores.append(score)
        
        logger.info(
            f"Impact score: {total:.1f}/100 ({grade}), "
            f"bonus: {bonus:.2f}x"
        )
        
        return score
    
    def _score_carbon(
        self,
        carbon_kg: float,
        area_hectares: float,
        species: Optional[str]
    ) -> float:
        """امتیاز کربن (0-100)"""
        if area_hectares <= 0:
            return 0.0
        
        # چگالی کربن در هکتار
        density = carbon_kg / area_hectares
        
        # امتیاز بر اساس چگالی (max ~50 ton/ha)
        base_score = min(100.0, (density / 50000) * 100)
        
        # bonus گونه بومی
        if species and species in self.NATIVE_SPECIES_BONUS:
            base_score *= self.NATIVE_SPECIES_BONUS[species]
        
        return min(100.0, base_score)
    
    def _score_biodiversity(
        self,
        activity_type: str,
        species: Optional[str],
        biodiversity_index: float
    ) -> float:
        """امتیاز تنوع زیستی"""
        
        # امتیاز پایه بر اساس نوع فعالیت
        base_scores = {
            "mangrove_planting": 90,
            "wetland_restoration": 85,
            "agroforestry": 80,
            "tree_planting": 70,
            "grassland_restoration": 65,
            "soil_regeneration": 60,
            "urban_greening": 50,
        }
        
        base = base_scores.get(activity_type, 60)
        
        # تعدیل بر اساس biodiversity index
        adjusted = base * (0.5 + biodiversity_index * 0.5)
        
        # bonus گونه بومی
        if species and species in self.NATIVE_SPECIES_BONUS:
            adjusted *= 1.1
        
        return min(100.0, adjusted)
    
    def _score_water(self, water_liters: float, activity_type: str) -> float:
        """امتیاز تأثیر آبی"""
        
        # پایه بر اساس نوع فعالیت
        base_scores = {
            "wetland_restoration": 95,
            "mangrove_planting": 90,
            "agroforestry": 70,
            "tree_planting": 65,
            "grassland_restoration": 60,
            "soil_regeneration": 55,
            "urban_greening": 45,
        }
        
        base = base_scores.get(activity_type, 50)
        
        # bonus برای حجم آب
        if water_liters > 0:
            water_bonus = min(20.0, (water_liters / 10000) * 10)
            base += water_bonus
        
        return min(100.0, base)
    
    def _score_soil(self, improvement: float, activity_type: str) -> float:
        """امتیاز خاک"""
        
        base_scores = {
            "soil_regeneration": 95,
            "agroforestry": 80,
            "grassland_restoration": 75,
            "tree_planting": 65,
            "wetland_restoration": 60,
            "mangrove_planting": 55,
            "urban_greening": 40,
        }
        
        base = base_scores.get(activity_type, 50)
        
        # bonus برای بهبود واقعی
        if improvement > 0:
            soil_bonus = min(20.0, improvement * 40)  # 0.5 -> 20
            base += soil_bonus
        
        return min(100.0, base)
    
    def _score_community(self, validators: int, activity_type: str) -> float:
        """امتیاز اجتماعی"""
        
        # پایه: مشارکت جامعه
        if validators == 0:
            return 30.0
        elif validators < 3:
            return 50.0
        elif validators < 10:
            return 75.0
        elif validators < 30:
            return 90.0
        else:
            return 100.0
    
    def _score_verification(self, sources: List[str]) -> float:
        """امتیاز اعتبارسنجی"""
        
        if not sources:
            return 20.0
        
        # وزن هر منبع
        source_weights = {
            "satellite": 35,
            "iot": 30,
            "scientific": 25,
            "community": 10,
        }
        
        score = sum(source_weights.get(s, 0) for s in sources)
        return min(100.0, score)
    
    def _calculate_grade(self, score: float) -> str:
        """تعیین رتبه از روی امتیاز"""
        for threshold, grade in self.GRADE_THRESHOLDS:
            if score >= threshold:
                return grade
        return "F"
    
    def _calculate_percentile(self, score: float) -> float:
        """محاسبه percentile نسبت به تاریخچه"""
        if not self.historical_scores:
            return 50.0
        
        below = sum(1 for s in self.historical_scores if s.total_score < score)
        total = len(self.historical_scores)
        
        return (below / total) * 100 if total > 0 else 50.0
    
    def _calculate_bonus(self, score: float, grade: str) -> float:
        """محاسبه ضریب پاداش"""
        
        # بر اساس رتبه
        grade_bonus = {
            "A+": 2.0, "A": 1.75, "A-": 1.5,
            "B+": 1.3, "B": 1.15, "B-": 1.05,
            "C+": 1.0, "C": 0.95, "C-": 0.9,
            "D": 0.8, "F": 0.5,
        }
        
        return grade_bonus.get(grade, 1.0)
    
    def compare_activities(
        self,
        activities: List[Dict]
    ) -> List[Dict]:
        """مقایسه چند فعالیت"""
        
        scored = []
        for activity in activities:
            score = self.calculate(**activity)
            scored.append({
                "activity": activity,
                "score": score.to_dict(),
            })
        
        # مرتب‌سازی بر اساس امتیاز
        return sorted(scored, key=lambda x: x["score"]["total_score"], reverse=True)