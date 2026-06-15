"""GRM Service - GCF/World Bank Aligned Grievance Redress Mechanism"""

مکانیزم رسیدگی به شکایات مطابق:
- GCF Independent Redress Mechanism (IRM)
- World Bank ESS10 (Stakeholder Engagement)
- IFC Performance Standard 1
- UNDP SES Grievance Mechanism
"""
from typing import List, Dict, Optional
from datetime import datetime, timezone, timedelta
import uuid
from .models.safeguards_models import (
    Grievance, GrievanceCategory, GrievanceSeverity, GrievanceStatus
)


class GRMService:
    """سرویس مدیریت رسیدگی به شکایات"""

    def __init__(self):
        self.grievances: Dict[str, Grievance] = {}
        self.sla_days = {
            GrievanceSeverity.LOW: 30,
            GrievanceSeverity.MEDIUM: 20,
            GrievanceSeverity.HIGH: 10,
            GrievanceSeverity.CRITICAL: 5
        }

    def submit_grievance(
        self,
        pilot_site: str,
        country: str,
        category: str,
        severity: str,
        description: str,
        complainant_type: str = "individual",
        complainant_gender: str = "not_disclosed",
        is_anonymous: bool = False
    ) -> Dict:
        """ثبت شکایت جدید"""
        grievance_id = f"GRM-{uuid.uuid4().hex[:8].upper()}"

        grievance = Grievance(
            grievance_id=grievance_id,
            pilot_site=pilot_site,
            country=country,
            category=GrievanceCategory(category),
            severity=GrievanceSeverity(severity),
            description=description,
            complainant_type=complainant_type,
            complainant_gender=complainant_gender,
            is_anonymous=is_anonymous,
            sla_days=self.sla_days[GrievanceSeverity(severity)]
        )

        self.grievances[grievance_id] = grievance

        return {
            "grievance_id": grievance_id,
            "status": "received",
            "sla_days": grievance.sla_days,
            "deadline": (grievance.submitted_at + timedelta(days=grievance.sla_days)).isoformat(),
            "message": "شکایت شما ثبت شد. ظرف ۵ روز کاری تأییدیه دریافت خواهید کرد."
        }

    def acknowledge_grievance(self, grievance_id: str) -> Dict:
        """تأیید دریافت شکایت"""
        if grievance_id not in self.grievances:
            return {"error": "Grievance not found"}

        grievance = self.grievances[grievance_id]
        grievance.status = GrievanceStatus.ACKNOWLEDGED
        grievance.acknowledged_at = datetime.now(timezone.utc)

        return {
            "grievance_id": grievance_id,
            "status": "acknowledged",
            "acknowledged_at": grievance.acknowledged_at.isoformat()
        }

    def resolve_grievance(self, grievance_id: str, resolution_notes: str) -> Dict:
        """حل و فصل شکایت"""
        if grievance_id not in self.grievances:
            return {"error": "Grievance not found"}

        grievance = self.grievances[grievance_id]
        grievance.status = GrievanceStatus.RESOLVED
        grievance.resolved_at = datetime.now(timezone.utc)
        grievance.resolution_notes = resolution_notes

        # محاسبه مدت رسیدگی
        days_to_resolve = (grievance.resolved_at - grievance.submitted_at).days
        sla_met = days_to_resolve <= grievance.sla_days

        return {
            "grievance_id": grievance_id,
            "status": "resolved",
            "days_to_resolve": days_to_resolve,
            "sla_met": sla_met,
            "resolution_notes": resolution_notes
        }

    def get_grievance_statistics(self, pilot_site: str = None) -> Dict:
        """آمار شکایات"""
        grievances = list(self.grievances.values())
        if pilot_site:
            grievances = [g for g in grievances if g.pilot_site == pilot_site]

        by_category = {}
        by_status = {}
        by_severity = {}
        by_gender = {}

        for g in grievances:
            cat = g.category.value
            by_category[cat] = by_category.get(cat, 0) + 1

            status = g.status.value
            by_status[status] = by_status.get(status, 0) + 1

            sev = g.severity.value
            by_severity[sev] = by_severity.get(sev, 0) + 1

            gender = g.complainant_gender
            by_gender[gender] = by_gender.get(gender, 0) + 1

        resolved = [g for g in grievances if g.status == GrievanceStatus.RESOLVED]
        sla_compliance = 0.0
        if resolved:
            met_sla = sum(
                1 for g in resolved
                if (g.resolved_at - g.submitted_at).days <= g.sla_days
            )
            sla_compliance = (met_sla / len(resolved)) * 100

        return {
            "total_grievances": len(grievances),
            "by_category": by_category,
            "by_status": by_status,
            "by_severity": by_severity,
            "by_gender": by_gender,
            "resolved_count": len(resolved),
            "sla_compliance_percent": round(sla_compliance, 2),
            "pilot_site": pilot_site or "all"
        }

    def generate_gcf_grievance_report(self, year: int) -> Dict:
        """تولید گزارش GRM برای GCF"""
        stats = self.get_grievance_statistics()

        return {
            "report_type": "GCF Grievance Redress Mechanism Annual Report",
            "standard": "GCF ESP + IRM",
            "reporting_year": year,
            "grievances_received": stats["total_grievances"],
            "grievances_resolved": stats["resolved_count"],
            "resolution_rate_percent": (
                (stats["resolved_count"] / stats["total_grievances"] * 100)
                if stats["total_grievances"] > 0 else 0
            ),
            "sla_compliance_percent": stats["sla_compliance_percent"],
            "breakdown_by_category": stats["by_category"],
            "gender_disaggregated": stats["by_gender"],
            "accessibility_features": [
                "Multiple languages (8 languages)",
                "Anonymous submission option",
                "Mobile/USSD access for offline areas",
                "Community-level focal points in all 12 pilots",
                "Gender-sensitive intake procedures"
            ],
            "escalation_pathway": [
                "Level 1: Local GRM Focal Point (5 days)",
                "Level 2: National GRM Committee (15 days)",
                "Level 3: GCF Independent Redress Mechanism"
            ],
            "generated_at": datetime.now(timezone.utc).isoformat()
        }