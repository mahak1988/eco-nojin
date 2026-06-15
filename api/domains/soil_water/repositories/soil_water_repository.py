"""Soil & Water Repository with database integration."""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from .models.db_models import SoilAnalysisDB, ErosionRiskDB
from .models.soil_water_models import SoilAnalysis, ErosionRisk


class SoilWaterRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def save_soil_analysis(self, analysis: SoilAnalysis) -> bool:
        """ذخیره تحلیل خاک در پایگاه داده"""
        db_obj = SoilAnalysisDB(
            location_lat=analysis.location_lat,
            location_lon=analysis.location_lon,
            soil_type=analysis.soil_type,
            organic_matter_percent=analysis.organic_matter_percent,
            moisture_content=analysis.moisture_content,
            ph_level=analysis.ph_level,
            timestamp=analysis.timestamp
        )
        self.db.add(db_obj)
        self.db.commit()
        return True
    
    def get_erosion_risk(
        self,
        lat: float,
        lon: float
    ) -> Optional[ErosionRisk]:
        """دریافت ریسک فرسایش از پایگاه داده"""
        result = self.db.query(ErosionRiskDB).filter(
            ErosionRiskDB.location_lat == lat,
            ErosionRiskDB.location_lon == lon
        ).order_by(ErosionRiskDB.timestamp.desc()).first()
        
        if result:
            return ErosionRisk(
                location_lat=result.location_lat,
                location_lon=result.location_lon,
                risk_level=result.risk_level,
                rusle_value=result.rusle_value,
                contributing_factors=[]
            )
        return None
    
    def save_erosion_risk(self, risk: ErosionRisk) -> bool:
        """ذخیره ریسک فرسایش"""
        db_obj = ErosionRiskDB(
            location_lat=risk.location_lat,
            location_lon=risk.location_lon,
            risk_level=risk.risk_level,
            rusle_value=risk.rusle_value,
            timestamp=datetime.utcnow()
        )
        self.db.add(db_obj)
        self.db.commit()
        return True
