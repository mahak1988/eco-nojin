"""API endpoint tester - fixed expectations"""
import sys

from scripts.core.logger import UnifiedLogger

logger = UnifiedLogger.get_logger(__name__)

sys.path.insert(0, r"D:\\econojin.com")


def test_api():
    logger.info("=== API Tester ===")
    try:
        from fastapi.testclient import TestClient

        from scripts.api.main import app

        client = TestClient(app)

        tests = [
            ("GET /", "/", ["message", "project"]),
            ("GET /health", "/health", ["status", "service"]),
            ("GET /models", "/models", ["count", "list"]),
            ("GET /openapi.json", "/openapi.json", ["openapi"]),
        ]

        passed = 0
        for name, path, keys in tests:
            logger.info(f"[TEST] {name}...", end=" ")
            resp = client.get(path)
            if resp.status_code == 200:
                data = resp.json()
                if all(k in data for k in keys):
                    logger.info("PASS")
                    passed += 1
                else:
                    logger.error(f"FAIL (missing: {[k for k in keys if k not in data]})")
            else:
                logger.error(f"FAIL ({resp.status_code})")

        logger.info(f"\nResult: {passed}/{len(tests)} passed")
        return passed == len(tests)
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


if __name__ == "__main__":
    test_api()
