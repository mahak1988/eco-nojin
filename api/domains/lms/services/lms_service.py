"""LMS Service"""
from typing import List, Dict, Optional
from datetime import datetime, timezone
from .models.lms_models import Course, Module, Enrollment, Certificate, Facilitator, Language, CourseCategory
import uuid


class LMSService:
    """Learning Management System Service"""
    
    def __init__(self):
        self.courses: Dict[str, Course] = {}
        self.modules: Dict[str, Module] = {}
        self.enrollments: Dict[str, Enrollment] = {}
        self.certificates: Dict[str, Certificate] = {}
        self.facilitators: Dict[str, Facilitator] = {}
        self._initialize_courses()
    
    def _initialize_courses(self):
        """Initialize courses for 12 global pilots"""
        
        # Course 1: Water Management (for all pilots)
        course1 = Course(
            course_id="water_mgmt_001",
            title={
                "fa": "مدیریت پایدار منابع آب",
                "en": "Sustainable Water Management",
                "ar": "الإدارة المستدامة للمياه",
                "fr": "Gestion durable de l'eau"
            },
            description={
                "fa": "آموزش اصول مدیریت یکپارچه منابع آب، SWC-AgMAR و تکنیک‌های حفظ آب",
                "en": "Training on IWRM principles, SWC-AgMAR and water conservation techniques"
            },
            category=CourseCategory.WATER_MANAGEMENT,
            difficulty="beginner",
            pilot_sites=[
                "dishmok", "behbahan", "rodbar_talesh", "snow_mountain",
                "ouarzazate", "wadi_rum", "sahel_senegal", "ethiopian_highlands",
                "rajasthan", "outback_australia", "atacama_chile", "mongolian_steppe"
            ],
            languages=[Language.FA, Language.EN, Language.AR, Language.FR],
            duration_hours=20.0
        )
        self.courses[course1.course_id] = course1
        
        # Course 2: Soil Conservation
        course2 = Course(
            course_id="soil_cons_001",
            title={
                "fa": "حفاظت و احیای خاک",
                "en": "Soil Conservation and Restoration"
            },
            description={
                "fa": "تکنیک‌های کنترل فرسایش، افزایش ماده آلی خاک و کشاورزی حفاظتی",
                "en": "Erosion control techniques, soil organic matter enhancement and conservation agriculture"
            },
            category=CourseCategory.SOIL_CONSERVATION,
            difficulty="beginner",
            pilot_sites=[
                "dishmok", "behbahan", "rodbar_talesh", "snow_mountain",
                "ouarzazate", "sahel_senegal", "ethiopian_highlands", "rajasthan"
            ],
            languages=[Language.FA, Language.EN, Language.AR, Language.FR, Language.SW],
            duration_hours=16.0
        )
        self.courses[course2.course_id] = course2
        
        # Course 3: Climate Smart Agriculture
        course3 = Course(
            course_id="csa_001",
            title={
                "fa": "کشاورزی هوشمند اقلیم",
                "en": "Climate Smart Agriculture"
            },
            description={
                "fa": "اصول CSA، تنوع کشت، گونه‌های مقاوم به خشکی و مدیریت ریسک اقلیمی",
                "en": "CSA principles, crop diversification, drought-resistant varieties and climate risk management"
            },
            category=CourseCategory.CLIMATE_SMART_AGRICULTURE,
            difficulty="intermediate",
            pilot_sites=[
                "dishmok", "behbahan", "snow_mountain",
                "ouarzazate", "wadi_rum", "sahel_senegal",
                "rajasthan", "outback_australia", "mongolian_steppe"
            ],
            languages=[Language.FA, Language.EN, Language.AR, Language.FR, Language.HI, Language.MN],
            duration_hours=24.0
        )
        self.courses[course3.course_id] = course3
        
        # Course 4: Agroforestry
        course4 = Course(
            course_id="agroforestry_001",
            title={
                "fa": "آگروفارستری و سیستم‌های تلفیقی",
                "en": "Agroforestry and Integrated Systems"
            },
            description={
                "fa": "طراحی سیستم‌های آگروفارستری، سیلواپاستورال و تنوع‌بخشی معیشت",
                "en": "Agroforestry design, silvopastoral systems and livelihood diversification"
            },
            category=CourseCategory.AGROFORESTRY,
            difficulty="intermediate",
            pilot_sites=[
                "dishmok", "rodbar_talesh", "snow_mountain",
                "sahel_senegal", "ethiopian_highlands"
            ],
            languages=[Language.FA, Language.EN, Language.FR, Language.SW],
            duration_hours=18.0
        )
        self.courses[course4.course_id] = course4
        
        # Course 5: Carbon Market
        course5 = Course(
            course_id="carbon_market_001",
            title={
                "fa": "بازار کربن و اعتبارات کربن",
                "en": "Carbon Market and Carbon Credits"
            },
            description={
                "fa": "آشنایی با بازارهای کربن، پروتکل‌های MRV و نحوه کسب درآمد از اعتبارات کربن",
                "en": "Introduction to carbon markets, MRV protocols and earning from carbon credits"
            },
            category=CourseCategory.CARBON_MARKET,
            difficulty="advanced",
            pilot_sites=[
                "dishmok", "behbahan", "rodbar_talesh", "snow_mountain",
                "ouarzazate", "sahel_senegal", "ethiopian_highlands",
                "rajasthan", "outback_australia", "atacama_chile", "mongolian_steppe"
            ],
            languages=[Language.FA, Language.EN, Language.AR, Language.FR, Language.ES],
            duration_hours=12.0
        )
        self.courses[course5.course_id] = course5
    
    def get_courses_by_pilot(self, pilot_site: str) -> List[Course]:
        """Get courses available for a specific pilot"""
        return [c for c in self.courses.values() if pilot_site in c.pilot_sites]
    
    def get_courses_by_language(self, language: Language) -> List[Course]:
        """Get courses available in a specific language"""
        return [c for c in self.courses.values() if language in c.languages]
    
    def enroll_user(self, user_id: str, course_id: str) -> Enrollment:
        """Enroll a user in a course"""
        enrollment_id = str(uuid.uuid4())
        enrollment = Enrollment(
            enrollment_id=enrollment_id,
            user_id=user_id,
            course_id=course_id
        )
        self.enrollments[enrollment_id] = enrollment
        return enrollment
    
    def update_progress(self, enrollment_id: str, module_id: str) -> bool:
        """Update course progress"""
        if enrollment_id not in self.enrollments:
            return False
        
        enrollment = self.enrollments[enrollment_id]
        if module_id not in enrollment.completed_modules:
            enrollment.completed_modules.append(module_id)
            
            # Calculate progress
            course = self.courses.get(enrollment.course_id)
            if course and len(course.modules) > 0:
                enrollment.progress_percent = (len(enrollment.completed_modules) / len(course.modules)) * 100
                
                if enrollment.progress_percent >= 100:
                    enrollment.completed = True
                    enrollment.completed_at = datetime.now(timezone.utc)
        
        return True
    
    def issue_certificate(self, user_id: str, course_id: str) -> Certificate:
        """Issue a certificate upon course completion"""
        certificate_id = str(uuid.uuid4())
        certificate = Certificate(
            certificate_id=certificate_id,
            user_id=user_id,
            course_id=course_id
        )
        self.certificates[certificate_id] = certificate
        return certificate
    
    def register_facilitator(
        self,
        name: str,
        pilot_site: str,
        languages: List[Language],
        expertise: List[str]
    ) -> Facilitator:
        """Register a new facilitator"""
        facilitator_id = str(uuid.uuid4())
        facilitator = Facilitator(
            facilitator_id=facilitator_id,
            name=name,
            pilot_site=pilot_site,
            languages=languages,
            expertise=expertise
        )
        self.facilitators[facilitator_id] = facilitator
        return facilitator
    
    def get_facilitators_by_pilot(self, pilot_site: str) -> List[Facilitator]:
        """Get facilitators for a specific pilot"""
        return [f for f in self.facilitators.values() if f.pilot_site == pilot_site and f.active]
