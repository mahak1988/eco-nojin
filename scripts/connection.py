"""Database connection module"""
import os

from dotenv import load_dotenv

from scripts.core.logger import UnifiedLogger

logger = UnifiedLogger.get_logger(__name__)

load_dotenv()


def get_connection(autocommit=False):
    """Create PostgreSQL connection"""
    import psycopg2

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "economugin"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )
    if autocommit:
        conn.autocommit = True
    return conn


if __name__ == "__main__":
    try:
        c = get_connection()
        cur = c.cursor()
        cur.execute("SELECT 1")
        logger.info("DB connection test: OK")
        cur.close()
        c.close()
    except Exception as e:
        logger.info(f"DB connection test: {e}")
