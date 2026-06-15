"""End-to-End Tests - Phase 16"""
import pytest
from datetime import datetime, timezone, timedelta
from api.domains.pilots.services.pilot_activation_service import PilotActivationService
from api.domains.pilots.models.pilot_models import PilotStatus


class TestPilotActivationE2E:
    """تست‌های end-to-end فعال‌سازی پایلوت"""

    def test_full_pilot_activation_cycle(self):
        """تست چرخه کامل فعال‌سازی یک پایلوت"""
        service = PilotActivationService()
        pilot = "dishmok"

        # 1. استقرار حسگرها
        sensor1 = service.deploy_sensor(pilot, "soil_moisture", 30.9, 51.4)
        assert "sensor_id" in sensor1
        assert sensor1["status"] == "deployed"

        sensor2 = service.deploy_sensor(pilot, "water_level", 30.91, 51.41)
        assert sensor2["sensor_id"] != sensor1["sensor_id"]

        # 2. ثبت اعضای جامعه
        for i in range(15):
            member = service.register_community_member(
                pilot, f"Member {i}", "farmer",
                "female" if i % 2 == 0 else "male", "adult"
            )
            assert "member_id" in member

        # 3. ثبت اولین قرائت
        reading = service.record_first_reading(pilot, sensor1["sensor_id"], 25.5)
        assert "reading_at" in reading

        # 4. تکمیل اولین چرخه MRV
        mrv = service.complete_first_mrv_cycle(pilot, 90)
        assert "cycle_id" in mrv
        assert mrv["verified"] == True
        assert "blockchain_tx" in mrv

        # 5. صدور اولین پرداخت PES
        members = service.members[pilot]
        payment = service.issue_first_pes_payment(
            pilot, members[0].member_id, 100.0
        )
        assert payment["status"] == "paid"
        assert "blockchain_tx" in payment

        # 6. بررسی وضعیت نهایی
        status = service.get_pilot_status(pilot)
        assert status["status"] == PilotStatus.FIRST_PES_PAID.value

    def test_all_pilots_can_be_activated(self):
        """تست اینکه همه پایلوت‌ها قابل فعال‌سازی هستند"""
        service = PilotActivationService()

        for pilot in service.PILOTS:
            # استقرار یک حسگر
            sensor = service.deploy_sensor(pilot, "soil_moisture", 0.0, 0.0)
            assert sensor["pilot_site"] == pilot

            # ثبت 10 عضو
            for i in range(10):
                service.register_community_member(
                    pilot, f"Member {i}", "farmer", "male", "adult"
                )

            # بررسی وضعیت
            status = service.get_pilot_status(pilot)
            assert status["sensors_deployed"] >= 1
            assert status["members_registered"] >= 10

    def test_mrv_calculation_accuracy(self):
        """تست دقت محاسبات MRV"""
        service = PilotActivationService()
        pilot = "dishmok"

        # استقرار حسگرها
        service.deploy_sensor(pilot, "soil_moisture", 30.9, 51.4)

        # تکمیل MRV
        mrv = service.complete_first_mrv_cycle(pilot)

        # بررسی مقادیر
        assert mrv["total_sequestration_tCO2"] > 0
        assert mrv["water_saved_m3"] > 0

    def test_pes_payment_calculation(self):
        """تست محاسبه پرداخت PES"""
        service = PilotActivationService()
        pilot = "dishmok"

        # استقرار و MRV
        service.deploy_sensor(pilot, "soil_moisture", 30.9, 51.4)
        service.register_community_member(pilot, "Test", "farmer", "male", "adult")
        service.complete_first_mrv_cycle(pilot)

        # پرداخت
        member = service.members[pilot][0]
        payment = service.issue_first_pes_payment(pilot, member.member_id, 150.0)

        assert payment["amount_usd"] == 150.0
        assert payment["status"] == "paid"


class TestBlockchainIntegration:
    """تست یکپارچگی بلاکچین"""

    def test_mrv_blockchain_hash(self):
        """تست تولید hash بلاکچین برای MRV"""
        service = PilotActivationService()
        service.deploy_sensor("dishmok", "soil_moisture", 30.9, 51.4)
        mrv = service.complete_first_mrv_cycle("dishmok")

        assert mrv["blockchain_tx"].startswith("0x")
        assert len(mrv["blockchain_tx"]) == 66  # 0x + 64 chars

    def test_pes_blockchain_hash(self):
        """تست تولید hash بلاکچین برای PES"""
        service = PilotActivationService()
        service.deploy_sensor("dishmok", "soil_moisture", 30.9, 51.4)
        service.register_community_member("dishmok", "Test", "farmer", "male", "adult")
        service.complete_first_mrv_cycle("dishmok")

        member = service.members["dishmok"][0]
        payment = service.issue_first_pes_payment("dishmok", member.member_id, 100.0)

        assert payment["blockchain_tx"].startswith("0x")
        assert len(payment["blockchain_tx"]) == 66


class TestMultiContinentSupport:
    """تست پشتیبانی از چند قاره"""

    def test_all_continents_represented(self):
        """تست حضور همه قاره‌ها"""
        service = PilotActivationService()
        continents = set(p["continent"] for p in service.PILOTS.values())

        assert "Asia" in continents
        assert "Africa" in continents
        assert "Oceania" in continents
        assert "South America" in continents
        assert len(continents) == 4

    def test_country_diversity(self):
        """تست تنوع کشورها"""
        service = PilotActivationService()
        countries = set(p["country"] for p in service.PILOTS.values())

        assert len(countries) == 9
        assert "Iran" in countries
        assert "Morocco" in countries
        assert "Australia" in countries