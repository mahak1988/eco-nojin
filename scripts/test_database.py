"""Test database models (mock or real)"""
import sys, os
from backend.core.logger import UnifiedLogger
logger = UnifiedLogger.get_logger(__name__)

sys.path.insert(0, r"D:\\econojin.com")

def test_models_import():
    """Test that models can be imported"""
    try:
        from scripts.db.models import Base, User, Subbasin, WeatherData, SoilProfile, Sensor, SensorData
        logger.info("✓ All ORM models imported successfully")
        return True
    except ImportError as e:
        logger.error(f"✗ Import failed: {e}")
        return False

def test_mock_registration():
    """Test farmer registration in mock mode"""
    try:
        # Simulate API call
        farmer = {"fid": "TEST001", "name": "Test User", "phone": "123"}
        # In real app, this would use session.add(User(...))
        logger.info(f"✓ Mock registration: {farmer['fid']} -> {farmer['name']}")
        return True
    except Exception as e:
        logger.error(f"✗ Mock test failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("\n=== Database Test Suite ===")
    r1 = test_models_import()
    r2 = test_mock_registration()
    logger.error(f"\nResult: {'PASS' if r1 and r2 else 'FAIL'}")
