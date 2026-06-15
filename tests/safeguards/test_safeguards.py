"""Safeguards Integration Tests"""
import pytest
from api.domains.safeguards.services.grm_service import GRMService
from api.domains.safeguards.services.sep_service import SEPService
from api.domains.safeguards.services.esmf_service import ESMFService


class TestGRMService:
    """تست‌های GRM"""

    def test_submit_grievance(self):
        """تست ثبت شکایت"""
        service = GRMService()
        result = service.submit_grievance(
            pilot_site="dishmok",
            country="Iran",
            category="environmental",
            severity="medium",
            description="Test grievance"
        )
        assert "grievance_id" in result
        assert result["status"] == "received"
        assert result["sla_days"] == 20

    def test_acknowledge_grievance(self):
        """تست تأیید شکایت"""
        service = GRMService()
        submission = service.submit_grievance(
            "dishmok", "Iran", "social", "low", "Test"
        )
        ack = service.acknowledge_grievance(submission["grievance_id"])
        assert ack["status"] == "acknowledged"

    def test_sla_calculation(self):
        """تست محاسبه SLA"""
        service = GRMService()
        critical = service.submit_grievance(
            "dishmok", "Iran", "gender", "critical", "Critical issue"
        )
        assert critical["sla_days"] == 5


class TestSEPService:
    """تست‌های SEP"""

    def test_record_engagement(self):
        """تست ثبت مشارکت"""
        service = SEPService()
        result = service.record_engagement(
            pilot_site="dishmok",
            activity_type="workshop",
            participant_count=50,
            women_count=25,
            youth_count=15,
            topics_discussed=["water", "rangeland"],
            feedback_summary="Positive feedback"
        )
        assert result["women_participation_percent"] == 50.0
        assert result["youth_participation_percent"] == 30.0

    def test_gcf_gender_target(self):
        """تست هدف جنسیتی GCF"""
        service = SEPService()
        service.record_engagement(
            "dishmok", "workshop", 100, 45, 30, ["test"], "ok"
        )
        metrics = service.get_inclusion_metrics()
        assert metrics["gcf_gender_target_met"] == True


class TestESMFService:
    """تست‌های ESMF"""

    def test_screen_low_risk_activity(self):
        """تست غربالگری فعالیت کم‌ریسک"""
        service = ESMFService()
        result = service.screen_activity(
            pilot_site="dishmok",
            activity_type="swc_structure",
            description="Building small stone bunds"
        )
        assert result["risk_category"] == "Category C"
        assert result["environmental_risk"] == "low"

    def test_screen_high_risk_activity(self):
        """تست غربالگری فعالیت پرریسک"""
        service = ESMFService()
        result = service.screen_activity(
            pilot_site="australia_outback",
            activity_type="resettlement",
            description="Test"
        )
        assert result["risk_category"] == "Category A"
        assert "PS5" in result["triggered_performance_standards"]
        assert "PS7" in result["triggered_performance_standards"]  # Indigenous

    def test_safeguards_summary(self):
        """تست خلاصه حفاظت‌ها"""
        service = ESMFService()
        summary = service.get_safeguards_summary()
        assert "GCF" in summary["alignment"]
        assert "World_Bank" in summary["alignment"]
        assert "IFC" in summary["alignment"]
        assert len(summary["gcf_performance_standards"]) == 8


class TestSafeguardsCompliance:
    """تست انطباق با استانداردها"""

    def test_gcf_esp_compliance(self):
        """تست انطباق با GCF ESP"""
        esmf = ESMFService()
        summary = esmf.get_safeguards_summary()
        # باید همه PSها پوشش داده شوند
        assert len(summary["gcf_performance_standards"]) == 8
        assert "PS1" in summary["gcf_performance_standards"]
        assert "PS7" in summary["gcf_performance_standards"]

    def test_all_instruments_present(self):
        """تست وجود همه اسناد حفاظتی"""
        esmf = ESMFService()
        summary = esmf.get_safeguards_summary()
        required = ["ESMF", "ESMP", "SEP", "GRM", "GAP", "LMP"]
        for instrument in required:
            assert instrument in summary["instruments_in_place"]