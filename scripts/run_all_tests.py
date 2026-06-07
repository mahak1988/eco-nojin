"""Integrated Test Runner"""
import os
import sys

from scripts.core.logger import UnifiedLogger

logger = UnifiedLogger.get_logger(__name__)

PROJECT = r"D:\\econojin.com"
sys.path.insert(0, PROJECT)


def test_imports():
    try:
        from scripts.api.main import app
        from scripts.db.connection import get_connection
        from scripts.models.soil_carbon.aquacrop import AquaCropModel

        return True
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return False


def test_aquacrop():
    try:
        from scripts.models.soil_carbon.aquacrop import AquaCropModel

        m = AquaCropModel()
        r = m.run({"temp_avg_c": 20}, {"field_capacity": 0.3}, {"growing_days": 100})
        return r and "yield_kg_ha" in r
    except Exception as e:
        return False


if __name__ == "__main__":
    logger.info("=== Test Suite ===")
    logger.error(f"Imports: {'PASS' if test_imports() else 'FAIL'}")
    logger.error(f"AquaCrop: {'PASS' if test_aquacrop() else 'FAIL'}")
