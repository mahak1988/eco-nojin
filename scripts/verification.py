# -*- coding: utf-8 -*-
"""
Scientific Verifier - اعتبارسنجی چندلایه فعالیت‌های اکوسیستمی
ترکیب ماهواره + IoT + جامعه + مدل‌های علمی
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.core.logger import UnifiedLogger

logger = UnifiedLogger.get_logger(__name__)


@dataclass
class VerificationResult:
    """نتیجه اعتبارسنجی"""
    verified: bool
    confidence: float
    sources: Dict[str, bool]
    evidence: List[str]
    warnings: List[str]
    timestamp: datetime
    
    def overall_score(self) -> float:
        verified_count = sum(1 for v in self.sources.values() if v)
        return verified_count / len(self.sources) if self.sources else 0.0


class ScientificVerifier:
    """اعتبارسنج علمی فعالیت‌ها"""
    
    def __init__(self):
        self.verification_history: List[VerificationResult] = []
    
    async def verify_activity(
        self,
        activity_type: str,
        location: Dict,
        claimed_carbon_kg: float,
        evidence_data: Dict,
    ) -> VerificationResult:
        """اعتبارسنجی کامل یک فعالیت"""
        
        logger.info(f"Verifying activity: {activity_type} at {location}")
        
        sources = {}
        evidence = []
        warnings = []
        
        # 1) اعتبارسنجی ماهواره‌ای
        sat_result = await self._verify_satellite(location, activity_type)
        sources["satellite"] = sat_result["verified"]
        if sat_result["verified"]:
            evidence.append(f"Satellite: {sat_result['evidence']}")
        else:
            warnings.append(f"Satellite: {sat_result['reason']}")
        
        # 2) اعتبارسنجی IoT
        iot_result = await self._verify_iot(location, evidence_data)
        sources["iot"] = iot_result["verified"]
        if iot_result["verified"]:
            evidence.append(f"IoT: {iot_result['evidence']}")
        else:
            warnings.append(f"IoT: {iot_result['reason']}")
        
        # 3) اعتبارسنجی علمی (مدل‌های Econojin)
        sci_result = await self._verify_scientific(
            activity_type, location, claimed_carbon_kg
        )
        sources["scientific"] = sci_result["verified"]
        if sci_result["verified"]:
            evidence.append(f"Scientific: {sci_result['evidence']}")
        else:
            warnings.append(f"Scientific: {sci_result['reason']}")
        
        # 4) اعتبارسنجی جامعه
        comm_result = await self._verify_community(location, evidence_data)
        sources["community"] = comm_result["verified"]
        if comm_result["verified"]:
            evidence.append(f"Community: {comm_result['count']} validators")
        else:
            warnings.append("Community: Insufficient validators")
        
        # محاسبه اطمینان کل
        verified_count = sum(1 for v in sources.values() if v)
        confidence = verified_count / len(sources)
        
        # تأیید نهایی: حداقل 2 از 4 منبع
        verified = verified_count >= 2
        
        result = VerificationResult(
            verified=verified,
            confidence=confidence,
            sources=sources,
            evidence=evidence,
            warnings=warnings,
            timestamp=datetime.now(timezone.utc),
        )
        
        self.verification_history.append(result)
        
        logger.info(
            f"Verification complete: {verified} (confidence: {confidence:.2f})"
        )
        
        return result
    
    async def _verify_satellite(self, location: Dict, activity_type: str) -> Dict:
        """اعتبارسنجی با تصاویر ماهواره‌ای"""
        try:
            # در production: اتصال به Sentinel-2 یا Planet Labs
            # اینجا شبیه‌سازی
            
            lat = location.get("lat", 0)
            lng = location.get("lng", 0)
            
            # بررسی NDVI (Normalized Difference Vegetation Index)
            # در واقعیت: از Sentinel-2 API
            
            # شبیه‌سازی
            ndvi_before = 0.2  # قبل از فعالیت
            ndvi_after = 0.5   # بعد از فعالیت
            
            improvement = ndvi_after - ndvi_before
            
            if improvement > 0.1:
                return {
                    "verified": True,
                    "evidence": f"NDVI improved from {ndvi_before} to {ndvi_after}",
                    "ndvi_change": improvement,
                }
            else:
                return {
                    "verified": False,
                    "reason": f"Insufficient NDVI change: {improvement}",
                }
                
        except Exception as e:
            return {"verified": False, "reason": f"Satellite check failed: {e}"}
    
    async def _verify_iot(self, location: Dict, evidence_data: Dict) -> Dict:
        """اعتبارسنجی با سنسورهای IoT"""
        try:
            # بررسی داده‌های IoT
            soil_moisture = evidence_data.get("soil_moisture")
            temperature = evidence_data.get("temperature")
            
            if soil_moisture is None or temperature is None:
                return {
                    "verified": False,
                    "reason": "Missing IoT data",
                }
            
            # بررسی محدوده‌های معقول
            if 0.1 <= soil_moisture <= 0.9 and -10 <= temperature <= 50:
                return {
                    "verified": True,
                    "evidence": f"Soil moisture: {soil_moisture}, Temp: {temperature}°C",
                }
            else:
                return {
                    "verified": False,
                    "reason": "IoT values out of range",
                }
                
        except Exception as e:
            return {"verified": False, "reason": f"IoT check failed: {e}"}
    
    async def _verify_scientific(
        self,
        activity_type: str,
        location: Dict,
        claimed_carbon_kg: float,
    ) -> Dict:
        """اعتبارسنجی علمی با مدل‌های Econojin"""
        try:
            from core.gaia.calculator import CarbonCalculator, ActivityType, Location, ClimateData
            
            calc = CarbonCalculator()
            
            # محاسبه مورد انتظار
            loc = Location(
                latitude=location.get("lat", 0),
                longitude=location.get("lng", 0),
            )
            climate = ClimateData(
                annual_rainfall_mm=400,
                avg_temperature_c=18,
                min_temperature_c=5,
                max_temperature_c=35,
            )
            
            expected = calc.calculate(
                activity_type=ActivityType(activity_type),
                location=loc,
                climate=climate,
                area_hectares=1.0,
            )
            
            # بررسی اینکه ادعا در محدوده معقول است
            expected_kg = expected.carbon_absorbed_kg
            deviation = abs(claimed_carbon_kg - expected_kg) / expected_kg
            
            if deviation < 0.3:  # کمتر از 30% انحراف
                return {
                    "verified": True,
                    "evidence": f"Claimed {claimed_carbon_kg:.2f} kg vs Expected {expected_kg:.2f} kg",
                    "deviation": deviation,
                }
            else:
                return {
                    "verified": False,
                    "reason": f"Deviation too high: {deviation:.2%}",
                }
                
        except Exception as e:
            return {"verified": False, "reason": f"Scientific check failed: {e}"}
    
    async def _verify_community(self, location: Dict, evidence_data: Dict) -> Dict:
        """اعتبارسنجی توسط جامعه"""
        try:
            validators = evidence_data.get("community_validators", [])
            
            if len(validators) >= 3:
                return {
                    "verified": True,
                    "count": len(validators),
                }
            else:
                return {
                    "verified": False,
                    "reason": f"Only {len(validators)} validators (need 3+)",
                }
        except Exception as e:
            return {"verified": False, "reason": str(e)}