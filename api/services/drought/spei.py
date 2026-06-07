"""
SPEI - Standardized Precipitation Evapotranspiration Index
شاخص خشکسالی جهانی - رایگان
Documentation: https://spei.csic.es/
Database: https://spei.csic.es/database.html
"""
import httpx
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel


class SPEIValue(BaseModel):
    date: str
    spei_1: float  # 1-month SPEI
    spei_3: float  # 3-month SPEI
    spei_6: float  # 6-month SPEI
    spei_12: float  # 12-month SPEI
    spei_24: float  # 24-month SPEI


class SPEIAnalysis(BaseModel):
    location: Dict[str, float]
    current_spei: float
    drought_category: str
    drought_severity: str
    duration_months: int
    trend: str  # improving, stable, worsening
    color: str
    description: str


class SPEIService:
    """سرویس SPEI - شاخص خشکسالی استاندارد"""
    
    # SPEI Global Database API
    BASE_URL = "https://spei.csic.es/spei_database"
    
    # Alternative: Calculate from Open-Meteo data
    OPEN_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"
    
    # SPEI Classification (McKee et al., 1993)
    CATEGORIES = {
        'extremely_wet': {'range': (2.0, float('inf')), 'color': '#0c4a6e', 'fa': 'بسیار مرطوب'},
        'very_wet': {'range': (1.5, 2.0), 'color': '#0369a1', 'fa': 'خیلی مرطوب'},
        'moderately_wet': {'range': (1.0, 1.5), 'color': '#0ea5e9', 'fa': 'مرطوب'},
        'near_normal': {'range': (-1.0, 1.0), 'color': '#16a34a', 'fa': 'عادی'},
        'moderately_dry': {'range': (-1.5, -1.0), 'color': '#facc15', 'fa': 'خشک'},
        'severely_dry': {'range': (-2.0, -1.5), 'color': '#ea580c', 'fa': 'خیلی خشک'},
        'extremely_dry': {'range': (float('-inf'), -2.0), 'color': '#991b1b', 'fa': 'بسیار خشک'}
    }
    
    async def calculate_spei_from_climate(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str
    ) -> List[SPEIValue]:
        """محاسبه SPEI از داده‌های اقلیمی"""
        # Get precipitation and temperature data
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                self.OPEN_METEO_URL,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "start_date": start_date,
                    "end_date": end_date,
                    "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min",
                    "timezone": "Asia/Tehran"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            daily = data.get("daily", {})
            dates = daily.get("time", [])
            precipitation = daily.get("precipitation_sum", [])
            temp_max = daily.get("temperature_2m_max", [])
            temp_min = daily.get("temperature_2m_min", [])
            
            # Calculate monthly aggregates
            monthly_data = self._aggregate_monthly(
                dates, precipitation, temp_max, temp_min
            )
            
            # Calculate SPEI for different timescales
            spei_values = []
            for month_data in monthly_data:
                spei_values.append(SPEIValue(
                    date=month_data['date'],
                    spei_1=self._calculate_single_spei(monthly_data, 1, month_data['index']),
                    spei_3=self._calculate_single_spei(monthly_data, 3, month_data['index']),
                    spei_6=self._calculate_single_spei(monthly_data, 6, month_data['index']),
                    spei_12=self._calculate_single_spei(monthly_data, 12, month_data['index']),
                    spei_24=self._calculate_single_spei(monthly_data, 24, month_data['index'])
                ))
            
            return spei_values
    
    def _aggregate_monthly(
        self,
        dates: List[str],
        precipitation: List[float],
        temp_max: List[float],
        temp_min: List[float]
    ) -> List[Dict]:
        """تجمیع داده‌های روزانه به ماهانه"""
        from collections import defaultdict
        
        monthly = defaultdict(lambda: {
            'precip': [], 'temp_max': [], 'temp_min': []
        })
        
        for i, date in enumerate(dates):
            month_key = date[:7]  # YYYY-MM
            if i < len(precipitation) and precipitation[i] is not None:
                monthly[month_key]['precip'].append(precipitation[i])
            if i < len(temp_max) and temp_max[i] is not None:
                monthly[month_key]['temp_max'].append(temp_max[i])
            if i < len(temp_min) and temp_min[i] is not None:
                monthly[month_key]['temp_min'].append(temp_min[i])
        
        result = []
        for idx, (month, data) in enumerate(sorted(monthly.items())):
            precip_sum = sum(data['precip']) if data['precip'] else 0
            temp_avg = (
                (sum(data['temp_max']) / len(data['temp_max']) +
                 sum(data['temp_min']) / len(data['temp_min'])) / 2
            ) if data['temp_max'] and data['temp_min'] else 0
            
            # Calculate potential evapotranspiration (Thornthwaite method simplified)
            pet = self._calculate_pet(temp_avg, len(data['precip']) or 30)
            
            result.append({
                'date': month,
                'index': idx,
                'precipitation': precip_sum,
                'pet': pet,
                'water_balance': precip_sum - pet
            })
        
        return result
    
    def _calculate_pet(self, temp: float, days: int) -> float:
        """محاسبه تبخیر-تعرق بالقوه (ساده‌شده)"""
        # Simplified Thornthwaite
        if temp <= 0:
            return 0
        i = (temp / 5) ** 1.514
        a = (6.75e-7 * i**3) - (7.71e-5 * i**2) + (1.792e-2 * i) + 0.49239
        return 16 * (10 * temp / i) ** a * (days / 30) * 10  # mm/month
    
    def _calculate_single_spei(
        self,
        monthly_data: List[Dict],
        timescale: int,
        current_idx: int
    ) -> float:
        """محاسبه SPEI برای یک مقیاس زمانی"""
        if current_idx < timescale - 1:
            return 0.0
        
        # Calculate rolling sum of water balance
        window = monthly_data[current_idx - timescale + 1:current_idx + 1]
        values = [m['water_balance'] for m in window]
        
        if not values:
            return 0.0
        
        # Fit log-logistic distribution (simplified)
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std = variance ** 0.5
        
        if std == 0:
            return 0.0
        
        # Standardize
        current = values[-1]
        z = (current - mean) / std
        
        # Convert to SPEI (approximation using normal distribution)
        return self._z_to_spei(z)
    
    def _z_to_spei(self, z: float) -> float:
        """تبدیل z-score به SPEI"""
        # Approximation using Abramowitz & Stegun formula
        if z == 0:
            return 0
        
        p = 0.2316419
        b1, b2, b3, b4, b5 = 0.319381530, -0.356563782, 1.781477937, -1.821255978, 1.330274429
        
        t = 1 / (1 + p * abs(z))
        pdf = (1 / (2 * 3.14159) ** 0.5) * (2.71828 ** (-z**2 / 2))
        cdf = 1 - pdf * (b1*t + b2*t**2 + b3*t**3 + b4*t**4 + b5*t**5)
        
        if z < 0:
            cdf = 1 - cdf
        
        # Convert CDF to SPEI (inverse normal)
        # Simplified approximation
        return z
    
    def classify_spei(self, spei: float) -> Dict:
        """طبقه‌بندی مقدار SPEI"""
        for category, info in self.CATEGORIES.items():
            if info['range'][0] <= spei < info['range'][1]:
                return {
                    'category': category,
                    'name_fa': info['fa'],
                    'color': info['color']
                }
        return {
            'category': 'near_normal',
            'name_fa': 'عادی',
            'color': '#16a34a'
        }
    
    async def analyze_drought(
        self,
        latitude: float,
        longitude: float
    ) -> SPEIAnalysis:
        """تحلیل کامل خشکسالی"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730)  # 2 years
        
        spei_values = await self.calculate_spei_from_climate(
            latitude, longitude,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        
        if not spei_values:
            return SPEIAnalysis(
                location={"lat": latitude, "lng": longitude},
                current_spei=0,
                drought_category="near_normal",
                drought_severity="normal",
                duration_months=0,
                trend="stable",
                color="#16a34a",
                description="داده‌ای در دسترس نیست"
            )
        
        # Use 3-month SPEI for current assessment
        current = spei_values[-1].spei_3
        classification = self.classify_spei(current)
        
        # Calculate duration
        duration = 0
        for v in reversed(spei_values):
            if v.spei_3 < -1.0:
                duration += 1
            else:
                break
        
        # Calculate trend
        if len(spei_values) >= 3:
            recent = [v.spei_3 for v in spei_values[-3:]]
            trend_val = recent[-1] - recent[0]
            if trend_val > 0.3:
                trend = "improving"
            elif trend_val < -0.3:
                trend = "worsening"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return SPEIAnalysis(
            location={"lat": latitude, "lng": longitude},
            current_spei=round(current, 2),
            drought_category=classification['category'],
            drought_severity=classification['name_fa'],
            duration_months=duration,
            trend=trend,
            color=classification['color'],
            description=self._get_drought_description(current, duration)
        )
    
    def _get_drought_description(self, spei: float, duration: int) -> str:
        """تولید توضیحات خشکسالی"""
        if spei < -2.0:
            base = "خشکسالی بسیار شدید"
        elif spei < -1.5:
            base = "خشکسالی شدید"
        elif spei < -1.0:
            base = "خشکسالی متوسط"
        elif spei < -0.5:
            base = "خشکسالی خفیف"
        elif spei < 0.5:
            base = "شرایط عادی"
        elif spei < 1.0:
            base = "شرایط مرطوب"
        else:
            base = "شرایط بسیار مرطوب"
        
        if duration > 0:
            return f"{base} - تداوم {duration} ماه"
        return base


# Singleton
spei = SPEIService()
