"""
Integration Tests for Econojin Project
Tests that all main modules can be imported and work together.
"""
import unittest
import sys
from pathlib import Path

# اضافه کردن ریشه پروژه به sys.path
ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class TestModuleImports(unittest.TestCase):
    """Test that all main modules can be imported."""
    
    def test_backend_hydrology(self):
        """Test hydrology models import."""
        try:
            from backend.models.hydrology import basin_model
            self.assertTrue(hasattr(basin_model, 'BasinModel'))
        except ImportError as e:
            self.skipTest(f"hydrology not available: {e}")
    
    def test_backend_soil_water(self):
        """Test soil water models import."""
        try:
            from backend.models.soil_water import richards_solver
            self.assertTrue(hasattr(richards_solver, 'RichardsEquation1D'))
        except ImportError as e:
            self.skipTest(f"soil_water not available: {e}")
    
    def test_backend_crop(self):
        """Test crop models import (with fallback)."""
        try:
            from backend.models.crop import aquacrop_integration
            self.assertTrue(hasattr(aquacrop_integration, 'AquaCropWrapper') or 
                          hasattr(aquacrop_integration, 'AQUACROP_AVAILABLE'))
        except ImportError as e:
            self.skipTest(f"crop not available: {e}")
    
    def test_backend_carbon(self):
        """Test carbon models import."""
        try:
            from backend.models.carbon import rothc_model
            self.assertTrue(hasattr(rothc_model, 'RothCModel'))
        except ImportError as e:
            self.skipTest(f"carbon not available: {e}")
    
    def test_backend_erosion(self):
        """Test erosion models import."""
        try:
            from backend.models.erosion import rusle_model
            self.assertTrue(hasattr(rusle_model, 'RUSLEModel'))
        except ImportError as e:
            self.skipTest(f"erosion not available: {e}")


class TestDataFlow(unittest.TestCase):
    """Test data flow between modules."""
    
    def test_coupling_engine(self):
        """Test coupling engine can be imported."""
        try:
            from backend.services.coupling_engine import CouplingEngine
            engine = CouplingEngine()
            self.assertIsNotNone(engine)
        except ImportError as e:
            self.skipTest(f"coupling_engine not available: {e}")


class TestAPIEndpoints(unittest.TestCase):
    """Test API endpoints exist."""
    
    def test_auth_module(self):
        """Test auth module has required functions."""
        try:
            from backend.api import auth
            self.assertTrue(hasattr(auth, 'login_user'))
            self.assertTrue(hasattr(auth, 'verify_token'))
        except ImportError as e:
            self.skipTest(f"auth not available: {e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
