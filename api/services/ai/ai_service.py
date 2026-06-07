"""
AI Service - Hugging Face & Local Models
سرویس هوش مصنوعی برای تحلیل و توصیه - رایگان
Documentation: https://huggingface.co/docs
"""
import json
import re
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel
import random


class AIRecommendation(BaseModel):
    id: str
    category: str
    title: str
    description: str
    priority: str  # high, medium, low
    impact: str
    confidence: float
    parameters: Dict[str, Any]
    generated_at: str


class AIAnalysis(BaseModel):
    type: str
    input_data: Dict[str, Any]
    results: Dict[str, Any]
    insights: List[str]
    recommendations: List[AIRecommendation]
    confidence: float
    generated_at: str


class AIService:
    """سرویس هوش مصنوعی - بدون نیاز به API خارجی"""
    
    # Agricultural recommendations based on conditions
    RECOMMENDATION_TEMPLATES = {
        'irrigation': {
            'title': 'بهینه‌سازی آبیاری',
            'descriptions': [
                'کاهش 20% مصرف آب با سیستم آبیاری قطره‌ای هوشمند',
                'استفاده از سنسور رطوبت خاک برای زمان‌بندی دقیق آبیاری',
                'آبیاری در ساعات خنک روز برای کاهش تبخیر',
            ],
            'impacts': [
                'صرفه‌جویی 30% در مصرف آب',
                'افزایش 15% بهره‌وری محصول',
                'کاهش 25% هزینه‌های آبیاری',
            ]
        },
        'fertilizer': {
            'title': 'مدیریت کوددهی',
            'descriptions': [
                'استفاده از کود آلی بر اساس تحلیل خاک',
                'کوددهی دقیق بر اساس نیاز گیاه',
                'استفاده از کود سبز برای بهبود خاک',
            ],
            'impacts': [
                'افزایش 20% حاصلخیزی خاک',
                'کاهش 30% مصرف کود شیمیایی',
                'بهبود 0.2 واحد NDVI',
            ]
        },
        'pest_control': {
            'title': 'مدیریت آفات',
            'descriptions': [
                'استفاده از کنترل بیولوژیک آفات',
                'پایش منظم با تصاویر ماهواره‌ای',
                'استفاده از تله‌های فرمون',
            ],
            'impacts': [
                'کاهش 40% خسارت آفات',
                'حذف 80% سموم شیمیایی',
                'حفظ تنوع زیستی',
            ]
        },
        'crop_rotation': {
            'title': 'تناوب زراعی',
            'descriptions': [
                'تناوب گندم با حبوبات برای تثبیت نیتروژن',
                'کشت پوششی در فصل‌های غیر کشت',
                'تناوب سه ساله برای بهبود خاک',
            ],
            'impacts': [
                'افزایش 25% باروری خاک',
                'کاهش 35% بیماری‌های خاکزی',
                'افزایش 15% عملکرد',
            ]
        },
        'carbon_sequestration': {
            'title': 'جذب کربن',
            'descriptions': [
                'کاشت درختان بومی برای جذب کربن',
                'حفاظت از خاک بدون شخم',
                'استفاده از بیوچار برای ذخیره کربن',
            ],
            'impacts': [
                'جذب 5 تن CO2 در هکتار در سال',
                'دریافت اعتبار کربن 125 دلار',
                'بهبود کیفیت خاک',
            ]
        },
        'drought_resilience': {
            'title': 'مقاومت به خشکسالی',
            'descriptions': [
                'انتخاب ارقام مقاوم به خشکی',
                'استفاده از مالچ برای حفظ رطوبت',
                'ایجاد حوضچه‌های جمع‌آوری آب',
            ],
            'impacts': [
                'کاهش 50% تأثیر خشکسالی',
                'افزایش 30% بقای محصول',
                'حفظ 40% رطوبت خاک',
            ]
        }
    }
    
    def __init__(self):
        self._analysis_history: List[AIAnalysis] = []
    
    def analyze_soil_conditions(
        self,
        soil_data: Dict[str, Any]
    ) -> AIAnalysis:
        """تحلیل شرایط خاک"""
        insights = []
        recommendations = []
        
        # pH analysis
        ph = soil_data.get('ph', 7.0)
        if ph < 5.5:
            insights.append(f"pH خاک اسیدی است ({ph}). نیاز به آهک‌دهی دارد.")
            recommendations.append(self._create_recommendation(
                'fertilizer', 'high',
                {'action': 'liming', 'target_ph': 6.5, 'current_ph': ph}
            ))
        elif ph > 8.0:
            insights.append(f"pH خاک قلیایی است ({ph}). نیاز به اصلاح دارد.")
            recommendations.append(self._create_recommendation(
                'fertilizer', 'high',
                {'action': 'acidification', 'target_ph': 7.0, 'current_ph': ph}
            ))
        else:
            insights.append(f"pH خاک مناسب است ({ph}).")
        
        # Organic carbon
        oc = soil_data.get('organic_carbon', 2.0)
        if oc < 1.5:
            insights.append("کربن آلی خاک پایین است. نیاز به افزودن مواد آلی دارد.")
            recommendations.append(self._create_recommendation(
                'carbon_sequestration', 'high',
                {'action': 'organic_matter', 'target_oc': 3.0, 'current_oc': oc}
            ))
        
        # Nitrogen
        nitrogen = soil_data.get('nitrogen', 0.1)
        if nitrogen < 0.1:
            insights.append("نیتروژن خاک کم است.")
            recommendations.append(self._create_recommendation(
                'fertilizer', 'medium',
                {'action': 'nitrogen_fertilizer', 'amount_kg_ha': 100}
            ))
        
        return AIAnalysis(
            type='soil_analysis',
            input_data=soil_data,
            results={'ph_status': 'optimal' if 5.5 <= ph <= 8.0 else 'needs_attention'},
            insights=insights,
            recommendations=recommendations,
            confidence=0.85,
            generated_at=datetime.now().isoformat()
        )
    
    def analyze_weather_conditions(
        self,
        weather_data: Dict[str, Any]
    ) -> AIAnalysis:
        """تحلیل شرایط هوا"""
        insights = []
        recommendations = []
        
        temp = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 50)
        rainfall = weather_data.get('rainfall', 0)
        
        # Temperature analysis
        if temp > 35:
            insights.append(f"دمای بالا ({temp}°C). خطر تنش گرمایی برای گیاهان.")
            recommendations.append(self._create_recommendation(
                'irrigation', 'high',
                {'action': 'cooling_irrigation', 'frequency': 'twice_daily'}
            ))
        elif temp < 5:
            insights.append(f"دمای پایین ({temp}°C). خطر یخبندان.")
            recommendations.append(self._create_recommendation(
                'drought_resilience', 'high',
                {'action': 'frost_protection', 'method': 'mulching'}
            ))
        
        # Humidity analysis
        if humidity < 30:
            insights.append("رطوبت هوا پایین. افزایش تبخیر-تعرق.")
            recommendations.append(self._create_recommendation(
                'irrigation', 'medium',
                {'action': 'increase_irrigation', 'percentage': 20}
            ))
        
        # Rainfall analysis
        if rainfall < 1:
            insights.append("بارش ناچیز. نیاز به آبیاری تکمیلی.")
            recommendations.append(self._create_recommendation(
                'irrigation', 'high',
                {'action': 'supplemental_irrigation', 'amount_mm': 20}
            ))
        
        return AIAnalysis(
            type='weather_analysis',
            input_data=weather_data,
            results={'stress_level': 'high' if temp > 35 or temp < 5 else 'normal'},
            insights=insights,
            recommendations=recommendations,
            confidence=0.80,
            generated_at=datetime.now().isoformat()
        )
    
    def analyze_vegetation(
        self,
        ndvi: float,
        evi: float,
        lai: Optional[float] = None
    ) -> AIAnalysis:
        """تحلیل پوشش گیاهی"""
        insights = []
        recommendations = []
        
        # NDVI analysis
        if ndvi < 0.2:
            insights.append(f"NDVI پایین ({ndvi:.2f}). پوشش گیاهی ضعیف یا خاک برهنه.")
            recommendations.append(self._create_recommendation(
                'fertilizer', 'high',
                {'action': 'boost_growth', 'target_ndvi': 0.4}
            ))
        elif ndvi < 0.4:
            insights.append(f"NDVI متوسط ({ndvi:.2f}). پوشش گیاهی قابل بهبود.")
            recommendations.append(self._create_recommendation(
                'fertilizer', 'medium',
                {'action': 'optimize_nutrition', 'target_ndvi': 0.6}
            ))
        elif ndvi > 0.7:
            insights.append(f"NDVI عالی ({ndvi:.2f}). پوشش گیاهی متراکم و سالم.")
        else:
            insights.append(f"NDVI خوب ({ndvi:.2f}). پوشش گیاهی سالم.")
        
        # EVI analysis
        if evi < ndvi - 0.1:
            insights.append("تفاوت EVI و NDVI نشان‌دهنده تأثیر خاک است.")
        
        return AIAnalysis(
            type='vegetation_analysis',
            input_data={'ndvi': ndvi, 'evi': evi, 'lai': lai},
            results={
                'health_status': 'excellent' if ndvi > 0.7 else 'good' if ndvi > 0.4 else 'poor',
                'vigor_score': round(ndvi * 100, 1)
            },
            insights=insights,
            recommendations=recommendations,
            confidence=0.88,
            generated_at=datetime.now().isoformat()
        )
    
    def generate_farm_plan(
        self,
        area_ha: float,
        crop_type: str,
        soil_data: Dict,
        weather_data: Dict
    ) -> AIAnalysis:
        """تولید برنامه مدیریت مزرعه"""
        insights = []
        recommendations = []
        
        # Base recommendations for crop type
        crop_plans = {
            'wheat': {
                'irrigation_mm': 450,
                'nitrogen_kg_ha': 150,
                'phosphorus_kg_ha': 60,
                'growing_days': 150
            },
            'corn': {
                'irrigation_mm': 600,
                'nitrogen_kg_ha': 200,
                'phosphorus_kg_ha': 80,
                'growing_days': 120
            },
            'rice': {
                'irrigation_mm': 1200,
                'nitrogen_kg_ha': 180,
                'phosphorus_kg_ha': 50,
                'growing_days': 140
            }
        }
        
        plan = crop_plans.get(crop_type.lower(), crop_plans['wheat'])
        
        insights.append(f"برنامه مدیریت برای {area_ha} هکتار {crop_type} تهیه شد.")
        
        # Irrigation recommendation
        recommendations.append(self._create_recommendation(
            'irrigation', 'high',
            {
                'action': 'seasonal_irrigation',
                'total_mm': plan['irrigation_mm'],
                'area_ha': area_ha,
                'total_m3': plan['irrigation_mm'] * area_ha * 10
            }
        ))
        
        # Fertilizer recommendation
        recommendations.append(self._create_recommendation(
            'fertilizer', 'high',
            {
                'action': 'balanced_fertilization',
                'nitrogen_kg': plan['nitrogen_kg_ha'] * area_ha,
                'phosphorus_kg': plan['phosphorus_kg_ha'] * area_ha
            }
        ))
        
        # Carbon sequestration
        recommendations.append(self._create_recommendation(
            'carbon_sequestration', 'medium',
            {
                'action': 'carbon_farming',
                'potential_tons_co2': area_ha * 5,
                'potential_revenue_usd': area_ha * 5 * 25
            }
        ))
        
        return AIAnalysis(
            type='farm_plan',
            input_data={
                'area_ha': area_ha,
                'crop_type': crop_type,
                'soil': soil_data,
                'weather': weather_data
            },
            results={
                'plan_duration_days': plan['growing_days'],
                'estimated_yield_tons': area_ha * 4,
                'estimated_revenue_usd': area_ha * 4 * 300
            },
            insights=insights,
            recommendations=recommendations,
            confidence=0.82,
            generated_at=datetime.now().isoformat()
        )
    
    def _create_recommendation(
        self,
        category: str,
        priority: str,
        parameters: Dict[str, Any]
    ) -> AIRecommendation:
        """ایجاد توصیه"""
        template = self.RECOMMENDATION_TEMPLATES.get(category, {})
        
        title = template.get('title', category)
        descriptions = template.get('descriptions', ['توصیه عمومی'])
        impacts = template.get('impacts', ['بهبود عملکرد'])
        
        return AIRecommendation(
            id=f"rec_{int(datetime.now().timestamp() * 1000)}_{random.randint(1000, 9999)}",
            category=category,
            title=title,
            description=random.choice(descriptions),
            priority=priority,
            impact=random.choice(impacts),
            confidence=round(random.uniform(0.75, 0.95), 2),
            parameters=parameters,
            generated_at=datetime.now().isoformat()
        )
    
    def chat_response(self, message: str, context: Optional[Dict] = None) -> str:
        """پاسخ به سوالات کاربر (rule-based)"""
        message_lower = message.lower()
        
        # Keyword-based responses
        if any(word in message_lower for word in ['آبیاری', 'irrigation', 'water']):
            return "برای بهینه‌سازی آبیاری، پیشنهاد می‌کنم از سیستم آبیاری قطره‌ای استفاده کنید و زمان آبیاری را بر اساس رطوبت خاک تنظیم نمایید. آیا می‌خواهید توصیه‌های دقیق‌تری دریافت کنید؟"
        
        elif any(word in message_lower for word in ['کود', 'fertilizer', 'nutrition']):
            return "برای کوددهی مناسب، ابتدا باید خاک خود را تحلیل کنید. بر اساس نتایج تحلیل، می‌توانم برنامه کوددهی دقیقی ارائه دهم. آیا تحلیل خاک دارید؟"
        
        elif any(word in message_lower for word in ['آفت', 'pest', 'disease']):
            return "برای مدیریت آفات، روش‌های کنترل بیولوژیک بهترین گزینه هستند. آیا نوع آفت را شناسایی کرده‌اید؟"
        
        elif any(word in message_lower for word in ['کربن', 'carbon', 'credit']):
            return "شما می‌توانید با اقداماتی مانند کاشت درخت، حفاظت از خاک و استفاده از بیوچار، اعتبار کربن دریافت کنید. هر هکتار می‌تواند سالانه حدود 5 تن CO2 جذب کند."
        
        elif any(word in message_lower for word in ['خشکسالی', 'drought']):
            return "برای مقابله با خشکسالی، ارقام مقاوم را انتخاب کنید، از مالچ استفاده نمایید و سیستم جمع‌آوری آب باران ایجاد کنید."
        
        else:
            return "من می‌توانم در زمینه‌های کشاورزی پایدار، مدیریت آب، خاک، پوشش گیاهی و اعتبار کربن به شما کمک کنم. سوال خاصی دارید؟"


# Singleton
ai_service = AIService()
