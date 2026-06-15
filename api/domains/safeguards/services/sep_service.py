"""SEP Service - Stakeholder Engagement Plan"""
مطابق با:
- World Bank ESS10 (Stakeholder Engagement and Information Disclosure)
- IFC PS1 (Assessment and Management of E&S Risks)
- GCF Stakeholder Engagement Guidelines
"""
from typing import List, Dict
from datetime import datetime, timezone
import uuid
from .models.safeguards_models import StakeholderEngagement


class SEPService:
    """سرویس مدیریت مشارکت ذی‌نفعان"""

    def __init__(self):
        self.engagements: List[StakeholderEngagement] = []
        self.stakeholder_mapping = self._initialize_stakeholder_mapping()

    def _initialize_stakeholder_mapping(self) -> Dict:
        """نقشه‌برداری ذی‌نفعان کلیدی برای ۱۲ پایلوت"""
        return {
            "iran_dishmok": {
                "affected_communities": ["دامداران عشایر", "روستاییان دیشموک"],
                "vulnerable_groups": ["زنان سرپرست خانوار", "جوانان بیکار"],
                "local_institutions": ["بُنه مرتع‌داری", "شورای روستا", "تعاونی"],
                "government": ["جهاد کشاورزی", "منابع طبیعی", "استانداری"]
            },
            "iran_behbahan": {
                "affected_communities": ["کشاورزان آبی", "کارگران کشاورزی"],
                "vulnerable_groups": ["کارگران مزدی", "زنان روستایی"],
                "local_institutions": ["تعاونی کشاورزی", "سازمان آب"],
                "government": ["جهاد کشاورزی خوزستان"]
            },
            "morocco_ouarzazate": {
                "affected_communities": ["Amazigh communities", "Oasis farmers"],
                "vulnerable_groups": ["Women cooperatives", "Youth"],
                "local_institutions": ["Water user associations", "Cooperatives"],
                "government": ["ORMVAO", "Ministry of Agriculture"]
            },
            "australia_outback": {
                "affected_communities": ["Aboriginal communities", "Pastoralists"],
                "vulnerable_groups": ["Indigenous elders", "Remote youth"],
                "local_institutions": ["Land Councils", "Indigenous Rangers"],
                "government": ["NT Government", "Federal Environment"]
            },
            "mongolia_steppe": {
                "affected_communities": ["Nomadic herders", "Bag communities"],
                "vulnerable_groups": ["Women herders", "Elderly herders"],
                "local_institutions": ["Herder groups", "Bag meetings"],
                "government": ["Soum government", "Ministry of Environment"]
            }
        }

    def record_engagement(
        self,
        pilot_site: str,
        activity_type: str,
        participant_count: int,
        women_count: int,
        youth_count: int,
        topics_discussed: List[str],
        feedback_summary: str,
        indigenous_count: int = 0,
        vulnerable_groups_count: int = 0
    ) -> Dict:
        """ثبت فعالیت مشارکت"""
        engagement = StakeholderEngagement(
            engagement_id=str(uuid.uuid4()),
            pilot_site=pilot_site,
            activity_type=activity_type,
            participant_count=participant_count,
            women_count=women_count,
            youth_count=youth_count,
            indigenous_count=indigenous_count,
            vulnerable_groups_count=vulnerable_groups_count,
            topics_discussed=topics_discussed,
            feedback_summary=feedback_summary
        )
        self.engagements.append(engagement)

        return {
            "engagement_id": engagement.engagement_id,
            "women_participation_percent": (
                (women_count / participant_count * 100) if participant_count else 0
            ),
            "youth_participation_percent": (
                (youth_count / participant_count * 100) if participant_count else 0
            )
        }

    def get_inclusion_metrics(self, pilot_site: str = None) -> Dict:
        """محاسبه شاخص‌های شمول (Inclusion Metrics)"""
        engagements = self.engagements
        if pilot_site:
            engagements = [e for e in engagements if e.pilot_site == pilot_site]

        total_participants = sum(e.participant_count for e in engagements)
        total_women = sum(e.women_count for e in engagements)
        total_youth = sum(e.youth_count for e in engagements)
        total_indigenous = sum(e.indigenous_count for e in engagements)
        total_vulnerable = sum(e.vulnerable_groups_count for e in engagements)

        return {
            "total_engagements": len(engagements),
            "total_participants": total_participants,
            "women_participation_percent": (
                (total_women / total_participants * 100) if total_participants else 0
            ),
            "youth_participation_percent": (
                (total_youth / total_participants * 100) if total_participants else 0
            ),
            "indigenous_participation_percent": (
                (total_indigenous / total_participants * 100) if total_participants else 0
            ),
            "vulnerable_groups_percent": (
                (total_vulnerable / total_participants * 100) if total_participants else 0
            ),
            "gcf_gender_target_met": (
                (total_women / total_participants * 100) >= 40 if total_participants else False
            )
        }