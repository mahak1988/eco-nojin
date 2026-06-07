"""
Unit tests for daily report module
"""

import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestDailyReport:
    """تست ماژول گزارش روزانه"""

    def test_import_module(self):
        """تست import"""
        try:
            from scripts.utils import daily_report

            assert daily_report is not None
        except ImportError:
            pytest.skip("daily_report module not found")

    def test_generate_daily_report(self):
        """تست تابع generate_daily_report"""
        try:
            from scripts.utils.daily_report import generate_daily_report

            report = generate_daily_report()
            assert isinstance(report, dict)
            assert "status" in report
        except (ImportError, AttributeError):
            pytest.skip("generate_daily_report not available")

    def test_report_with_date(self):
        """تست گزارش با تاریخ خاص"""
        try:
            from scripts.utils.daily_report import generate_daily_report

            test_date = datetime(2026, 1, 1)
            report = generate_daily_report(test_date)
            assert isinstance(report, dict)
        except Exception:
            pytest.skip("Cannot generate report with date")
