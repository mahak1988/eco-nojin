#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Builder Module
Provides common functionality for all builders.
"""
import logging
import shutil
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# تعیین داینامیک ریشه پروژه بر اساس مسیر این فایل
# مسیر: scripts/builders/base_builder.py -> ریشه: parent.parent.parent
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
CONTRACTS_DIR = PROJECT_ROOT / "contracts"


class BaseBuilder:
    """کلاس پایه برای تمام سازنده‌ها با قابلیت پشتیبان‌گیری خودکار"""

    def __init__(self, name: str):
        self.name = name
        self.backup_dir = PROJECT_ROOT / f".{name}_backup"
        self.backup_dir.mkdir(exist_ok=True)
        self.files_created = []

    def backup(self, path: Path):
        """ایجاد پشتیبان امن قبل از بازنویسی فایل"""
        if not path.exists():
            return
        try:
            rel = path.relative_to(PROJECT_ROOT)
            dest = self.backup_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup = dest.parent / f"{dest.stem}_{ts}{dest.suffix}"
            shutil.copy2(path, backup)
            logger.debug(f"  📦 Backed up: {rel}")
        except Exception as e:
            logger.error(f"  ⚠️ Backup failed for {path}: {e}")

    def write(self, path: Path, content: str):
        """نوشتن محتوا با مدیریت خودکار پشتیبان و دایرکتوری‌ها"""
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            self.backup(path)
        path.write_text(content, encoding="utf-8")
        self.files_created.append(path.relative_to(PROJECT_ROOT))
        logger.info(f"  ✓ {path.relative_to(PROJECT_ROOT)}")

    def get_stats(self) -> dict:
        return {
            "name": self.name,
            "files_created": len(self.files_created),
            "files": [str(f) for f in self.files_created],
        }
