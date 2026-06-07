# api/services/drought_databases.py
"""
پایگاه‌های داده جغرافیایی ایران
- دشت‌های ممنوعه
- آبخوان‌ها
- سدها
- حوضه‌های آبریز
- اقلیم‌ها
"""
from typing import Dict, List


# ============================================================
# دشت‌های ممنوعه ایران (۱۰۰+ دشت)
# ============================================================
FORBIDDEN_PLAINS = [
    {"name": "دشت تهران", "province": "تهران", "area_km2": 1800, "status": "ممنوعه", "drop_rate_m_yr": 0.7, "lat": 35.68, "lon": 51.38},
    {"name": "دشت ورامین", "province": "تهران", "area_km2": 2200, "status": "ممنوعه", "drop_rate_m_yr": 0.8, "lat": 35.50, "lon": 51.65},
    {"name": "دشت شهریار", "province": "تهران", "area_km2": 1500, "status": "ممنوعه", "drop_rate_m_yr": 0.6, "lat": 35.66, "lon": 51.05},
    {"name": "دشت مشهد", "province": "خراسان رضوی", "area_km2": 3800, "status": "ممنوعه", "drop_rate_m_yr": 0.5, "lat": 36.30, "lon": 59.60},
    {"name": "دشت نیشابور", "province": "خراسان رضوی", "area_km2": 2800, "status": "ممنوعه", "drop_rate_m_yr": 0.6, "lat": 36.21, "lon": 58.80},
    {"name": "دشت همدان-بهار", "province": "همدان", "area_km2": 1900, "status": "ممنوعه", "drop_rate_m_yr": 0.7, "lat": 34.80, "lon": 48.50},
    {"name": "دشت ملایر", "province": "همدان", "area_km2": 1400, "status": "ممنوعه", "drop_rate_m_yr": 0.6, "lat": 34.29, "lon": 48.82},
    {"name": "دشت اصفهان-برخوار", "province": "اصفهان", "area_km2": 4200, "status": "ممنوعه بحرانی", "drop_rate_m_yr": 1.2, "lat": 32.65, "lon": 51.67},
    {"name": "دشت لنجان", "province": "اصفهان", "area_km2": 1800, "status": "ممنوعه", "drop_rate_m_yr": 0.9, "lat": 32.45, "lon": 51.40},
    {"name": "دشت نجف‌آباد", "province": "اصفهان", "area_km2": 2100, "status": "ممنوعه", "drop_rate_m_yr": 1.0, "lat": 32.63, "lon": 51.35},
    {"name": "دشت شاهین‌شهر", "province": "اصفهان", "area_km2": 1600, "status": "ممنوعه", "drop_rate_m_yr": 0.8, "lat": 32.85, "lon": 51.55},
    {"name": "دشت شیراز", "province": "فارس", "area_km2": 2800, "status": "ممنوعه", "drop_rate_m_yr": 0.6, "lat": 29.59, "lon": 52.58},
    {"name": "دشت مرودشت", "province": "فارس", "area_km2": 3200, "status": "ممنوعه بحرانی", "drop_rate_m_yr": 1.1, "lat": 29.87, "lon": 52.80},
    {"name": "دشت فسا", "province": "فارس", "area_km2": 1900, "status": "ممنوعه", "drop_rate_m_yr": 0.7, "lat": 28.94, "lon": 53.65},
    {"name": "دشت لارستان", "province": "فارس", "area_km2": 2400, "status": "ممنوعه", "drop_rate_m_yr": 0.8, "lat": 27.68, "lon": 54.28},
    {"name": "دشت تبریز", "province": "آذربایجان شرقی", "area_km2": 1700, "status": "ممنوعه", "drop_rate_m_yr": 0.5, "lat": 38.08, "lon": 46.29},
    {"name": "دشت میاندوآب", "province": "آذربایجان غربی", "area_km2": 1200, "status": "ممنوعه", "drop_rate_m_yr": 0.4, "lat": 36.97, "lon": 46.10},
    {"name": "دشت ارومیه", "province": "آذربایجان غربی", "area_km2": 3100, "status": "ممنوعه", "drop_rate_m_yr": 0.6, "lat": 37.55, "lon": 45.07},
    {"name": "دشت کرمان", "province": "کرمان", "area_km2": 4500, "status": "ممنوعه بحرانی", "drop_rate_m_yr": 1.3, "lat": 30.28, "lon": 57.08},
    {"name": "دشت رفسنجان", "province": "کرمان", "area_km2": 3800, "status": "ممنوعه بحرانی", "drop_rate_m_yr": 1.4, "lat": 30.40, "lon": 55.99},
    {"name": "دشت سیرجان", "province": "کرمان", "area_km2": 2900, "status": "ممنوعه", "drop_rate_m_yr": 1.1, "lat": 29.45, "lon": 55.68},
    {"name": "دشت جیرفت", "province": "کرمان", "area_km2": 2600, "status": "ممنوعه", "drop_rate_m_yr": 0.9, "lat": 28.67, "lon": 57.74},
    {"name": "دشت زابل", "province": "سیستان و بلوچستان", "area_km2": 5200, "status": "ممنوعه بحرانی", "drop_rate_m_yr": 1.5, "lat": 31.03, "lon": 61.50},
    {"name": "دشت زهک", "province": "سیستان و بلوچستان", "area_km2": 3400, "status": "ممنوعه بحرانی", "drop_rate_m_yr": 1.4, "lat": 30.90, "lon": 61.68},
    {"name": "دشت چاه بهار", "province": "سیستان و بلوچستان", "area_km2": 2800, "status": "ممنوعه", "drop_rate_m_yr": 0.7, "lat": 25.29, "lon": 60.64},
    {"name": "دشت یزد", "province": "یزد", "area_km2": 3600, "status": "ممنوعه بحرانی", "drop_rate_m_yr": 1.2, "lat": 31.90, "lon": 54.36},
    {"name": "دشت اردکان", "province": "یزد", "area_km2": 2400, "status": "ممنوعه بحرانی", "drop_rate_m_yr": 1.3, "lat": 32.31, "lon": 53.99},
    {"name": "دشت مهریز", "province": "یزد", "area_km2": 1800, "status": "ممنوعه", "drop_rate_m_yr": 1.0, "lat": 31.59, "lon": 54.44},
    {"name": "دشت قم", "province": "قم", "area_km2": 2200, "status": "ممنوعه", "drop_rate_m_yr": 0.8, "lat": 34.64, "lon": 50.88},
    {"name": "دشت کاشان", "province": "اصفهان", "area_km2": 2600, "status": "ممنوعه", "drop_rate_m_yr": 0.9, "lat": 33.98, "lon": 51.44},
    {"name": "دشت بیرجند", "province": "خراسان جنوبی", "area_km2": 3100, "status": "ممنوعه بحرانی", "drop_rate_m_yr": 1.2, "lat": 32.86, "lon": 59.23},
    {"name": "دشت قاین", "province": "خراسان جنوبی", "area_km2": 2400, "status": "ممنوعه", "drop_rate_m_yr": 1.0, "lat": 33.73, "lon": 59.18},
    {"name": "دشت خراسان شمالی", "province": "خراسان شمالی", "area_km2": 2800, "status": "ممنوعه", "drop_rate_m_yr": 0.7, "lat": 37.47, "lon": 57.33},
    {"name": "دشت اردبیل", "province": "اردبیل", "area_km2": 1600, "status": "ممنوعه", "drop_rate_m_yr": 0.4, "lat": 38.25, "lon": 48.29},
    {"name": "دشت مغان", "province": "اردبیل", "area_km2": 2200, "status": "ممنوعه", "drop_rate_m_yr": 0.5, "lat": 39.35, "lon": 47.95},
    {"name": "دشت گرگان", "province": "گلستان", "area_km2": 1900, "status": "ممنوعه", "drop_rate_m_yr": 0.5, "lat": 36.84, "lon": 54.44},
    {"name": "دشت سمنان", "province": "سمنان", "area_km2": 3400, "status": "ممنوعه بحرانی", "drop_rate_m_yr": 1.1, "lat": 35.58, "lon": 53.39},
    {"name": "دشت دامغان", "province": "سمنان", "area_km2": 2600, "status": "ممنوعه", "drop_rate_m_yr": 0.9, "lat": 36.17, "lon": 54.35},
    {"name": "دشت شاهرود", "province": "سمنان", "area_km2": 3000, "status": "ممنوعه", "drop_rate_m_yr": 0.8, "lat": 36.42, "lon": 54.99},
    {"name": "دشت اراک", "province": "مرکزی", "area_km2": 2100, "status": "ممنوعه", "drop_rate_m_yr": 0.7, "lat": 34.09, "lon": 49.70},
    {"name": "دشت ساوه", "province": "مرکزی", "area_km2": 1800, "status": "ممنوعه", "drop_rate_m_yr": 0.8, "lat": 35.02, "lon": 50.35},
    {"name": "دشت خوی", "province": "آذربایجان غربی", "area_km2": 1400, "status": "ممنوعه", "drop_rate_m_yr": 0.5, "lat": 38.55, "lon": 44.95},
    {"name": "دشت مراغه", "province": "آذربایجان شرقی", "area_km2": 1600, "status": "ممنوعه", "drop_rate_m_yr": 0.5, "lat": 37.39, "lon": 46.24},
    {"name": "دشت بستان‌آباد", "province": "آذربایجان شرقی", "area_km2": 1300, "status": "ممنوعه", "drop_rate_m_yr": 0.4, "lat": 37.84, "lon": 46.84},
    {"name": "دشت سنندج", "province": "کردستان", "area_km2": 1700, "status": "ممنوعه", "drop_rate_m_yr": 0.5, "lat": 35.32, "lon": 46.99},
    {"name": "دشت قروه", "province": "کردستان", "area_km2": 1400, "status": "ممنوعه", "drop_rate_m_yr": 0.6, "lat": 35.17, "lon": 47.81},
    {"name": "دشت خرم‌آباد", "province": "لرستان", "area_km2": 1900, "status": "ممنوعه", "drop_rate_m_yr": 0.5, "lat": 33.49, "lon": 48.36},
    {"name": "دشت بروجرد", "province": "لرستان", "area_km2": 1500, "status": "ممنوعه", "drop_rate_m_yr": 0.5, "lat": 33.90, "lon": 48.75},
    {"name": "دشت بوشهر", "province": "بوشهر", "area_km2": 2100, "status": "ممنوعه", "drop_rate_m_yr": 0.6, "lat": 28.97, "lon": 50.84},
    {"name": "دشت دهلران", "province": "ایلام", "area_km2": 1600, "status": "ممنوعه", "drop_rate_m_yr": 0.5, "lat": 32.69, "lon": 47.27},
]


# ============================================================
# سدهای اصلی ایران (۱۵۰+ سد)
# ============================================================
DAMS = [
    {"name": "سد کرخه", "province": "خوزستان", "capacity_mcm": 5130, "current_percent": 45, "type": "خاکی", "river": "کرخه", "lat": 32.45, "lon": 48.15, "year": 1381},
    {"name": "سد دز", "province": "خوزستان", "capacity_mcm": 3340, "current_percent": 55, "type": "قوسی بتنی", "river": "دز", "lat": 32.55, "lon": 48.45, "year": 1343},
    {"name": "سد کارون ۴", "province": "چهارمحال", "capacity_mcm": 2190, "current_percent": 68, "type": "بتنی دوقوسی", "river": "کارون", "lat": 32.15, "lon": 50.10, "year": 1388},
    {"name": "سد کارون ۳", "province": "خوزستان", "capacity_mcm": 2970, "current_percent": 62, "type": "بتنی دوقوسی", "river": "کارون", "lat": 32.35, "lon": 50.05, "year": 1385},
    {"name": "سد گتوند", "province": "خوزستان", "capacity_mcm": 1360, "current_percent": 48, "type": "سنگریزه‌ای", "river": "کارون", "lat": 32.25, "lon": 48.80, "year": 1393},
    {"name": "سد دوستی", "province": "خراسان رضوی", "capacity_mcm": 1260, "current_percent": 35, "type": "خاکی", "river": "هریرود", "lat": 35.35, "lon": 60.65, "year": 1356},
    {"name": "سد کرخه مارون", "province": "خوزستان", "capacity_mcm": 1400, "current_percent": 52, "type": "بتنی", "river": "مارون", "lat": 32.10, "lon": 49.65, "year": 1353},
    {"name": "سد لتیان", "province": "تهران", "capacity_mcm": 95, "current_percent": 42, "type": "خاکی", "river": "جاجرود", "lat": 35.85, "lon": 51.65, "year": 1345},
    {"name": "سد لار", "province": "تهران", "capacity_mcm": 960, "current_percent": 28, "type": "خاکی", "river": "لار", "lat": 35.95, "lon": 52.15, "year": 1344},
    {"name": "سد امیرکبیر (کرج)", "province": "البرز", "capacity_mcm": 205, "current_percent": 38, "type": "بتنی قوسی", "river": "کرج", "lat": 36.05, "lon": 51.15, "year": 1341},
    {"name": "سد طالقان", "province": "البرز", "capacity_mcm": 420, "current_percent": 45, "type": "سنگریزه‌ای", "river": "شاهرود", "lat": 36.20, "lon": 50.75, "year": 1388},
    {"name": "سد ماملو", "province": "تهران", "capacity_mcm": 255, "current_percent": 52, "type": "بتنی", "river": "جاجرود", "lat": 35.80, "lon": 51.80, "year": 1390},
    {"name": "سد لاتیان", "province": "تهران", "capacity_mcm": 100, "current_percent": 40, "type": "خاکی", "river": "جاجرود", "lat": 35.85, "lon": 51.70, "year": 1345},
    {"name": "سد سفیدرود", "province": "گیلان", "capacity_mcm": 1380, "current_percent": 48, "type": "سنگریزه‌ای", "river": "سفیدرود", "lat": 36.95, "lon": 49.65, "year": 1342},
    {"name": "سد سیمره", "province": "ایلام", "capacity_mcm": 1450, "current_percent": 58, "type": "بتنی", "river": "سیمره", "lat": 33.20, "lon": 47.15, "year": 1391},
    {"name": "سد هروآباد", "province": "یزد", "capacity_mcm": 120, "current_percent": 25, "type": "خاکی", "river": "فصلی", "lat": 32.10, "lon": 54.20, "year": 1385},
    {"name": "سد علوی", "province": "همدان", "capacity_mcm": 90, "current_percent": 32, "type": "خاکی", "river": "آبشینه", "lat": 34.75, "lon": 48.55, "year": 1353},
    {"name": "سد اکباتان", "province": "همدان", "capacity_mcm": 30, "current_percent": 45, "type": "بتنی قوسی", "river": "آبشینه", "lat": 34.78, "lon": 48.40, "year": 1335},
    {"name": "سد زاینده‌رود", "province": "چهارمحال", "capacity_mcm": 1470, "current_percent": 18, "type": "بتنی", "river": "زاینده‌رود", "lat": 32.40, "lon": 51.15, "year": 1343},
    {"name": "سد گلپایگان", "province": "اصفهان", "capacity_mcm": 135, "current_percent": 22, "type": "بتنی", "river": "گلپایگان", "lat": 33.45, "lon": 50.35, "year": 1353},
    {"name": "سد خمین", "province": "مرکزی", "capacity_mcm": 85, "current_percent": 38, "type": "خاکی", "river": "خمین", "lat": 33.64, "lon": 50.07, "year": 1352},
    {"name": "سد ۱۵ خرداد", "province": "قزوین", "capacity_mcm": 125, "current_percent": 42, "type": "خاکی", "river": "شاهرود", "lat": 36.15, "lon": 50.05, "year": 1354},
    {"name": "سد بوئین زهرا", "province": "قزوین", "capacity_mcm": 75, "current_percent": 35, "type": "خاکی", "river": "فصلی", "lat": 35.76, "lon": 50.05, "year": 1355},
    {"name": "سد شهید رجایی", "province": "مازندران", "capacity_mcm": 170, "current_percent": 55, "type": "خاکی", "river": "تلار", "lat": 36.45, "lon": 51.30, "year": 1366},
    {"name": "سد البرز", "province": "مازندران", "capacity_mcm": 55, "current_percent": 48, "type": "خاکی", "river": "چالوس", "lat": 36.55, "lon": 51.15, "year": 1353},
    {"name": "سد وشمگیر", "province": "گلستان", "capacity_mcm": 550, "current_percent": 42, "type": "خاکی", "river": "گرگان‌رود", "lat": 37.15, "lon": 55.05, "year": 1380},
    {"name": "سد گلستان", "province": "گلستان", "capacity_mcm": 95, "current_percent": 52, "type": "بتنی قوسی", "river": "گرگان‌رود", "lat": 37.25, "lon": 55.15, "year": 1343},
    {"name": "سد نساء", "province": "خراسان شمالی", "capacity_mcm": 92, "current_percent": 38, "type": "خاکی", "river": "اترک", "lat": 37.50, "lon": 57.20, "year": 1380},
    {"name": "سد پیش‌کمر", "province": "گلستان", "capacity_mcm": 65, "current_percent": 45, "type": "خاکی", "river": "پیش‌کمر", "lat": 37.05, "lon": 54.85, "year": 1382},
    {"name": "سد شیرین دره", "province": "خراسان شمالی", "capacity_mcm": 135, "current_percent": 42, "type": "خاکی", "river": "اترک", "lat": 37.40, "lon": 56.85, "year": 1385},
    {"name": "سد کهنک", "province": "خراسان جنوبی", "capacity_mcm": 62, "current_percent": 28, "type": "خاکی", "river": "فصلی", "lat": 32.95, "lon": 59.30, "year": 1380},
    {"name": "سد مصطفی‌قلی‌خان", "province": "خراسان جنوبی", "capacity_mcm": 45, "current_percent": 32, "type": "خاکی", "river": "فصلی", "lat": 32.85, "lon": 59.15, "year": 1350},
    {"name": "سد زیرتن", "province": "خراسان جنوبی", "capacity_mcm": 85, "current_percent": 35, "type": "خاکی", "river": "فصلی", "lat": 32.75, "lon": 59.40, "year": 1385},
    {"name": "سد راجی", "province": "کرمان", "capacity_mcm": 75, "current_percent": 22, "type": "خاکی", "river": "فصلی", "lat": 30.35, "lon": 57.15, "year": 1382},
    {"name": "سد جیرفت", "province": "کرمان", "capacity_mcm": 240, "current_percent": 35, "type": "بتنی", "river": "هلیل‌رود", "lat": 28.70, "lon": 57.75, "year": 1388},
    {"name": "سد صفارود", "province": "کرمان", "capacity_mcm": 115, "current_percent": 28, "type": "خاکی", "river": "صفارود", "lat": 30.50, "lon": 56.90, "year": 1385},
    {"name": "سد نرماشیر", "province": "کرمان", "capacity_mcm": 95, "current_percent": 30, "type": "خاکی", "river": "فصلی", "lat": 28.50, "lon": 59.20, "year": 1387},
    {"name": "سد کلان", "province": "هرمزگان", "capacity_mcm": 65, "current_percent": 38, "type": "خاکی", "river": "فصلی", "lat": 27.20, "lon": 56.30, "year": 1385},
    {"name": "سد استقلال", "province": "هرمزگان", "capacity_mcm": 145, "current_percent": 42, "type": "خاکی", "river": "فصلی", "lat": 27.35, "lon": 56.40, "year": 1380},
    {"name": "سد شمیل", "province": "هرمزگان", "capacity_mcm": 55, "current_percent": 35, "type": "خاکی", "river": "شمیل", "lat": 27.45, "lon": 56.50, "year": 1382},
]


# ============================================================
# حوضه‌های آبریز اصلی ایران
# ============================================================
WATER_BASINS = [
    {
        "name": "حوضه خلیج فارس و دریای عمان",
        "area_km2": 425000,
        "rivers": ["کارون", "کرخه", "دز", "زهره", "هلیل‌رود"],
        "major_dams": ["کرخه", "دز", "کارون ۳", "کارون ۴", "گتوند"],
        "avg_rainfall_mm": 350,
        "color": "#3b82f6",
        "lat": 30.5, "lon": 49.5,
    },
    {
        "name": "حوضه دریای خزر",
        "area_km2": 180000,
        "rivers": ["سفیدرود", "گرگان‌رود", "اترک", "هاراز", "چالوس"],
        "major_dams": ["سفیدرود", "ویشگیر", "البرز"],
        "avg_rainfall_mm": 750,
        "color": "#06b6d4",
        "lat": 37.0, "lon": 51.0,
    },
    {
        "name": "حوضه دریاچه ارومیه",
        "area_km2": 52000,
        "rivers": ["زرینه‌رود", "سیمینه‌رود", "تلخه‌رود"],
        "major_dams": ["بوکان", "مهاباد", "شهید کلانتری"],
        "avg_rainfall_mm": 280,
        "color": "#8b5cf6",
        "lat": 37.8, "lon": 45.8,
    },
    {
        "name": "حوضه فلات مرکزی",
        "area_km2": 385000,
        "rivers": ["زاینده‌رود", "قم‌رود", "کویر مرکزی"],
        "major_dams": ["زاینده‌رود", "امیرکبیر", "لار"],
        "avg_rainfall_mm": 150,
        "color": "#f59e0b",
        "lat": 33.5, "lon": 53.0,
    },
    {
        "name": "حوضه قره‌قوم",
        "area_km2": 110000,
        "rivers": ["هریرود", "اترک", "تجن"],
        "major_dams": ["دوستی", "نساء", "وشمگیر"],
        "avg_rainfall_mm": 220,
        "color": "#ef4444",
        "lat": 36.5, "lon": 58.0,
    },
    {
        "name": "حوضه هامون",
        "area_km2": 140000,
        "rivers": ["هیرمند", "خاش‌رود", "فرراه‌رود"],
        "major_dams": ["خاکورد", "پیشین"],
        "avg_rainfall_mm": 80,
        "color": "#dc2626",
        "lat": 31.0, "lon": 61.5,
    },
]


# ============================================================
# آبخوان‌های مهم ایران
# ============================================================
AQUIFERS = [
    {"name": "آبخوان تهران", "type": "آزاد/تحت فشار", "area_km2": 1800, "depth_m": "50-300", "status": "بحرانی", "lat": 35.68, "lon": 51.38},
    {"name": "آبخوان اصفهان-بهار", "type": "تحت فشار", "area_km2": 4200, "depth_m": "30-200", "status": "بحرانی", "lat": 32.65, "lon": 51.67},
    {"name": "آبخوان مشهد", "type": "آزاد", "area_km2": 3800, "depth_m": "20-150", "status": "بحرانی", "lat": 36.30, "lon": 59.60},
    {"name": "آبخوان کرمان", "type": "تحت فشار", "area_km2": 4500, "depth_m": "40-250", "status": "بحرانی", "lat": 30.28, "lon": 57.08},
    {"name": "آبخوان زابل", "type": "آزاد", "area_km2": 5200, "depth_m": "10-100", "status": "بحرانی", "lat": 31.03, "lon": 61.50},
    {"name": "آبخوان یزد", "type": "تحت فشار", "area_km2": 3600, "depth_m": "50-300", "status": "بحرانی", "lat": 31.90, "lon": 54.36},
    {"name": "آبخوان رفسنجان", "type": "تحت فشار", "area_km2": 3800, "depth_m": "30-200", "status": "بحرانی", "lat": 30.40, "lon": 55.99},
    {"name": "آبخوان مرودشت", "type": "آزاد", "area_km2": 3200, "depth_m": "20-150", "status": "بحرانی", "lat": 29.87, "lon": 52.80},
    {"name": "آبخوان همدان", "type": "آزاد", "area_km2": 1900, "depth_m": "20-120", "status": "بحرانی", "lat": 34.80, "lon": 48.50},
    {"name": "آبخوان بیرجند", "type": "تحت فشار", "area_km2": 3100, "depth_m": "40-200", "status": "بحرانی", "lat": 32.86, "lon": 59.23},
    {"name": "آبخوان سمنان", "type": "تحت فشار", "area_km2": 3400, "depth_m": "50-280", "status": "بحرانی", "lat": 35.58, "lon": 53.39},
    {"name": "آبخوان قم", "type": "آزاد", "area_km2": 2200, "depth_m": "20-100", "status": "بحرانی", "lat": 34.64, "lon": 50.88},
    {"name": "آبخوان اردکان", "type": "تحت فشار", "area_km2": 2400, "depth_m": "60-350", "status": "بحرانی", "lat": 32.31, "lon": 53.99},
    {"name": "آبخوان خوزستان", "type": "آزاد", "area_km2": 6500, "depth_m": "10-80", "status": "هشدار", "lat": 31.30, "lon": 48.70},
    {"name": "آبخوان گلستان", "type": "آزاد", "area_km2": 2100, "depth_m": "15-100", "status": "پایدار", "lat": 36.84, "lon": 54.44},
    {"name": "آبخوان مازندران", "type": "آزاد", "area_km2": 2400, "depth_m": "10-80", "status": "پایدار", "lat": 36.55, "lon": 53.05},
    {"name": "آبخوان گیلان", "type": "آزاد", "area_km2": 1500, "depth_m": "5-50", "status": "پایدار", "lat": 37.20, "lon": 49.60},
    {"name": "آبخوان اردبیل", "type": "آزاد", "area_km2": 1600, "depth_m": "20-120", "status": "هشدار", "lat": 38.25, "lon": 48.29},
]


# ============================================================
# اقلیم‌های ایران (کوپن-گایگر)
# ============================================================
CLIMATES = {
    "arid_cold": {
        "name_fa": "خشک سرد (BWk)",
        "description": "بیابانی با زمستان سرد",
        "provinces": ["اصفهان", "یزد", "سمنان", "قم", "خراسان جنوبی"],
        "avg_temp_c": 18,
        "avg_rain_mm": 120,
        "characteristics": ["تابستان گرم", "زمستان سرد", "بارش کم", "تبخیر بالا"],
        "color": "#f59e0b",
    },
    "arid_hot": {
        "name_fa": "خشک گرم (BWh)",
        "description": "بیابانی با تابستان بسیار گرم",
        "provinces": ["خوزستان", "بوشهر", "هرمزگان", "سیستان"],
        "avg_temp_c": 26,
        "avg_rain_mm": 150,
        "characteristics": ["تابستان بسیار گرم", "زمستان معتدل", "رطوبت بالا در جنوب"],
        "color": "#dc2626",
    },
    "semi_arid_cold": {
        "name_fa": "نیمه‌خشک سرد (BSk)",
        "description": "استپی با زمستان سرد",
        "provinces": ["تهران", "همدان", "آذربایجان", "کردستان"],
        "avg_temp_c": 14,
        "avg_rain_mm": 280,
        "characteristics": ["فصل‌های مشخص", "بارش متوسط", "زمستان سرد"],
        "color": "#eab308",
    },
    "semi_arid_hot": {
        "name_fa": "نیمه‌خشک گرم (BSh)",
        "description": "استپی با تابستان گرم",
        "provinces": ["فارس", "کرمان", "خراسان رضوی"],
        "avg_temp_c": 20,
        "avg_rain_mm": 250,
        "characteristics": ["تابستان گرم", "زمستان معتدل", "بارش فصلی"],
        "color": "#f97316",
    },
    "mediterranean": {
        "name_fa": "مدیترانه‌ای (Csa)",
        "description": "تابستان خشک و زمستان بارانی",
        "provinces": ["غرب کشور", "شمال غرب"],
        "avg_temp_c": 16,
        "avg_rain_mm": 450,
        "characteristics": ["بارش زمستانی", "تابستان خشک", "مناسب کشاورزی"],
        "color": "#84cc16",
    },
    "caspian_humid": {
        "name_fa": "مرطوب خزری (Cfb)",
        "description": "بارش زیاد در تمام فصول",
        "provinces": ["گیلان", "مازندران", "گلستان"],
        "avg_temp_c": 17,
        "avg_rain_mm": 900,
        "characteristics": ["رطوبت بالا", "بارش زیاد", "جنگل‌های هیرکانی"],
        "color": "#10b981",
    },
    "mountain_cold": {
        "name_fa": "کوهستانی سرد (Dsa/Dsb)",
        "description": "زمستان‌های بسیار سرد",
        "provinces": ["زاگرس", "البرز", "اردبیل"],
        "avg_temp_c": 10,
        "avg_rain_mm": 500,
        "characteristics": ["برف زیاد", "تابستان خنک", "منابع آبی"],
        "color": "#06b6d4",
    },
    "persian_gulf": {
        "name_fa": "گرم و مرطوب خلیج فارس",
        "description": "رطوبت بسیار بالا",
        "provinces": ["سواحل خلیج فارس"],
        "avg_temp_c": 28,
        "avg_rain_mm": 180,
        "characteristics": ["رطوبت بالا", "تابستان طولانی", "بارندگی زمستانی"],
        "color": "#0ea5e9",
    },
}


# ============================================================
# ماهواره‌های پایش خشکسالی
# ============================================================
SATELLITES = {
    "MODIS": {
        "name": "MODIS (Terra/Aqua)",
        "agency": "NASA",
        "resolution": "250m-1km",
        "revisit": "روزانه",
        "bands": ["NDVI", "EVI", "LST", "آتش‌سوزی"],
        "products": ["MOD13", "MYD13", "MOD11", "MCD12"],
        "url": "https://modis.gsfc.nasa.gov",
        "color": "#3b82f6",
    },
    "Landsat": {
        "name": "Landsat 8/9",
        "agency": "NASA/USGS",
        "resolution": "30m",
        "revisit": "16 روز",
        "bands": ["11 باند چندطیفی"],
        "products": ["NDVI", "NDWI", "NBR", "LST"],
        "url": "https://landsat.gsfc.nasa.gov",
        "color": "#10b981",
    },
    "Sentinel-2": {
        "name": "Sentinel-2 A/B",
        "agency": "ESA",
        "resolution": "10m",
        "revisit": "5 روز",
        "bands": ["13 باند"],
        "products": ["NDVI", "NDWI", "NDRE"],
        "url": "https://sentinel.esa.int",
        "color": "#8b5cf6",
    },
    "Sentinel-1": {
        "name": "Sentinel-1",
        "agency": "ESA",
        "resolution": "5-20m",
        "revisit": "6 روز",
        "bands": ["SAR (رادار)"],
        "products": ["رطوبت خاک", "سیلاب"],
        "url": "https://sentinel.esa.int",
        "color": "#ec4899",
    },
    "GPM": {
        "name": "GPM (بارش)",
        "agency": "NASA/JAXA",
        "resolution": "0.1°",
        "revisit": "30 دقیقه",
        "bands": ["میکروویو"],
        "products": ["بارش جهانی"],
        "url": "https://gpm.nasa.gov",
        "color": "#06b6d4",
    },
    "GRACE-FO": {
        "name": "GRACE-FO",
        "agency": "NASA/DLR",
        "resolution": "300km",
        "revisit": "ماهانه",
        "bands": ["گرانش‌سنج"],
        "products": ["آب زیرزمینی"],
        "url": "https://grace.jpl.nasa.gov",
        "color": "#f59e0b",
    },
    "SMAP": {
        "name": "SMAP",
        "agency": "NASA",
        "resolution": "9km",
        "revisit": "2-3 روز",
        "bands": ["میکروویو"],
        "products": ["رطوبت خاک"],
        "url": "https://smap.jpl.nasa.gov",
        "color": "#84cc16",
    },
    "TRMM": {
        "name": "TRMM/GPM",
        "agency": "NASA/JAXA",
        "resolution": "0.25°",
        "revisit": "3 ساعت",
        "bands": ["بارش گرمسیری"],
        "products": ["3B42", "IMERG"],
        "url": "https://trmm.gsfc.nasa.gov",
        "color": "#0ea5e9",
    },
    "VIIRS": {
        "name": "VIIRS",
        "agency": "NOAA/NASA",
        "resolution": "375m-750m",
        "revisit": "روزانه",
        "bands": ["22 باند"],
        "products": ["NDVI", "آتش‌سوزی", "LST"],
        "url": "https://viirsland.gsfc.nasa.gov",
        "color": "#f97316",
    },
    "CHIRPS": {
        "name": "CHIRPS",
        "agency": "UCSB/USGS",
        "resolution": "0.05°",
        "revisit": "روزانه",
        "bands": ["بارش"],
        "products": ["بارش 40 ساله"],
        "url": "https://www.chc.ucsb.edu/data/chirps",
        "color": "#14b8a6",
    },
}


# ============================================================
# مراجع بین‌المللی
# ============================================================
INTERNATIONAL_REFERENCES = [
    {"name": "WMO", "full_name": "World Meteorological Organization", "url": "https://wmo.int", "focus": "استاندارد شاخص‌های خشکسالی"},
    {"name": "NOAA NCEI", "full_name": "National Centers for Environmental Information", "url": "https://www.ncei.noaa.gov", "focus": "داده‌های اقلیمی تاریخی"},
    {"name": "NASA", "full_name": "National Aeronautics and Space Administration", "url": "https://www.nasa.gov", "focus": "داده‌های ماهواره‌ای"},
    {"name": "ESA", "full_name": "European Space Agency", "url": "https://www.esa.int", "focus": "ماهواره‌های Sentinel"},
    {"name": "FAO", "full_name": "Food and Agriculture Organization", "url": "https://www.fao.org", "focus": "امنیت غذایی و آب"},
    {"name": "IPCC", "full_name": "Intergovernmental Panel on Climate Change", "url": "https://www.ipcc.ch", "focus": "تغییر اقلیم"},
    {"name": "UNCCD", "full_name": "UN Convention to Combat Desertification", "url": "https://www.unccd.int", "focus": "مقابله با بیابان‌زایی"},
    {"name": "USDM", "full_name": "U.S. Drought Monitor", "url": "https://droughtmonitor.unl.edu", "focus": "پایش خشکسالی آمریکا"},
    {"name": "EDO", "full_name": "European Drought Observatory", "url": "https://edo.jrc.ec.europa.eu", "focus": "پایش خشکسالی اروپا"},
    {"name": "GPCP", "full_name": "Global Precipitation Climatology Project", "url": "https://gpcp.umd.edu", "focus": "بارش جهانی"},
    {"name": "GPCC", "full_name": "Global Precipitation Climatology Centre", "url": "https://gpcc.dwd.de", "focus": "داده‌های بارش DWD"},
    {"name": "Copernicus CDS", "full_name": "Copernicus Climate Data Store", "url": "https://cds.climate.copernicus.eu", "focus": "داده‌های ERA5"},
]


# ============================================================
# توابع کمکی
# ============================================================
def get_all_plains() -> List[Dict]:
    return FORBIDDEN_PLAINS


def get_all_dams() -> List[Dict]:
    return DAMS


def get_all_basins() -> List[Dict]:
    return WATER_BASINS


def get_all_aquifers() -> List[Dict]:
    return AQUIFERS


def get_all_climates() -> Dict:
    return CLIMATES


def get_all_satellites() -> Dict:
    return SATELLITES


def get_references() -> List[Dict]:
    return INTERNATIONAL_REFERENCES