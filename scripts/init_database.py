"""Database initialization with PostGIS"""
import os
import sys

sys.path.insert(0, r"D:\\econojin.com")
from scripts.core.logger import UnifiedLogger
from scripts.db.connection import get_connection

logger = UnifiedLogger.get_logger(__name__)


def init_database():
    """Create tables for Economugin"""
    logger.info("[INFO] Initializing database...")
    try:
        import psycopg2

        conn = get_connection(autocommit=True)
        cur = conn.cursor()

        cur.execute("CREATE EXTENSION IF NOT EXISTS postgis")
        logger.info("[OK] PostGIS enabled")

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                full_name VARCHAR(255),
                role VARCHAR(50) DEFAULT 'farmer',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        logger.info("[OK] Table: users")

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS weather_data (
                id SERIAL PRIMARY KEY,
                subbasin_code VARCHAR(50),
                date DATE,
                temp_avg_c DECIMAL(5,2),
                precipitation_mm DECIMAL(8,2),
                UNIQUE(subbasin_code, date)
            )
        """
        )
        logger.info("[OK] Table: weather_data")

        cur.close()
        conn.close()
        logger.info("[SUCCESS] Database ready")
        return True
    except ImportError:
        logger.error("[ERROR] psycopg2 not installed")
        return False
    except Exception as e:
        logger.error(f"[ERROR] {e}")
        return False


if __name__ == "__main__":
    init_database()
