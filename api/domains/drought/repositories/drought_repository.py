"""Drought Repository with database integration."""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from .models.db_models import DroughtIndexDB, SPEIValueDB
from .models.drought_models import DroughtIndex, SPEIValue


class DroughtRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_drought_index(
        self, 
        lat: float, 
        lon: float, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[DroughtIndex]:
        """دریافت شاخص‌های خشکسالی از پایگاه داده"""
        results = self.db.query(DroughtIndexDB).filter(
            DroughtIndexDB.location_lat == lat,
            DroughtIndexDB.location_lon == lon,
            DroughtIndexDB.timestamp >= start_date,
            DroughtIndexDB.timestamp <= end_date
        ).all()
        
        return [
            DroughtIndex(
                name=r.name,
                value=r.value,
                timestamp=r.timestamp,
                location_lat=r.location_lat,
                location_lon=r.location_lon,
                severity=r.severity
            )
            for r in results
        ]
    
    def save_spei_value(self, spei: SPEIValue) -> bool:
        """ذخیره مقدار SPEI در پایگاه داده"""
        db_obj = SPEIValueDB(
            station_id=spei.station_id,
            date=spei.date,
            value=spei.value,
            scale_months=spei.scale_months
        )
        self.db.add(db_obj)
        self.db.commit()
        return True
    
    def get_latest_spei(self, station_id: str) -> Optional[SPEIValue]:
        """دریافت آخرین مقدار SPEI"""
        result = self.db.query(SPEIValueDB).filter(
            SPEIValueDB.station_id == station_id
        ).order_by(SPEIValueDB.date.desc()).first()
        
        if result:
            return SPEIValue(
                station_id=result.station_id,
                date=result.date,
                value=result.value,
                scale_months=result.scale_months
            )
        return None
