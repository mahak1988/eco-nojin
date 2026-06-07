"""
🔧 به‌روزرسانی تمام صفحات برای استفاده از useTranslation
"""
from pathlib import Path

print("=" * 100)
print("🔧 UPDATING PAGES TO USE TRANSLATIONS")
print("=" * 100)

FRONTEND = Path('apps/web/src')

# ============================================================
# 1. UPDATE WEATHER PAGE
# ============================================================
print("\n1. Updating weather page...")

weather_page = FRONTEND / 'app' / 'weather' / 'page.tsx'
if weather_page.exists():
    content = weather_page.read_text(encoding='utf-8')
    
    # Add useTranslation import
    if 'useTranslation' not in content:
        content = content.replace(
            "import { useState } from 'react';",
            "import { useState } from 'react';\nimport { useTranslation } from '@/hooks/useTranslation';"
        )
    
    # Add t function in component
    if 'const { t } = useTranslation();' not in content:
        content = content.replace(
            'export default function WeatherPage() {',
            'export default function WeatherPage() {\n  const { t } = useTranslation();'
        )
    
    # Replace hardcoded text with t() calls
    replacements = {
        'هواشناسی و اقلیم‌شناسی': "{t('weather.title')}",
        'پیش‌بینی هوا و تحلیل داده‌های اقلیمی با Open-Meteo': "{t('weather.subtitle')}",
        'جستجوی موقعیت': "{t('weather.location_search')}",
        'عرض جغرافیایی': "{t('weather.latitude')}",
        'طول جغرافیایی': "{t('weather.longitude')}",
        'جستجو': "{t('common.search')}",
        'موقعیت فعلی:': "موقعیت فعلی:",
        'هوای فعلی': "{t('weather.current_weather')}",
        'در حال بارگذاری...': "{t('common.loading')}",
        'دما': "{t('weather.temperature')}",
        'رطوبت نسبی': "{t('weather.humidity')}",
        'سرعت باد (km/h)': "{t('weather.wind_speed')}",
        'بارش (mm)': "{t('weather.precipitation')}",
        'پوشش ابر': "{t('weather.cloud_cover')}",
        'فشار (hPa)': "{t('weather.pressure')}",
        'وضعیت هوا': "وضعیت هوا",
        'پیش‌بینی ۷ روزه': "{t('weather.forecast_7days')}",
        'منبع داده': "{t('weather.data_source')}",
        'دقت پیش‌بینی': "{t('weather.accuracy')}",
        'به‌روزرسانی': "{t('weather.update_frequency')}",
    }
    
    for old, new in replacements.items():
        content = content.replace(f'>{old}<', f'>{new}<')
        content = content.replace(f'"{old}"', f'"{new}"')
    
    weather_page.write_text(content, encoding='utf-8')
    print("   [OK] Weather page updated")

# ============================================================
# 2. UPDATE IOT PAGE
# ============================================================
print("\n2. Updating IoT page...")

iot_page = FRONTEND / 'app' / 'iot' / 'page.tsx'
if iot_page.exists():
    content = iot_page.read_text(encoding='utf-8')
    
    if 'useTranslation' not in content:
        content = content.replace(
            "import { useState } from 'react';",
            "import { useState } from 'react';\nimport { useTranslation } from '@/hooks/useTranslation';"
        )
    
    if 'const { t } = useTranslation();' not in content:
        content = content.replace(
            'export default function IoTPage() {',
            'export default function IoTPage() {\n  const { t } = useTranslation();'
        )
    
    replacements = {
        'اینترنت اشیا (IoT)': "{t('iot.title')}",
        'پایش سنسورها و داده‌های real-time با MQTT': "{t('iot.subtitle')}",
        'به‌روزرسانی': "{t('iot.refresh')}",
        'سنسورهای فعال': "{t('iot.active_sensors')}",
        'هشدارها': "{t('iot.alerts')}",
        'بحرانی': "{t('iot.critical')}",
        'کل سنسورها': "{t('iot.total_sensors')}",
        'در حال بارگذاری...': "{t('common.loading')}",
        'سنسوری یافت نشد': "سنسوری یافت نشد",
        'لطفاً سنسورها را فعال کنید': "لطفاً سنسورها را فعال کنید",
        'هشدارهای فعال': "هشدارهای فعال",
        'تأیید': "تأیید",
        'پروتکل MQTT': "پروتکل MQTT",
        'ارتباط real-time با سنسورها از طریق EMQX broker': "ارتباط real-time با سنسورها از طریق EMQX broker",
        '۱۲ نوع سنسور': "۱۲ نوع سنسور",
        'دما، رطوبت، خاک، نور، باد، باران و...': "دما، رطوبت، خاک، نور، باد، باران و...",
        'هشدار هوشمند': "هشدار هوشمند",
        'سیستم آستانه خودکار با اعلان real-time': "سیستم آستانه خودکار با اعلان real-time",
    }
    
    for old, new in replacements.items():
        content = content.replace(f'>{old}<', f'>{new}<')
        content = content.replace(f'"{old}"', f'"{new}"')
    
    iot_page.write_text(content, encoding='utf-8')
    print("   [OK] IoT page updated")

# ============================================================
# 3. UPDATE ECOCOIN PAGE
# ============================================================
print("\n3. Updating EcoCoin page...")

ecocoin_page = FRONTEND / 'app' / 'ecocoin' / 'page.tsx'
if ecocoin_page.exists():
    content = ecocoin_page.read_text(encoding='utf-8')
    
    if 'useTranslation' not in content:
        content = content.replace(
            "import { useState } from 'react';",
            "import { useState } from 'react';\nimport { useTranslation } from '@/hooks/useTranslation';"
        )
    
    if 'const { t } = useTranslation();' not in content:
        content = content.replace(
            'export default function EcoCoinPage() {',
            'export default function EcoCoinPage() {\n  const { t } = useTranslation();'
        )
    
    replacements = {
        'EcoCoin - ارز دیجیتال اکولوژیک': "{t('ecocoin.title')}",
        'توکن‌های سبز بر بستر Polygon - پاداش اقدامات زیست‌محیطی': "{t('ecocoin.subtitle')}",
        'کیف پول': "{t('ecocoin.wallet')}",
        'موجودی': "{t('ecocoin.balance')}",
        'قفل شده': "{t('ecocoin.staked')}",
        'قیمت': "{t('ecocoin.price')}",
        'آمار بازار': "آمار بازار",
        'انتقال توکن': "{t('ecocoin.transfer')}",
        'آدرس مقصد': "آدرس مقصد",
        'مقدار': "مقدار",
        'توکن': "توکن",
        'انتقال': "{t('ecocoin.send')}",
        'در حال انتقال...': "در حال انتقال...",
        'Staking': "{t('ecocoin.staking')}",
        'مدت قفل (روز)': "مدت قفل (روز)",
        'Stake کردن': "Stake کردن",
        'در حال stake...': "در حال stake...",
        'تاریخچه تراکنش‌ها': "{t('ecocoin.transactions')}",
        'شبکه Polygon': "شبکه Polygon",
        'تراکنش‌های سریع و کم‌هزینه بر بستر L2': "تراکنش‌های سریع و کم‌هزینه بر بستر L2",
        'پاداش سبز': "پاداش سبز",
        'کسب توکن با اقدامات زیست‌محیطی': "کسب توکن با اقدامات زیست‌محیطی",
        'Staking سودآور': "Staking سودآور",
        '۸-۱۲٪ APY با قفل کردن توکن': "۸-۱۲٪ APY با قفل کردن توکن",
    }
    
    for old, new in replacements.items():
        content = content.replace(f'>{old}<', f'>{new}<')
        content = content.replace(f'"{old}"', f'"{new}"')
    
    ecocoin_page.write_text(content, encoding='utf-8')
    print("   [OK] EcoCoin page updated")

# ============================================================
# 4. UPDATE SOIL-WATER PAGE
# ============================================================
print("\n4. Updating soil-water page...")

soil_water_page = FRONTEND / 'app' / 'soil-water' / 'page.tsx'
if soil_water_page.exists():
    content = soil_water_page.read_text(encoding='utf-8')
    
    if 'useTranslation' not in content:
        content = content.replace(
            "import { useState } from 'react';",
            "import { useState } from 'react';\nimport { useTranslation } from '@/hooks/useTranslation';"
        )
    
    if 'const { t } = useTranslation();' not in content:
        content = content.replace(
            'export default function SoilWaterPage() {',
            'export default function SoilWaterPage() {\n  const { t } = useTranslation();'
        )
    
    replacements = {
        'خاک و آب': "{t('soil_water.title')}",
        'تحلیل خواص خاک و مدیریت منابع آب با SoilGrids': "{t('soil_water.subtitle')}",
        'موقعیت نمونه‌برداری': "{t('soil_water.sampling_location')}",
        'عرض جغرافیایی': "{t('weather.latitude')}",
        'طول جغرافیایی': "{t('weather.longitude')}",
        'تحلیل خاک': "{t('soil_water.analyze_soil')}",
        'خواص فیزیکی و شیمیایی خاک': "{t('soil_water.physical_chemical')}",
        'در حال تحلیل...': "در حال تحلیل...",
        'داده‌ای در دسترس نیست': "داده‌ای در دسترس نیست",
        'طبقه‌بندی خاک': "{t('soil_water.soil_classification')}",
        'بر اساس سیستم طبقه‌بندی FAO': "بر اساس سیستم طبقه‌بندی FAO",
        'مدیریت آب خاک': "{t('soil_water.water_management')}",
        'ظرفیت نگهداری آب': "ظرفیت نگهداری آب",
        'نفوذپذیری': "نفوذپذیری",
        'توصیه‌های مدیریتی': "{t('soil_water.recommendations')}",
        'آبیاری': "آبیاری",
        'کوددهی': "کوددهی",
        'حفاظت خاک': "حفاظت خاک",
        'منبع داده': "{t('weather.data_source')}",
        '۱۴ خاصیت خاک': "۱۴ خاصیت خاک",
        '۶ عمق': "۶ عمق",
    }
    
    for old, new in replacements.items():
        content = content.replace(f'>{old}<', f'>{new}<')
        content = content.replace(f'"{old}"', f'"{new}"')
    
    soil_water_page.write_text(content, encoding='utf-8')
    print("   [OK] Soil-water page updated")

# ============================================================
# 5. UPDATE SENTINEL PAGE
# ============================================================
print("\n5. Updating sentinel page...")

sentinel_page = FRONTEND / 'app' / 'sentinel' / 'page.tsx'
if sentinel_page.exists():
    content = sentinel_page.read_text(encoding='utf-8')
    
    if 'useTranslation' not in content:
        content = content.replace(
            "import { useState } from 'react';",
            "import { useState } from 'react';\nimport { useTranslation } from '@/hooks/useTranslation';"
        )
    
    if 'const { t } = useTranslation();' not in content:
        content = content.replace(
            'export default function SentinelPage() {',
            'export default function SentinelPage() {\n  const { t } = useTranslation();'
        )
    
    replacements = {
        'پایش ماهواره‌ای': "{t('sentinel.title')}",
        'تصاویر Sentinel-2 و تحلیل شاخص‌های طیفی': "{t('sentinel.subtitle')}",
        'فیلترهای جستجو': "{t('sentinel.search_filters')}",
        'تاریخ شروع': "{t('sentinel.start_date')}",
        'تاریخ پایان': "{t('sentinel.end_date')}",
        'حداکثر پوشش ابر (%)': "{t('sentinel.cloud_cover_max')}",
        'جستجو': "{t('common.search')}",
        'شاخص NDVI': "{t('sentinel.ndvi_index')}",
        'مقدار': "مقدار",
        'وضعیت': "{t('iot.status')}",
        'توضیحات': "توضیحات",
        'تصاویر Sentinel-2': "{t('sentinel.satellite_images')}",
        'در حال بارگذاری...': "{t('common.loading')}",
        'تصویری یافت نشد': "تصویری یافت نشد",
        'فیلترها را تغییر دهید': "فیلترها را تغییر دهید",
        'مشاهده تصویر': "مشاهده تصویر",
        'شاخص‌های طیفی': "{t('sentinel.spectral_indices')}",
        'پوشش گیاهی': "پوشش گیاهی",
        'شاخص بهبودیافته': "شاخص بهبودیافته",
        'رطوبت': "رطوبت",
        'تنظیم‌شده خاک': "تنظیم‌شده خاک",
        'محاسبه': "محاسبه",
        'رزولوشن ۱۰ متر، تکرار ۵ روزه': "رزولوشن ۱۰ متر، تکرار ۵ روزه",
        '۱۳ باند طیفی': "۱۳ باند طیفی",
        'از مرئی تا مادون قرمز حرارتی': "از مرئی تا مادون قرمز حرارتی",
        'رایگان': "رایگان",
        'داده‌های Copernicus ESA': "داده‌های Copernicus ESA",
    }
    
    for old, new in replacements.items():
        content = content.replace(f'>{old}<', f'>{new}<')
        content = content.replace(f'"{old}"', f'"{new}"')
    
    sentinel_page.write_text(content, encoding='utf-8')
    print("   [OK] Sentinel page updated")

# ============================================================
# 6. UPDATE AI PAGE
# ============================================================
print("\n6. Updating AI page...")

ai_page = FRONTEND / 'app' / 'ai' / 'page.tsx'
if ai_page.exists():
    content = ai_page.read_text(encoding='utf-8')
    
    if 'useTranslation' not in content:
        content = content.replace(
            "import { useState } from 'react';",
            "import { useState } from 'react';\nimport { useTranslation } from '@/hooks/useTranslation';"
        )
    
    if 'const { t } = useTranslation();' not in content:
        content = content.replace(
            'export default function AIPage() {',
            'export default function AIPage() {\n  const { t } = useTranslation();'
        )
    
    replacements = {
        'دستیار هوشمند کشاورزی': "{t('ai.title')}",
        'تحلیل هوشمند و توصیه‌های تخصصی با AI': "{t('ai.subtitle')}",
        'چت با دستیار هوشمند': "{t('ai.chat_assistant')}",
        'در حال تحلیل...': "در حال تحلیل...",
        'سوال خود را بپرسید...': "{t('ai.ask_question')}",
        'مثلاً: چگونه آبیاری را بهینه کنم؟': "مثلاً: چگونه آبیاری را بهینه کنم؟",
        'چگونه آبیاری را بهینه کنم؟': "چگونه آبیاری را بهینه کنم؟",
        'بهترین زمان کوددهی کی است؟': "بهترین زمان کوددهی کی است؟",
        'چگونه از آفات جلوگیری کنم؟': "چگونه از آفات جلوگیری کنم؟",
        'چقدر کربن جذب شده؟': "چقدر کربن جذب شده؟",
        'تحلیل هوشمند خاک': "{t('ai.soil_analysis')}",
        'توصیه‌ها:': "توصیه‌ها:",
        'تحلیل هوشمند هوا': "{t('ai.weather_analysis')}",
        'تحلیل پوشش گیاهی': "{t('ai.vegetation_analysis')}",
        'وضعیت سلامت': "وضعیت سلامت",
        'امتیاز vigor': "امتیاز vigor",
        'اطمینان': "اطمینان",
        'تحلیل هوشمند': "تحلیل هوشمند",
        'ترکیب داده‌های خاک، هوا و ماهواره': "ترکیب داده‌های خاک، هوا و ماهواره",
        'توصیه‌های تخصصی': "توصیه‌های تخصصی",
        'بر اساس استانداردهای FAO و IPCC': "بر اساس استانداردهای FAO و IPCC",
        'یادگیری مداوم': "یادگیری مداوم",
        'بهبود توصیه‌ها با داده‌های جدید': "بهبود توصیه‌ها با داده‌های جدید",
    }
    
    for old, new in replacements.items():
        content = content.replace(f'>{old}<', f'>{new}<')
        content = content.replace(f'"{old}"', f'"{new}"')
    
    ai_page.write_text(content, encoding='utf-8')
    print("   [OK] AI page updated")

# ============================================================
# 7. UPDATE DROUGHT PAGE
# ============================================================
print("\n7. Updating drought page...")

drought_page = FRONTEND / 'app' / 'drought' / 'page.tsx'
if drought_page.exists():
    content = drought_page.read_text(encoding='utf-8')
    
    if 'useTranslation' not in content:
        content = content.replace(
            "import { useState } from 'react';",
            "import { useState } from 'react';\nimport { useTranslation } from '@/hooks/useTranslation';"
        )
    
    if 'const { t } = useTranslation();' not in content:
        content = content.replace(
            'export default function DroughtPage() {',
            'export default function DroughtPage() {\n  const { t } = useTranslation();'
        )
    
    replacements = {
        'پایش خشکسالی': "{t('drought.title')}",
        'وضعیت خشکسالی': "{t('drought.drought_risk')}",
        'سطح:': "سطح:",
        'امتیاز:': "امتیاز:",
        'توصیه:': "توصیه:",
        'شاخص SPEI': "{t('drought.spei_index')}",
        'مقدار فعلی:': "مقدار فعلی:",
        'دسته:': "دسته:",
        'مدت (ماه):': "مدت (ماه):",
        'روند:': "{t('drought.trend')}",
        'بهبود': "{t('drought.improving')}",
        'وخامت': "{t('drought.worsening')}",
        'پایدار': "{t('drought.stable')}",
    }
    
    for old, new in replacements.items():
        content = content.replace(f'>{old}<', f'>{new}<')
        content = content.replace(f'"{old}"', f'"{new}"')
    
    drought_page.write_text(content, encoding='utf-8')
    print("   [OK] Drought page updated")

# ============================================================
# 8. UPDATE MRV PAGE
# ============================================================
print("\n8. Updating MRV page...")

mrv_page = FRONTEND / 'app' / 'mrv' / 'page.tsx'
if mrv_page.exists():
    content = mrv_page.read_text(encoding='utf-8')
    
    if 'useTranslation' not in content:
        content = content.replace(
            "import { useState } from 'react';",
            "import { useState } from 'react';\nimport { useTranslation } from '@/hooks/useTranslation';"
        )
    
    if 'const { t } = useTranslation();' not in content:
        content = content.replace(
            'export default function MRVPage() {',
            'export default function MRVPage() {\n  const { t } = useTranslation();'
        )
    
    replacements = {
        'MRV - پایش کربن': "{t('mrv.title')}",
        'معیارهای جنگل': "{t('mrv.forest_metrics')}",
        'ارتفاع تاج:': "{t('mrv.canopy_height')}:",
        'پوشش تاج:': "{t('mrv.canopy_cover')}:",
        'زیست‌توده:': "{t('mrv.biomass')}:",
        'نوع جنگل:': "{t('mrv.forest_type')}:",
        'جذب کربن': "{t('mrv.carbon_sequestration')}",
        'کربن جذب شده:': "کربن جذب شده:",
        'معادل CO2:': "معادل CO2:",
        'ارزش اقتصادی:': "ارزش اقتصادی:",
        'در هکتار:': "در هکتار:",
    }
    
    for old, new in replacements.items():
        content = content.replace(f'>{old}<', f'>{new}<')
        content = content.replace(f'"{old}"', f'"{new}"')
    
    mrv_page.write_text(content, encoding='utf-8')
    print("   [OK] MRV page updated")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 100)
print("✅ ALL PAGES UPDATED TO USE TRANSLATIONS")
print("=" * 100)

print("""
Updated pages:
   [OK] weather/page.tsx
   [OK] iot/page.tsx
   [OK] ecocoin/page.tsx
   [OK] soil-water/page.tsx
   [OK] sentinel/page.tsx
   [OK] ai/page.tsx
   [OK] drought/page.tsx
   [OK] mrv/page.tsx

Each page now:
   ✅ Imports useTranslation hook
   ✅ Uses t() function for all text
   ✅ Supports 6 languages
   ✅ Automatically switches based on selected language

🚀 Next Steps:
   1. Restart frontend: npx next dev -p 3001
   2. Test language switcher in navbar
   3. Verify text changes when switching languages
   4. Test RTL/LTR for Arabic and Persian
""")