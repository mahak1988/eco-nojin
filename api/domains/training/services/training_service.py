"""Training Service"""
from typing import List, Dict
from datetime import datetime
from .models.training_models import (
    TrainingModule, TrainingSession, TrainingCertificate,
    TrainingType, TargetAudience
)
import uuid


class TrainingService:
    def __init__(self):
        self.modules = []
        self.sessions = []
        self.certificates = []
        self._initialize_ffs_modules()
    
    def _initialize_ffs_modules(self):
        module1 = TrainingModule(
            module_id="ffs_001",
            title="کشاورزی حفاظتی و مدیریت خاک",
            description="آموزش اصول کشاورزی حفاظتی",
            training_type=TrainingType.FFS,
            target_audience=[TargetAudience.FARMERS, TargetAudience.WOMEN],
            duration_hours=16.0,
            pilot_sites=["dishmok", "behbahan", "rodbar_talesh", "snow_mountain",
                        "ouarzazate", "wadi_rum", "sahel_senegal", "ethiopian_highlands",
                        "rajasthan", "outback_australia", "atacama_chile", "mongolian_steppe"],
            topics=["اصول کشاورزی حفاظتی", "کاهش شخم", "مدیریت بقایا"]
        )
        self.modules.append(module1)
        
        module2 = TrainingModule(
            module_id="ffs_002",
            title="مدیریت هوشمند آب",
            description="آموزش تکنیک‌های آبیاری کارآمد",
            training_type=TrainingType.FFS,
            target_audience=[TargetAudience.FARMERS],
            duration_hours=12.0,
            pilot_sites=["behbahan", "dishmok", "ouarzazate", "rajasthan"],
            topics=["آبیاری قطره‌ای", "زمان‌بندی آبیاری", "بهره‌وری آب"]
        )
        self.modules.append(module2)
        
        module3 = TrainingModule(
            module_id="ffs_003",
            title="آگروفارستری و سیستم‌های تلفیقی",
            description="آموزش طراحی آگروفارستری",
            training_type=TrainingType.FFS,
            target_audience=[TargetAudience.FARMERS, TargetAudience.HERDERS],
            duration_hours=20.0,
            pilot_sites=["dishmok", "snow_mountain", "rodbar_talesh",
                        "sahel_senegal", "ethiopian_highlands"],
            topics=["اصول آگروفارستری", "انتخاب گونه", "سیلواپاستورال"]
        )
        self.modules.append(module3)
    
    def get_modules_by_pilot(self, pilot_site: str) -> List[TrainingModule]:
        return [m for m in self.modules if pilot_site in m.pilot_sites]
    
    def schedule_session(self, module_id: str, pilot_site: str,
                        date: datetime, location: str, instructor: str) -> TrainingSession:
        session = TrainingSession(
            session_id=str(uuid.uuid4()),
            module_id=module_id,
            pilot_site=pilot_site,
            date=date,
            location=location,
            instructor=instructor,
            participants_count=0
        )
        self.sessions.append(session)
        return session
    
    def issue_certificate(self, participant_id: str, participant_name: str,
                         module_id: str, score: float, pilot_site: str) -> TrainingCertificate:
        module = next((m for m in self.modules if m.module_id == module_id), None)
        certificate = TrainingCertificate(
            certificate_id=str(uuid.uuid4()),
            participant_id=participant_id,
            participant_name=participant_name,
            module_id=module_id,
            module_title=module.title if module else "Unknown",
            completion_date=datetime.utcnow(),
            score=score,
            pilot_site=pilot_site
        )
        self.certificates.append(certificate)
        return certificate
