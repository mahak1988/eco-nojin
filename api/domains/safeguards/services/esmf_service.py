"""ESMF/ESMP Service - Environmental & Social Management Framework"""
مطابق با:
- GCF Environmental and Social Policy (ESP)
- GCF Performance Standards (PS1-PS8)
- World Bank ESS1-ESS10
- IFC Performance Standards
"""
from typing import List, Dict
from datetime import datetime, timezone
from .models.safeguards_models import SafeguardAssessment, ESMPAction


class ESMFService:
    """سرویس مدیریت حفاظت‌های زیست‌محیطی-اجتماعی"""

    def __init__(self):
        self.assessments: List[SafeguardAssessment] = []
        self.esmp_actions: List[ESMPAction] = []
        self.gcf_performance_standards = {
            "PS1": "Environmental and Social Assessment and Management",
            "PS2": "Labour and Working Conditions",
            "PS3": "Resource Efficiency and Pollution Prevention",
            "PS4": "Community Health, Safety and Security",
            "PS5": "Land Acquisition and Involuntary Resettlement",
            "PS6": "Biodiversity Conservation and Sustainable Management",
            "PS7": "Indigenous Peoples",
            "PS8": "Cultural Heritage"
        }

    def screen_activity(
        self,
        pilot_site: str,
        activity_type: str,
        description: str
    ) -> Dict:
        """غربالگری زیست‌محیطی-اجتماعی فعالیت"""

        # ریسک‌سنجی بر اساس نوع فعالیت
        risk_matrix = {
            "swc_structure": {"env": "low", "social": "low", "gender": "low"},
            "agroforestry": {"env": "low", "social": "low", "gender": "low"},
            "rangeland_exclosure": {"env": "low", "social": "medium", "gender": "medium"},
            "water_harvesting": {"env": "low", "social": "low", "gender": "low"},
            "road_construction": {"env": "high", "social": "high", "gender": "medium"},
            "resettlement": {"env": "medium", "social": "high", "gender": "high"},
            "large_dam": {"env": "high", "social": "high", "gender": "high"}
        }

        risks = risk_matrix.get(activity_type, {"env": "low", "social": "low", "gender": "low"})

        # شناسایی PSهای فعال
        triggered_ps = ["PS1"]
        if risks["env"] in ["medium", "high"]:
            triggered_ps.extend(["PS3", "PS6"])
        if risks["social"] in ["medium", "high"]:
            triggered_ps.append("PS4")
        if "resettlement" in activity_type:
            triggered_ps.append("PS5")
        if pilot_site in ["mongolia_steppe", "australia_outback"]:
            triggered_ps.append("PS7")

        # تولید اقدامات کاهش
        mitigation = []
        if risks["env"] != "low":
            mitigation.append("Environmental Impact Assessment required")
            mitigation.append("Biodiversity offset plan if applicable")
        if risks["social"] != "low":
            mitigation.append("Stakeholder engagement plan (SEP)")
            mitigation.append("Grievance redress mechanism (GRM)")
        if risks["gender"] != "low":
            mitigation.append("Gender action plan")
            mitigation.append("Women consultation sessions")

        return {
            "pilot_site": pilot_site,
            "activity_type": activity_type,
            "risk_category": "Category " + (
                "A" if "high" in risks.values() else
                "B" if "medium" in risks.values() else "C"
            ),
            "environmental_risk": risks["env"],
            "social_risk": risks["social"],
            "gender_risk": risks["gender"],
            "triggered_performance_standards": triggered_ps,
            "required_instruments": self._get_required_instruments(triggered_ps),
            "mitigation_measures": mitigation,
            "screened_at": datetime.now(timezone.utc).isoformat()
        }

    def _get_required_instruments(self, triggered_ps: List[str]) -> List[str]:
        """تعیین اسناد مورد نیاز"""
        instruments = ["ESMF", "SEP", "GRM"]
        if "PS3" in triggered_ps:
            instruments.append("Environmental Management Plan (EMP)")
        if "PS4" in triggered_ps:
            instruments.append("Community Health & Safety Plan")
        if "PS5" in triggered_ps:
            instruments.append("Resettlement Policy Framework (RPF)")
        if "PS6" in triggered_ps:
            instruments.append("Biodiversity Action Plan")
        if "PS7" in triggered_ps:
            instruments.append("Indigenous Peoples Plan (IPP)")
        if "PS8" in triggered_ps:
            instruments.append("Cultural Heritage Management Plan")
        instruments.append("Gender Action Plan")
        instruments.append("Labour Management Procedures")
        return instruments

    def get_safeguards_summary(self) -> Dict:
        """خلاصه چارچوب حفاظت‌ها"""
        return {
            "framework": "Integrated Environmental and Social Safeguards",
            "alignment": {
                "GCF": "Environmental and Social Policy (ESP) + 8 Performance Standards",
                "World_Bank": "Environmental and Social Framework (ESF) + ESS1-10",
                "IFC": "Performance Standards 1-8",
                "UNDP": "Social and Environmental Standards (SES)",
                "UNCCD": "Gender Action Plan + LDN safeguards"
            },
            "instruments_in_place": [
                "ESMF (Environmental & Social Management Framework)",
                "ESMP (Environmental & Social Management Plan)",
                "SEP (Stakeholder Engagement Plan)",
                "GRM (Grievance Redress Mechanism)",
                "RPF (Resettlement Policy Framework)",
                "IPPF (Indigenous Peoples Planning Framework)",
                "GAP (Gender Action Plan)",
                "LMP (Labour Management Procedures)",
                "PEMP (Pest Management Plan)",
                "CHMP (Cultural Heritage Management Plan)"
            ],
            "gcf_performance_standards": self.gcf_performance_standards,
            "exclusion_list": [
                "No forced displacement without FPIC",
                "No activities violating indigenous rights",
                "No child labour or forced labour",
                "No activities in critical habitats without offset",
                "No significant cultural heritage destruction"
            ]
        }