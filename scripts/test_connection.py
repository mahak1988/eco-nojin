"""
تست اتصال به دیتابیس - نسخه امن
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.logger import UnifiedLogger

logger = UnifiedLogger.get_logger('test_connection')


def test_database_connection():
    """تست اتصال به PostgreSQL"""
    try:
        import psycopg2
        from dotenv import load_dotenv
        
        load_dotenv()
        
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'econojin'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', ''),
            port=os.getenv('DB_PORT', '5432')
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        logger.info(f"✅ Connected to: {version}")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        return False


if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)
