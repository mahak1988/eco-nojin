"""PostgreSQL Connection Setup"""
import os, sys
from scripts.core.logger import UnifiedLogger
logger = UnifiedLogger.get_logger(__name__)


PROJECT = r"D:\\econojin.com"
sys.path.insert(0, PROJECT)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT, ".env"))
except Exception as e:
    pass

DB = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "economugin"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "")
}

def test_connection():
    logger.info(f"[INFO] Testing connection to {DB['database']}@{DB['host']}")
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=DB["host"],
            port=DB["port"],
            database="postgres",
            user=DB["user"],
            password=DB["password"]
        )
        cur = conn.cursor()
        cur.execute("SELECT version()")
        ver = cur.fetchone()[0]
        cur.close()
        conn.close()
        logger.info(f"[OK] PostgreSQL: {ver[:50]}...")
        return True
    except ImportError:
        logger.error("[ERROR] Install: pip install psycopg2-binary")
        return False
    except Exception as e:
        logger.error(f"[ERROR] Connection failed: {str(e)[:150]}")
        return False

def create_database():
    logger.info(f"[INFO] Creating database '{DB['database']}'...")
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=DB["host"],
            port=DB["port"],
            database="postgres",
            user=DB["user"],
            password=DB["password"]
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = %s", (DB["database"],))
        if not cur.fetchone():
            cur.execute(f'CREATE DATABASE "{DB["database"]}"')
            logger.info("[OK] Database created")
        else:
            logger.info("[INFO] Database already exists")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    logger.info("=== PostgreSQL Setup ===")
    ok1 = test_connection()
    ok2 = create_database() if ok1 else False
    logger.error(f"\n{'OK' if ok1 and ok2 else 'WARN'}: {'Ready' if ok1 and ok2 else 'Check errors above'}")
