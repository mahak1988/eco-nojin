"""Facilitator Network Management"""
from typing import List, Dict, Optional
from datetime import datetime, timezone
from dataclasses import dataclass


@dataclass
class FacilitatorProfile:
    facilitator_id: str
    name: str
    pilot_site: str
    country: str
    languages: List[str]
    expertise: List[str]
    contact_email: str
    contact_phone: Optional[str] = None
    certified_courses: List[str] = []
    active: bool = True
    registered_at: datetime = None


class FacilitatorNetwork:
    """Facilitator Network Management"""
    
    def __init__(self):
        self.facilitators: Dict[str, FacilitatorProfile] = {}
        self._initialize_facilitators()
    
    def _initialize_facilitators(self):
        """Initialize facilitators for 12 pilots"""
        
        # Iran pilots
        self._add_facilitator("فاطمه احمدی", "dishmok", "ایران", ["fa", "en"], ["مرتعداری", "SWC"])
        self._add_facilitator("محمد رضایی", "behbahan", "ایران", ["fa", "ar"], ["مدیریت شوری", "IWRM"])
        self._add_facilitator"زهرا محمدی", "rodbar_talesh", "ایران", ["fa", "en"], ["جنگلداری", "حفاظت خاک"])
        self._add_facilitator("علی حسینی", "snow_mountain", "ایران", ["fa", "en"], ["مدیریت برف", "مرتعداری"])
        
        # MENA pilots
        self._add_facilitator("أحمد بن علی", "ouarzazate", "المغرب", ["ar", "fr", "en"], ["إدارة المياه", "الزراعة"])
        self._add_facilitator("محمد البدوي", "wadi_rum", "الأردن", ["ar", "en"], ["السياحة البيئية", "الحفاظ"])
        
        # Africa pilots
        self._add_facilitator("Aminata Diallo", "sahel_senegal", "Sénégal", ["fr", "sw", "en"], ["Agroforesterie", "Élevage"])
        self._add_facilitator("Tadesse Bekele", "ethiopian_highlands", "Ethiopia", ["en", "sw"], ["Watershed", "Soil Conservation"])
        
        # Asia pilots
        self._add_facilitator("Rajesh Kumar", "rajasthan", "India", ["hi", "en"], ["Johad", "Water Harvesting"])
        self._add_facilitator("Batu Khan", "mongolian_steppe", "Mongolia", ["mn", "en"], ["Pastoral Management", "Rangeland"])
        
        # Oceania pilot
        self._add_facilitator("Sarah Williams", "outback_australia", "Australia", ["en"], ["Fire Management", "Rangeland"])
        
        # South America pilot
        self._add_facilitator("Carlos Mendoza", "atacama_chile", "Chile", ["es", "en"], ["Fog Harvesting", "AgriTech"])
    
    def _add_facilitator(self, name: str, pilot_site: str, country: str, languages: List[str], expertise: List[str]):
        """Add a facilitator"""
        import uuid
        facilitator_id = str(uuid.uuid4())
        facilitator = FacilitatorProfile(
            facilitator_id=facilitator_id,
            name=name,
            pilot_site=pilot_site,
            country=country,
            languages=languages,
            expertise=expertise,
            contact_email=f"{name.lower().replace(' ', '.')}@econojin.com",
            registered_at=datetime.now(timezone.utc)
        )
        self.facilitators[facilitator_id] = facilitator
    
    def get_facilitators_by_pilot(self, pilot_site: str) -> List[FacilitatorProfile]:
        """Get facilitators for a specific pilot"""
        return [f for f in self.facilitators.values() if f.pilot_site == pilot_site and f.active]
    
    def get_facilitators_by_language(self, language: str) -> List[FacilitatorProfile]:
        """Get facilitators by language"""
        return [f for f in self.facilitators.values() if language in f.languages and f.active]
    
    def get_all_facilitators(self) -> List[FacilitatorProfile]:
        """Get all active facilitators"""
        return [f for f in self.facilitators.values() if f.active]
