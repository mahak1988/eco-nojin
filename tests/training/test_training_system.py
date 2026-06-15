"""Integration Tests for Training System - Phase 14"""
import pytest
from datetime import datetime, timezone
from api.domains.lms.services.lms_service import LMSService
from api.services.certificates.certificate_service import CertificateService
from api.services.facilitators.facilitator_network import FacilitatorNetwork


class TestLMSService:
    """Tests for LMS Service"""
    
    def test_get_courses_by_pilot(self):
        """Test getting courses for a specific pilot"""
        lms = LMSService()
        
        # Test Iran pilot
        dishmok_courses = lms.get_courses_by_pilot("dishmok")
        assert len(dishmok_courses) > 0
        
        # Test international pilot
        ouarzazate_courses = lms.get_courses_by_pilot("ouarzazate")
        assert len(ouarzazate_courses) > 0
    
    def test_enroll_user(self):
        """Test user enrollment"""
        lms = LMSService()
        
        enrollment = lms.enroll_user("user_001", "water_mgmt_001")
        assert enrollment.user_id == "user_001"
        assert enrollment.course_id == "water_mgmt_001"
        assert enrollment.progress_percent == 0.0
    
    def test_update_progress(self):
        """Test progress update"""
        lms = LMSService()
        
        enrollment = lms.enroll_user("user_002", "water_mgmt_001")
        success = lms.update_progress(enrollment.enrollment_id, "module_001")
        assert success == True


class TestCertificateService:
    """Tests for Certificate Service"""
    
    def test_issue_certificate(self):
        """Test certificate issuance"""
        cert_service = CertificateService()
        
        certificate = cert_service.issue_certificate(
            user_id="user_001",
            user_name="علی محمدی",
            course_id="water_mgmt_001",
            course_title="مدیریت پایدار منابع آب",
            completion_date=datetime.now(timezone.utc),
            pilot_site="dishmok"
        )
        
        assert "hash" in certificate
        assert "qr_code_url" in certificate
    
    def test_verify_certificate(self):
        """Test certificate verification"""
        cert_service = CertificateService()
        
        certificate = cert_service.issue_certificate(
            user_id="user_002",
            user_name="فاطمه احمدی",
            course_id="soil_cons_001",
            course_title="حفاظت و احیای خاک",
            completion_date=datetime.now(timezone.utc),
            pilot_site="behbahan"
        )
        
        verified = cert_service.verify_certificate(certificate["hash"])
        assert verified is not None
        assert verified["user_id"] == "user_002"


class TestFacilitatorNetwork:
    """Tests for Facilitator Network"""
    
    def test_get_facilitators_by_pilot(self):
        """Test getting facilitators for a pilot"""
        network = FacilitatorNetwork()
        
        # Test Iran pilot
        dishmok_facilitators = network.get_facilitators_by_pilot("dishmok")
        assert len(dishmok_facilitators) > 0
        assert dishmok_facilitators[0].pilot_site == "dishmok"
        
        # Test international pilot
        ouarzazate_facilitators = network.get_facilitators_by_pilot("ouarzazate")
        assert len(ouarzazate_facilitators) > 0
    
    def test_get_facilitators_by_language(self):
        """Test getting facilitators by language"""
        network = FacilitatorNetwork()
        
        # Test Persian facilitators
        fa_facilitators = network.get_facilitators_by_language("fa")
        assert len(fa_facilitators) > 0
        
        # Test Arabic facilitators
        ar_facilitators = network.get_facilitators_by_language("ar")
        assert len(ar_facilitators) > 0
    
    def test_all_pilots_have_facilitators(self):
        """Test that all 12 pilots have facilitators"""
        network = FacilitatorNetwork()
        
        pilots = [
            "dishmok", "behbahan", "rodbar_talesh", "snow_mountain",
            "ouarzazate", "wadi_rum", "sahel_senegal", "ethiopian_highlands",
            "rajasthan", "outback_australia", "atacama_chile", "mongolian_steppe"
        ]
        
        for pilot in pilots:
            facilitators = network.get_facilitators_by_pilot(pilot)
            assert len(facilitators) > 0, f"No facilitators for {pilot}"
