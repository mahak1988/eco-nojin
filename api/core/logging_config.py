"""Logging configuration for Econojin."""
import logging
import sys
from pathlib import Path


def setup_logging():
    """Configure logging for the application."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "econojin.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # تنظیمات خاص برای ماژول‌ها
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("web3").setLevel(logging.INFO)
    
    return logging.getLogger("econojin")
