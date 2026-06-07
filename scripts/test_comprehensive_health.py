# -*- coding: utf-8 -*-
"""
Comprehensive Health Test Suite for Econojin Project

این اسکریپت موارد زیر را تست می‌کند:
1. Import موفقیت‌آمیز ماژول‌های اصلی
2. Sentinel-2 Client در حالت simulation
3. Satellite Verification در حالت simulation
4. AquaCrop Integration با fallback داخلی
5. AgroforestryDesigner (LER, Spacing, Carbon)
6. یکپارچگی بین ماژول‌ها

اجرا:
    python -m pytest tests/test_comprehensive_health.py -v
    یا
    python tests/test_comprehensive_health.py
"""

import importlib
import os
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

# اضافه کردن ریشه پروژه به sys.path
ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class TestModuleImports(unittest.TestCase):
    """بررسی import موفقیت‌آمیز ماژول‌های اصلی"""

    def test_sentinel2_import(self):
        """core.gaia.sentinel2 باید import شود"""
        try:
            from core.gaia import sentinel2

            self.assertTrue(hasattr(sentinel2, "Sentinel2Client"))
        except ImportError as e:
            self.fail(f"Import sentinel2 failed: {e}")

    def test_satellite_import(self):
        """core.gaia.satellite باید import شود"""
        try:
            from core.gaia import satellite

            self.assertTrue(hasattr(satellite, "Sentinel2Client"))
            self.assertTrue(hasattr(satellite, "SatelliteVerification"))
        except ImportError as e:
            self.fail(f"Import satellite failed: {e}")

    def test_aquacrop_integration_import(self):
        """backend.models.crop.aquacrop_integration باید import شود"""
        try:
            from backend.models.crop import aquacrop_integration

            self.assertTrue(hasattr(aquacrop_integration, "AquaCropWrapper"))
            self.assertTrue(hasattr(aquacrop_integration, "AgroforestryDesigner"))
            self.assertTrue(hasattr(aquacrop_integration, "CropConfig"))
            self.assertTrue(hasattr(aquacrop_integration, "ClimateInput"))
            self.assertTrue(hasattr(aquacrop_integration, "SoilConfig"))
        except ImportError as e:
            self.fail(f"Import aquacrop_integration failed: {e}")

    def test_core_gaia_modules(self):
        """تمام ماژول‌های core/gaia باید import شوند"""
        modules = [
            "core.gaia.calculator",
            "core.gaia.scoring",
            "core.gaia.certificates",
            "core.gaia.blockchain_simulator",
            "core.gaia.carbon_model_simulator",
            "core.gaia.iot_simulator",
            "core.gaia.oracle",
            "core.gaia.verification",
        ]
        for module_name in modules:
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                self.fail(f"Import {module_name} failed: {e}")


class TestSentinel2Client(unittest.TestCase):
    """تست Sentinel2Client در حالت simulation"""

    def setUp(self):
        """ایجاد instance در حالت simulation (بدون credentials)"""
        from core.gaia.sentinel2 import Sentinel2Client

        # پاک کردن credentials از environment
        with patch.dict(os.environ, {}, clear=True):
            self.client = Sentinel2Client()

    def test_simulation_mode_enabled(self):
        """در حالت simulation، credentials نباید موجود باشد"""
        self.assertTrue(self.client.simulation_mode)

    def test_mock_search(self):
        """_mock_search باید داده‌های شبیه‌سازی شده برگرداند"""
        result = self.client._mock_search(
            lat=35.7, lng=51.4, start=datetime.now() - timedelta(days=30), end=datetime.now()
        )
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn("id", result[0])
        self.assertIn("simulation", result[0])
        self.assertTrue(result[0]["simulation"])

    def test_mock_ndvi(self):
        """_mock_ndvi باید عددی بین 0 و 1 برگرداند"""
        ndvi = self.client._mock_ndvi(lat=35.7, lng=51.4, date=datetime.now())
        self.assertIsInstance(ndvi, float)
        self.assertGreaterEqual(ndvi, -1.0)
        self.assertLessEqual(ndvi, 1.0)

    def test_search_images_simulation(self):
        """search_images در simulation mode باید mock برگرداند"""
        result = self.client.search_images(
            lat=35.7,
            lng=51.4,
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now(),
            max_cloud_cover=20.0,
        )
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_calculate_ndvi_simulation(self):
        """calculate_ndvi در simulation mode باید عدد برگرداند"""
        ndvi = self.client.calculate_ndvi(lat=35.7, lng=51.4, date=datetime.now())
        self.assertIsInstance(ndvi, float)

    def test_verify_activity_simulation(self):
        """verify_activity باید نتیجه با فیلدهای مورد انتظار برگرداند"""
        result = self.client.verify_activity(
            lat=35.7,
            lng=51.4,
            activity_date=datetime.now() - timedelta(days=180),
            activity_type="tree_planting",
        )
        self.assertIsInstance(result, dict)
        self.assertIn("verified", result)
        self.assertIn("ndvi_before", result)
        self.assertIn("ndvi_after", result)
        self.assertIn("ndvi_change", result)
        self.assertIn("confidence", result)
        self.assertIn("activity_type", result)
        self.assertEqual(result["activity_type"], "tree_planting")


class TestSatelliteVerification(unittest.TestCase):
    """تست Satellite Verification در حالت simulation"""

    def setUp(self):
        from core.gaia.satellite import Sentinel2Client

        with patch.dict(os.environ, {}, clear=True):
            self.client = Sentinel2Client()

    def test_simulation_mode(self):
        """Simulation mode باید فعال باشد"""
        self.assertTrue(self.client.simulation_mode)

    def test_simulate_search(self):
        """_simulate_search باید داده ساختگی برگرداند"""
        result = self.client._simulate_search(
            lat=35.7,
            lng=51.4,
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now(),
        )
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn("simulation", result[0])
        self.assertTrue(result[0]["simulation"])

    def test_simulate_ndvi_before_activity(self):
        """NDVI قبل از فعالیت باید پایه باشد"""
        activity_date = datetime.now() - timedelta(days=100)
        ndvi = self.client._simulate_ndvi(
            lat=35.7, lng=51.4, date=activity_date - timedelta(days=30), activity_date=activity_date
        )
        self.assertIsInstance(ndvi, float)
        self.assertGreater(ndvi, 0)

    def test_simulate_ndvi_after_activity(self):
        """NDVI بعد از فعالیت باید بیشتر باشد (رشد درخت)"""
        activity_date = datetime.now() - timedelta(days=365)
        ndvi_before = self.client._simulate_ndvi(
            lat=35.7, lng=51.4, date=activity_date - timedelta(days=30), activity_date=None
        )
        ndvi_after = self.client._simulate_ndvi(
            lat=35.7,
            lng=51.4,
            date=activity_date + timedelta(days=180),
            activity_date=activity_date,
        )
        # NDVI بعد از فعالیت باید بیشتر باشد
        self.assertGreater(ndvi_after, ndvi_before)

    def test_verify_activity_returns_satellite_verification(self):
        """verify_activity باید SatelliteVerification برگرداند"""
        from core.gaia.satellite import SatelliteVerification

        result = self.client.verify_activity(
            lat=35.7,
            lng=51.4,
            activity_date=datetime.now() - timedelta(days=365),
            activity_type="tree_planting",
        )
        self.assertIsInstance(result, SatelliteVerification)
        self.assertIsInstance(result.verified, bool)
        self.assertIsNotNone(result.ndvi_before)
        self.assertIsNotNone(result.ndvi_after)


class TestAquaCropIntegration(unittest.TestCase):
    """تست AquaCrop Integration با fallback داخلی"""

    def setUp(self):
        import numpy as np
        import pandas as pd
        from backend.models.crop.aquacrop_integration import (
            AquaCropWrapper,
            ClimateInput,
            CropConfig,
            SoilConfig,
        )

        self.wrapper = AquaCropWrapper()

        # Crop Configuration - گندم
        self.crop = CropConfig(
            crop_type="wheat",
            planting_date="2025-10-15",
            harvest_date="2026-06-15",
            initial_canopy_cover=0.5,
            max_canopy_cover=95.0,
            max_root_depth=1.2,
            max_crop_height=1.0,
            p_upper=0.55,
            p_lower=0.75,
            harvest_index_max=0.48,
            biomass_wue=20.0,  # g/m²/mm
        )

        # Soil Configuration
        self.soil = SoilConfig(
            total_available_water=150.0,  # mm/m
            saturation_point=450.0,
            field_capacity=350.0,
            wilting_point=150.0,
            initial_depletion=0.3,
            depth=1.2,
        )

        # Climate Data - 365 روز
        n_days = 365
        dates = pd.date_range("2025-10-15", periods=n_days, freq="D")
        np.random.seed(42)
        self.climate = ClimateInput(
            date=dates,
            t_min=np.random.normal(10, 5, n_days),
            t_max=np.random.normal(20, 5, n_days),
            precip=np.random.exponential(2, n_days),
            et0=np.random.normal(3, 1, n_days),
            co2=np.full(n_days, 415.0),
        )

    def test_setup_with_fallback(self):
        """setup باید با fallback داخلی کار کند"""
        self.wrapper.setup(self.crop, self.soil, self.climate)
        self.assertIsNotNone(self.wrapper.internal_config)

    def test_run_internal_model(self):
        """اجرای مدل داخلی باید نتیجه معتبر برگرداند"""
        self.wrapper.setup(self.crop, self.soil, self.climate)
        result = self.wrapper.run()

        self.assertIsInstance(result, dict)
        self.assertIn("date", result)
        self.assertIn("canopy_cover", result)
        self.assertIn("biomass", result)
        self.assertIn("yield", result)
        self.assertIn("et_actual", result)
        self.assertIn("soil_water", result)
        self.assertIn("final_yield", result)
        self.assertIn("total_et", result)
        self.assertIn("water_productivity", result)

    def test_canopy_cover_dynamics(self):
        """canopy cover باید از مقدار اولیه رشد کند"""
        import numpy as np

        self.wrapper.setup(self.crop, self.soil, self.climate)
        result = self.wrapper.run()

        canopy = result["canopy_cover"]
        # canopy باید در طول زمان رشد کند
        self.assertGreater(canopy.max(), self.crop.initial_canopy_cover)

    def test_positive_final_yield(self):
        """بازده نهایی باید مثبت باشد"""
        self.wrapper.setup(self.crop, self.soil, self.climate)
        result = self.wrapper.run()
        self.assertGreater(result["final_yield"], 0)

    def test_water_productivity_calculation(self):
        """Water Productivity باید محاسبه شود"""
        self.wrapper.setup(self.crop, self.soil, self.climate)
        result = self.wrapper.run()
        self.assertGreaterEqual(result["water_productivity"], 0)


class TestAgroforestryDesigner(unittest.TestCase):
    """تست AgroforestryDesigner"""

    def setUp(self):
        from backend.models.crop.aquacrop_integration import AgroforestryDesigner

        self.designer = AgroforestryDesigner()

    def test_calculate_ler_advantage(self):
        """LER > 1 نشان‌دهنده مزیت agroforestry است"""
        ler = self.designer.calculate_ler(
            monocrop_yield=5.0, tree_yield=10.0, intercrop_yield=3.5, tree_intercrop_yield=7.0
        )
        # LER = 3.5/5 + 7/10 = 0.7 + 0.7 = 1.4
        self.assertAlmostEqual(ler, 1.4, places=2)
        self.assertGreater(ler, 1.0)

    def test_calculate_ler_zero_denominator(self):
        """LER با مخرج صفر باید صفر برگرداند"""
        ler = self.designer.calculate_ler(
            monocrop_yield=0, tree_yield=0, intercrop_yield=3.5, tree_intercrop_yield=7.0
        )
        self.assertEqual(ler, 0)

    def test_design_spacing_east_west(self):
        """Spacing برای east-west باید uniformity بالاتری داشته باشد"""
        result = self.designer.design_spacing(
            tree_height=15.0, crop_light_requirement=0.6, row_orientation="east-west"
        )
        self.assertIn("recommended_spacing_m", result)
        self.assertIn("shadow_length_m", result)
        self.assertIn("shade_uniformity", result)
        self.assertIn("estimated_ler", result)
        self.assertEqual(result["shade_uniformity"], 0.8)
        self.assertGreater(result["recommended_spacing_m"], 0)

    def test_design_spacing_north_south(self):
        """Spacing برای north-south باید uniformity پایین‌تری داشته باشد"""
        result = self.designer.design_spacing(
            tree_height=15.0, crop_light_requirement=0.6, row_orientation="north-south"
        )
        self.assertEqual(result["shade_uniformity"], 0.6)

    def test_estimate_carbon_sequestration(self):
        """تخمین کربن باید مقادیر معتبر برگرداند"""
        result = self.designer.estimate_carbon_sequestration(
            tree_species="walnut",
            tree_density=100,
            simulation_years=20,
            climate_zone="temperate_broadleaf",
        )
        self.assertIn("annual_sequestration_t_c_per_ha", result)
        self.assertIn("cumulative_sequestration", result)
        self.assertIn("co2_equivalent_t_per_ha_20yr", result)
        self.assertIn("methodology", result)

        # مقادیر باید مثبت باشند
        self.assertGreater(result["annual_sequestration_t_c_per_ha"], 0)
        self.assertGreater(result["cumulative_sequestration"]["year_20"], 0)
        self.assertGreater(result["co2_equivalent_t_per_ha_20yr"], 0)

    def test_carbon_sequestration_increases_over_time(self):
        """کربن ذخیره‌شده باید با زمان افزایش یابد"""
        result = self.designer.estimate_carbon_sequestration(
            tree_species="oak",
            tree_density=200,
            simulation_years=20,
            climate_zone="temperate_broadleaf",
        )
        y5 = result["cumulative_sequestration"]["year_5"]
        y10 = result["cumulative_sequestration"]["year_10"]
        y20 = result["cumulative_sequestration"]["year_20"]
        self.assertLess(y5, y10)
        self.assertLess(y10, y20)


class TestCopernicusAPIKnowledge(unittest.TestCase):
    """تست دانش درباره Copernicus Data Space Ecosystem"""

    def test_catalogue_url(self):
        """Sentinel-2 Client باید URL صحیح Catalogue API را داشته باشد"""
        from core.gaia.sentinel2 import Sentinel2Client

        expected = "https://catalogue.dataspace.copernicus.eu/odata/v1"
        self.assertEqual(Sentinel2Client.CATALOG_URL, expected)

    def test_process_url(self):
        """Sentinel Hub Process API باید URL صحیح داشته باشد"""
        from core.gaia.sentinel2 import Sentinel2Client

        expected = "https://sh.dataspace.copernicus.eu/api/v1/process"
        self.assertEqual(Sentinel2Client.PROCESS_URL, expected)

    def test_token_url(self):
        """OAuth Token URL باید صحیح باشد"""
        from core.gaia.sentinel2 import Sentinel2Client

        expected = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
        self.assertEqual(Sentinel2Client.TOKEN_URL, expected)


class TestIntegration(unittest.TestCase):
    """تست یکپارچگی بین ماژول‌ها"""

    def test_full_workflow_simulation(self):
        """Workflow کامل: ثبت فعالیت → تایید ماهواره‌ای → طراحی agroforestry"""
        import numpy as np
        import pandas as pd
        from backend.models.crop.aquacrop_integration import (
            AgroforestryDesigner,
            AquaCropWrapper,
            ClimateInput,
            CropConfig,
            SoilConfig,
        )
        from core.gaia.satellite import Sentinel2Client

        # مرحله 1: ثبت فعالیت (tree planting)
        activity_date = datetime.now() - timedelta(days=365)
        lat, lng = 35.7, 51.4

        # مرحله 2: تایید ماهواره‌ای
        client = Sentinel2Client()
        verification = client.verify_activity(
            lat=lat, lng=lng, activity_date=activity_date, activity_type="tree_planting"
        )
        self.assertIsNotNone(verification.verified)

        # مرحله 3: شبیه‌سازی رشد محصول
        wrapper = AquaCropWrapper()
        crop = CropConfig(
            crop_type="wheat",
            planting_date="2025-10-15",
            harvest_date="2026-06-15",
            initial_canopy_cover=0.5,
            max_canopy_cover=95.0,
            max_root_depth=1.2,
            max_crop_height=1.0,
            p_upper=0.55,
            p_lower=0.75,
            harvest_index_max=0.48,
            biomass_wue=20.0,
        )
        soil = SoilConfig(
            total_available_water=150.0,
            saturation_point=450.0,
            field_capacity=350.0,
            wilting_point=150.0,
            initial_depletion=0.3,
            depth=1.2,
        )
        n_days = 240
        dates = pd.date_range("2025-10-15", periods=n_days, freq="D")
        np.random.seed(42)
        climate = ClimateInput(
            date=dates,
            t_min=np.random.normal(10, 5, n_days),
            t_max=np.random.normal(20, 5, n_days),
            precip=np.random.exponential(2, n_days),
            et0=np.random.normal(3, 1, n_days),
        )
        wrapper.setup(crop, soil, climate)
        crop_result = wrapper.run()
        self.assertGreater(crop_result["final_yield"], 0)

        # مرحله 4: طراحی agroforestry
        designer = AgroforestryDesigner()
        spacing = designer.design_spacing(
            tree_height=15.0, crop_light_requirement=0.6, row_orientation="east-west"
        )
        self.assertGreater(spacing["recommended_spacing_m"], 0)

        ler = designer.calculate_ler(
            monocrop_yield=crop_result["final_yield"],
            tree_yield=1000.0,
            intercrop_yield=crop_result["final_yield"] * 0.7,
            tree_intercrop_yield=700.0,
        )
        self.assertGreater(ler, 1.0)


def run_tests():
    """اجرای تست‌ها و تولید گزارش"""
    print("=" * 70)
    print("🧪 اجرای تست جامع سلامت پروژه Econojin")
    print("=" * 70)
    print(f"⏰ زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📂 ریشه پروژه: {ROOT_DIR}")
    print()

    # ایجاد Test Suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # اضافه کردن کلاس‌های تست
    test_classes = [
        TestModuleImports,
        TestSentinel2Client,
        TestSatelliteVerification,
        TestAquaCropIntegration,
        TestAgroforestryDesigner,
        TestCopernicusAPIKnowledge,
        TestIntegration,
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # اجرای تست‌ها
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # گزارش نهایی
    print("\n" + "=" * 70)
    print("📊 گزارش نهایی")
    print("=" * 70)
    print(f"  تعداد کل تست‌ها: {result.testsRun}")
    print(f"  ✅ موفق: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  ❌ ناموفق: {len(result.failures)}")
    print(f"  ⚠️ خطا: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n🎉 تمام تست‌ها با موفقیت پاس شدند!")
        return 0
    else:
        print("\n⚠️ برخی تست‌ها ناموفق بودند:")
        for test, traceback in result.failures + result.errors:
            print(f"  ❌ {test}")
        return 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
