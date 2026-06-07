"""
🌍 پیاده‌سازی سیستم چندزبانه کامل
زبان‌های پشتیبانی شده: فارسی، انگلیسی، عربی، چینی، اسپانیایی، فرانسوی
"""
from pathlib import Path
import json

print("=" * 100)
print("🌍 IMPLEMENTING MULTI-LANGUAGE SYSTEM (i18n)")
print("=" * 100)

FRONTEND = Path('apps/web/src')

# ============================================================
# 1. CREATE I18N STRUCTURE
# ============================================================
print("\n1. Creating i18n structure...")

i18n_dir = FRONTEND / 'lib' / 'i18n'
i18n_dir.mkdir(parents=True, exist_ok=True)

translations_dir = i18n_dir / 'translations'
translations_dir.mkdir(parents=True, exist_ok=True)

# ============================================================
# 2. CREATE TRANSLATION FILES
# ============================================================
print("\n2. Creating translation files...")

# Persian (Farsi) - Default
fa_translations = {
    "common": {
        "home": "خانه",
        "about": "درباره ما",
        "contact": "تماس",
        "login": "ورود",
        "register": "ثبت‌نام",
        "logout": "خروج",
        "search": "جستجو",
        "save": "ذخیره",
        "cancel": "انصراف",
        "delete": "حذف",
        "edit": "ویرایش",
        "loading": "در حال بارگذاری...",
        "error": "خطا",
        "success": "موفقیت",
        "submit": "ارسال",
        "back": "بازگشت",
        "next": "بعدی",
        "previous": "قبلی"
    },
    "navbar": {
        "home": "خانه",
        "academy": "آکادمی",
        "gis": "GIS",
        "weather": "هواشناسی",
        "drought": "خشکسالی",
        "iot": "IoT",
        "ecocoin": "EcoCoin",
        "mrv": "MRV",
        "soil_water": "خاک و آب",
        "sentinel": "ماهواره",
        "ai": "هوش مصنوعی"
    },
    "weather": {
        "title": "هواشناسی و اقلیم‌شناسی",
        "subtitle": "پیش‌بینی هوا و تحلیل داده‌های اقلیمی با Open-Meteo",
        "current_weather": "هوای فعلی",
        "forecast_7days": "پیش‌بینی ۷ روزه",
        "temperature": "دما",
        "humidity": "رطوبت نسبی",
        "wind_speed": "سرعت باد",
        "precipitation": "بارش",
        "cloud_cover": "پوشش ابر",
        "pressure": "فشار",
        "location_search": "جستجوی موقعیت",
        "latitude": "عرض جغرافیایی",
        "longitude": "طول جغرافیایی",
        "data_source": "منبع داده",
        "accuracy": "دقت پیش‌بینی",
        "update_frequency": "به‌روزرسانی"
    },
    "drought": {
        "title": "پایش خشکسالی",
        "subtitle": "تحلیل شاخص‌های خشکسالی و ریسک",
        "drought_risk": "ریسک خشکسالی",
        "spei_index": "شاخص SPEI",
        "rainfall_stats": "آمار بارش",
        "severity": "شدت",
        "duration": "مدت",
        "trend": "روند",
        "improving": "بهبود",
        "worsening": "وخامت",
        "stable": "پایدار"
    },
    "iot": {
        "title": "اینترنت اشیا (IoT)",
        "subtitle": "پایش سنسورها و داده‌های real-time با MQTT",
        "active_sensors": "سنسورهای فعال",
        "alerts": "هشدارها",
        "critical": "بحرانی",
        "total_sensors": "کل سنسورها",
        "refresh": "به‌روزرسانی",
        "sensor_id": "شناسه سنسور",
        "status": "وضعیت",
        "last_update": "آخرین به‌روزرسانی"
    },
    "ecocoin": {
        "title": "EcoCoin - ارز دیجیتال اکولوژیک",
        "subtitle": "توکن‌های سبز بر بستر Polygon - پاداش اقدامات زیست‌محیطی",
        "wallet": "کیف پول",
        "balance": "موجودی",
        "staked": "قفل شده",
        "price": "قیمت",
        "market_cap": "ارزش بازار",
        "transfer": "انتقال",
        "staking": "Staking",
        "transactions": "تراکنش‌ها",
        "send": "ارسال",
        "receive": "دریافت"
    },
    "mrv": {
        "title": "MRV - پایش کربن",
        "subtitle": "اندازه‌گیری، گزارش‌دهی و تأیید جذب کربن",
        "forest_metrics": "معیارهای جنگل",
        "carbon_sequestration": "جذب کربن",
        "canopy_height": "ارتفاع تاج",
        "canopy_cover": "پوشش تاج",
        "biomass": "زیست‌توده",
        "forest_type": "نوع جنگل"
    },
    "soil_water": {
        "title": "خاک و آب",
        "subtitle": "تحلیل خواص خاک و مدیریت منابع آب با SoilGrids",
        "soil_properties": "خواص خاک",
        "physical_chemical": "خواص فیزیکی و شیمیایی",
        "soil_classification": "طبقه‌بندی خاک",
        "water_management": "مدیریت آب خاک",
        "recommendations": "توصیه‌های مدیریتی",
        "sampling_location": "موقعیت نمونه‌برداری",
        "analyze_soil": "تحلیل خاک"
    },
    "sentinel": {
        "title": "پایش ماهواره‌ای",
        "subtitle": "تصاویر Sentinel-2 و تحلیل شاخص‌های طیفی",
        "search_filters": "فیلترهای جستجو",
        "start_date": "تاریخ شروع",
        "end_date": "تاریخ پایان",
        "cloud_cover_max": "حداکثر پوشش ابر",
        "satellite_images": "تصاویر ماهواره‌ای",
        "spectral_indices": "شاخص‌های طیفی",
        "ndvi_index": "شاخص NDVI"
    },
    "ai": {
        "title": "دستیار هوشمند کشاورزی",
        "subtitle": "تحلیل هوشمند و توصیه‌های تخصصی با AI",
        "chat_assistant": "چت با دستیار هوشمند",
        "soil_analysis": "تحلیل هوشمند خاک",
        "weather_analysis": "تحلیل هوشمند هوا",
        "vegetation_analysis": "تحلیل پوشش گیاهی",
        "ask_question": "سوال خود را بپرسید",
        "quick_questions": "سوالات سریع",
        "insights": "بینش‌ها",
        "recommendations": "توصیه‌ها"
    },
    "academy": {
        "title": "آکادمی اکو نوین",
        "subtitle": "دوره‌های تخصصی رایگان با گواهینامه معتبر",
        "courses": "دوره‌ها",
        "my_courses": "دوره‌های من",
        "certificates": "گواهینامه‌ها",
        "guide": "راهنما",
        "enroll": "ثبت‌نام",
        "start_learning": "شروع یادگیری",
        "duration": "مدت",
        "lessons": "درس",
        "students": "دانشجو",
        "rating": "امتیاز"
    },
    "gis": {
        "title": "سیستم اطلاعات مکانی",
        "subtitle": "تحلیل مکانی و طیفی پیشرفته",
        "map": "نقشه",
        "layers": "لایه‌ها",
        "tools": "ابزارها",
        "measure": "اندازه‌گیری",
        "draw": "رسم",
        "export": "خروجی",
        "coordinates": "مختصات"
    }
}

# English
en_translations = {
    "common": {
        "home": "Home",
        "about": "About",
        "contact": "Contact",
        "login": "Login",
        "register": "Register",
        "logout": "Logout",
        "search": "Search",
        "save": "Save",
        "cancel": "Cancel",
        "delete": "Delete",
        "edit": "Edit",
        "loading": "Loading...",
        "error": "Error",
        "success": "Success",
        "submit": "Submit",
        "back": "Back",
        "next": "Next",
        "previous": "Previous"
    },
    "navbar": {
        "home": "Home",
        "academy": "Academy",
        "gis": "GIS",
        "weather": "Weather",
        "drought": "Drought",
        "iot": "IoT",
        "ecocoin": "EcoCoin",
        "mrv": "MRV",
        "soil_water": "Soil & Water",
        "sentinel": "Satellite",
        "ai": "AI Assistant"
    },
    "weather": {
        "title": "Weather & Climate",
        "subtitle": "Weather forecasting and climate data analysis with Open-Meteo",
        "current_weather": "Current Weather",
        "forecast_7days": "7-Day Forecast",
        "temperature": "Temperature",
        "humidity": "Humidity",
        "wind_speed": "Wind Speed",
        "precipitation": "Precipitation",
        "cloud_cover": "Cloud Cover",
        "pressure": "Pressure",
        "location_search": "Location Search",
        "latitude": "Latitude",
        "longitude": "Longitude",
        "data_source": "Data Source",
        "accuracy": "Forecast Accuracy",
        "update_frequency": "Update Frequency"
    },
    "drought": {
        "title": "Drought Monitoring",
        "subtitle": "Drought indices analysis and risk assessment",
        "drought_risk": "Drought Risk",
        "spei_index": "SPEI Index",
        "rainfall_stats": "Rainfall Statistics",
        "severity": "Severity",
        "duration": "Duration",
        "trend": "Trend",
        "improving": "Improving",
        "worsening": "Worsening",
        "stable": "Stable"
    },
    "iot": {
        "title": "Internet of Things (IoT)",
        "subtitle": "Sensor monitoring and real-time data with MQTT",
        "active_sensors": "Active Sensors",
        "alerts": "Alerts",
        "critical": "Critical",
        "total_sensors": "Total Sensors",
        "refresh": "Refresh",
        "sensor_id": "Sensor ID",
        "status": "Status",
        "last_update": "Last Update"
    },
    "ecocoin": {
        "title": "EcoCoin - Ecological Digital Currency",
        "subtitle": "Green tokens on Polygon - Rewards for environmental actions",
        "wallet": "Wallet",
        "balance": "Balance",
        "staked": "Staked",
        "price": "Price",
        "market_cap": "Market Cap",
        "transfer": "Transfer",
        "staking": "Staking",
        "transactions": "Transactions",
        "send": "Send",
        "receive": "Receive"
    },
    "mrv": {
        "title": "MRV - Carbon Monitoring",
        "subtitle": "Measurement, Reporting and Verification of carbon sequestration",
        "forest_metrics": "Forest Metrics",
        "carbon_sequestration": "Carbon Sequestration",
        "canopy_height": "Canopy Height",
        "canopy_cover": "Canopy Cover",
        "biomass": "Biomass",
        "forest_type": "Forest Type"
    },
    "soil_water": {
        "title": "Soil & Water",
        "subtitle": "Soil properties analysis and water resource management with SoilGrids",
        "soil_properties": "Soil Properties",
        "physical_chemical": "Physical & Chemical Properties",
        "soil_classification": "Soil Classification",
        "water_management": "Water Management",
        "recommendations": "Management Recommendations",
        "sampling_location": "Sampling Location",
        "analyze_soil": "Analyze Soil"
    },
    "sentinel": {
        "title": "Satellite Monitoring",
        "subtitle": "Sentinel-2 imagery and spectral indices analysis",
        "search_filters": "Search Filters",
        "start_date": "Start Date",
        "end_date": "End Date",
        "cloud_cover_max": "Max Cloud Cover",
        "satellite_images": "Satellite Images",
        "spectral_indices": "Spectral Indices",
        "ndvi_index": "NDVI Index"
    },
    "ai": {
        "title": "Smart Agriculture Assistant",
        "subtitle": "Intelligent analysis and expert recommendations with AI",
        "chat_assistant": "Chat with Smart Assistant",
        "soil_analysis": "Smart Soil Analysis",
        "weather_analysis": "Smart Weather Analysis",
        "vegetation_analysis": "Vegetation Analysis",
        "ask_question": "Ask your question",
        "quick_questions": "Quick Questions",
        "insights": "Insights",
        "recommendations": "Recommendations"
    },
    "academy": {
        "title": "Eco Novin Academy",
        "subtitle": "Free specialized courses with valid certificates",
        "courses": "Courses",
        "my_courses": "My Courses",
        "certificates": "Certificates",
        "guide": "Guide",
        "enroll": "Enroll",
        "start_learning": "Start Learning",
        "duration": "Duration",
        "lessons": "Lessons",
        "students": "Students",
        "rating": "Rating"
    },
    "gis": {
        "title": "Geographic Information System",
        "subtitle": "Advanced spatial and spectral analysis",
        "map": "Map",
        "layers": "Layers",
        "tools": "Tools",
        "measure": "Measure",
        "draw": "Draw",
        "export": "Export",
        "coordinates": "Coordinates"
    }
}

# Arabic
ar_translations = {
    "common": {
        "home": "الرئيسية",
        "about": "حول",
        "contact": "اتصل",
        "login": "تسجيل الدخول",
        "register": "تسجيل",
        "logout": "خروج",
        "search": "بحث",
        "save": "حفظ",
        "cancel": "إلغاء",
        "delete": "حذف",
        "edit": "تحرير",
        "loading": "جاري التحميل...",
        "error": "خطأ",
        "success": "نجاح",
        "submit": "إرسال",
        "back": "رجوع",
        "next": "التالي",
        "previous": "السابق"
    },
    "navbar": {
        "home": "الرئيسية",
        "academy": "الأكاديمية",
        "gis": "نظم المعلومات الجغرافية",
        "weather": "الطقس",
        "drought": "الجفاف",
        "iot": "إنترنت الأشياء",
        "ecocoin": "EcoCoin",
        "mrv": "MRV",
        "soil_water": "التربة والمياه",
        "sentinel": "القمر الصناعي",
        "ai": "الذكاء الاصطناعي"
    },
    "weather": {
        "title": "الطقس والمناخ",
        "subtitle": "توقعات الطقس وتحليل بيانات المناخ",
        "current_weather": "الطقس الحالي",
        "forecast_7days": "توقعات 7 أيام",
        "temperature": "درجة الحرارة",
        "humidity": "الرطوبة",
        "wind_speed": "سرعة الرياح",
        "precipitation": "هطول الأمطار",
        "cloud_cover": "الغطاء السحابي",
        "pressure": "الضغط",
        "location_search": "البحث عن الموقع",
        "latitude": "خط العرض",
        "longitude": "خط الطول"
    }
}

# Chinese
zh_translations = {
    "common": {
        "home": "首页",
        "about": "关于",
        "contact": "联系",
        "login": "登录",
        "register": "注册",
        "logout": "退出",
        "search": "搜索",
        "save": "保存",
        "cancel": "取消",
        "delete": "删除",
        "edit": "编辑",
        "loading": "加载中...",
        "error": "错误",
        "success": "成功",
        "submit": "提交",
        "back": "返回",
        "next": "下一步",
        "previous": "上一步"
    },
    "navbar": {
        "home": "首页",
        "academy": "学院",
        "gis": "地理信息系统",
        "weather": "天气",
        "drought": "干旱",
        "iot": "物联网",
        "ecocoin": "EcoCoin",
        "mrv": "MRV",
        "soil_water": "土壤与水",
        "sentinel": "卫星",
        "ai": "AI助手"
    },
    "weather": {
        "title": "天气与气候",
        "subtitle": "天气预报和气候数据分析",
        "current_weather": "当前天气",
        "forecast_7days": "7天预报",
        "temperature": "温度",
        "humidity": "湿度",
        "wind_speed": "风速",
        "precipitation": "降水量",
        "cloud_cover": "云量",
        "pressure": "气压"
    }
}

# Spanish
es_translations = {
    "common": {
        "home": "Inicio",
        "about": "Acerca de",
        "contact": "Contacto",
        "login": "Iniciar sesión",
        "register": "Registrarse",
        "logout": "Cerrar sesión",
        "search": "Buscar",
        "save": "Guardar",
        "cancel": "Cancelar",
        "delete": "Eliminar",
        "edit": "Editar",
        "loading": "Cargando...",
        "error": "Error",
        "success": "Éxito",
        "submit": "Enviar",
        "back": "Atrás",
        "next": "Siguiente",
        "previous": "Anterior"
    },
    "navbar": {
        "home": "Inicio",
        "academy": "Academia",
        "gis": "SIG",
        "weather": "Clima",
        "drought": "Sequía",
        "iot": "IoT",
        "ecocoin": "EcoCoin",
        "mrv": "MRV",
        "soil_water": "Suelo y Agua",
        "sentinel": "Satélite",
        "ai": "Asistente IA"
    },
    "weather": {
        "title": "Clima y Clima",
        "subtitle": "Pronóstico del tiempo y análisis de datos climáticos",
        "current_weather": "Clima Actual",
        "forecast_7days": "Pronóstico de 7 Días",
        "temperature": "Temperatura",
        "humidity": "Humedad",
        "wind_speed": "Velocidad del Viento",
        "precipitation": "Precipitación",
        "cloud_cover": "Cobertura Nubosa",
        "pressure": "Presión"
    }
}

# French
fr_translations = {
    "common": {
        "home": "Accueil",
        "about": "À propos",
        "contact": "Contact",
        "login": "Connexion",
        "register": "S'inscrire",
        "logout": "Déconnexion",
        "search": "Rechercher",
        "save": "Enregistrer",
        "cancel": "Annuler",
        "delete": "Supprimer",
        "edit": "Modifier",
        "loading": "Chargement...",
        "error": "Erreur",
        "success": "Succès",
        "submit": "Soumettre",
        "back": "Retour",
        "next": "Suivant",
        "previous": "Précédent"
    },
    "navbar": {
        "home": "Accueil",
        "academy": "Académie",
        "gis": "SIG",
        "weather": "Météo",
        "drought": "Sécheresse",
        "iot": "IoT",
        "ecocoin": "EcoCoin",
        "mrv": "MRV",
        "soil_water": "Sol et Eau",
        "sentinel": "Satellite",
        "ai": "Assistant IA"
    },
    "weather": {
        "title": "Météo et Climat",
        "subtitle": "Prévisions météorologiques et analyse des données climatiques",
        "current_weather": "Météo Actuelle",
        "forecast_7days": "Prévisions 7 Jours",
        "temperature": "Température",
        "humidity": "Humidité",
        "wind_speed": "Vitesse du Vent",
        "precipitation": "Précipitations",
        "cloud_cover": "Couverture Nuageuse",
        "pressure": "Pression"
    }
}

# Save all translation files
translations = {
    'fa': fa_translations,
    'en': en_translations,
    'ar': ar_translations,
    'zh': zh_translations,
    'es': es_translations,
    'fr': fr_translations
}

for lang_code, translations_data in translations.items():
    file_path = translations_dir / f'{lang_code}.json'
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(translations_data, f, ensure_ascii=False, indent=2)
    print(f"   [OK] Created {lang_code}.json")

# ============================================================
# 3. CREATE I18N CONFIG
# ============================================================
print("\n3. Creating i18n config...")

i18n_config = '''// i18n configuration
export const languages = {
  fa: { name: 'فارسی', dir: 'rtl', flag: '🇮🇷' },
  en: { name: 'English', dir: 'ltr', flag: '🇺🇸' },
  ar: { name: 'العربية', dir: 'rtl', flag: '🇸🇦' },
  zh: { name: '中文', dir: 'ltr', flag: '🇨🇳' },
  es: { name: 'Español', dir: 'ltr', flag: '🇪🇸' },
  fr: { name: 'Français', dir: 'ltr', flag: '🇫🇷' }
};

export const defaultLanguage = 'fa';

export type Language = keyof typeof languages;
'''

(i18n_dir / 'config.ts').write_text(i18n_config, encoding='utf-8')
print("   [OK] Created config.ts")

# ============================================================
# 4. CREATE LANGUAGE CONTEXT
# ============================================================
print("\n4. Creating language context...")

contexts_dir = FRONTEND / 'contexts'
contexts_dir.mkdir(parents=True, exist_ok=True)

language_context = '''"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Language, languages, defaultLanguage } from '@/lib/i18n/config';
import faTranslations from '@/lib/i18n/translations/fa.json';
import enTranslations from '@/lib/i18n/translations/en.json';
import arTranslations from '@/lib/i18n/translations/ar.json';
import zhTranslations from '@/lib/i18n/translations/zh.json';
import esTranslations from '@/lib/i18n/translations/es.json';
import frTranslations from '@/lib/i18n/translations/fr.json';

const allTranslations = {
  fa: faTranslations,
  en: enTranslations,
  ar: arTranslations,
  zh: zhTranslations,
  es: esTranslations,
  fr: frTranslations
};

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
  dir: 'ltr' | 'rtl';
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<Language>(defaultLanguage);

  useEffect(() => {
    const saved = localStorage.getItem('language') as Language;
    if (saved && languages[saved]) {
      setLanguageState(saved);
    }
  }, []);

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('language', lang);
    document.documentElement.dir = languages[lang].dir;
    document.documentElement.lang = lang;
  };

  const t = (key: string): string => {
    const keys = key.split('.');
    let value: any = allTranslations[language];
    
    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        // Fallback to English
        value = allTranslations.en;
        for (const fk of keys) {
          if (value && typeof value === 'object' && fk in value) {
            value = value[fk];
          } else {
            return key;
          }
        }
        break;
      }
    }
    
    return typeof value === 'string' ? value : key;
  };

  const dir = languages[language].dir;

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t, dir }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within LanguageProvider');
  }
  return context;
}
'''

(contexts_dir / 'LanguageContext.tsx').write_text(language_context, encoding='utf-8')
print("   [OK] Created LanguageContext.tsx")

# ============================================================
# 5. CREATE USE TRANSLATION HOOK
# ============================================================
print("\n5. Creating useTranslation hook...")

hooks_dir = FRONTEND / 'hooks'
use_translation_hook = '''import { useLanguage } from '@/contexts/LanguageContext';

export function useTranslation() {
  const { t, language, dir } = useLanguage();
  return { t, language, dir };
}
'''

(hooks_dir / 'useTranslation.ts').write_text(use_translation_hook, encoding='utf-8')
print("   [OK] Created useTranslation.ts")

# ============================================================
# 6. CREATE LANGUAGE SWITCHER COMPONENT
# ============================================================
print("\n6. Creating LanguageSwitcher component...")

components_dir = FRONTEND / 'components' / 'ui'
components_dir.mkdir(parents=True, exist_ok=True)

language_switcher = '''"use client";

import { useState } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { languages, Language } from '@/lib/i18n/config';
import { Globe } from 'lucide-react';

export function LanguageSwitcher() {
  const { language, setLanguage } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 text-sm text-slate-300 hover:text-emerald-400 hover:bg-slate-800/50 rounded-lg transition-colors"
      >
        <Globe className="w-4 h-4" />
        <span>{languages[language].flag}</span>
        <span className="hidden md:inline">{languages[language].name}</span>
      </button>

      {isOpen && (
        <>
          <div 
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-48 bg-slate-900 border border-slate-700 rounded-lg shadow-xl z-50 overflow-hidden">
            {Object.entries(languages).map(([code, lang]) => (
              <button
                key={code}
                onClick={() => {
                  setLanguage(code as Language);
                  setIsOpen(false);
                }}
                className={`w-full px-4 py-3 text-left flex items-center gap-3 hover:bg-slate-800 transition-colors ${
                  language === code ? 'bg-slate-800 text-emerald-400' : 'text-slate-300'
                }`}
              >
                <span className="text-xl">{lang.flag}</span>
                <span className="flex-1">{lang.name}</span>
                {language === code && (
                  <span className="text-emerald-400">✓</span>
                )}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
'''

(components_dir / 'LanguageSwitcher.tsx').write_text(language_switcher, encoding='utf-8')
print("   [OK] Created LanguageSwitcher.tsx")

# ============================================================
# 7. UPDATE PROVIDERS
# ============================================================
print("\n7. Updating providers...")

providers_path = FRONTEND / 'app' / 'providers.tsx'
if providers_path.exists():
    content = providers_path.read_text(encoding='utf-8')
    
    # Add LanguageProvider import
    if 'LanguageProvider' not in content:
        content = content.replace(
            "import { QueryClient, QueryClientProvider } from '@tanstack/react-query';",
            "import { QueryClient, QueryClientProvider } from '@tanstack/react-query';\nimport { LanguageProvider } from '@/contexts/LanguageContext';"
        )
        
        # Wrap children with LanguageProvider
        content = content.replace(
            '<QueryClientProvider client={queryClient}>',
            '<LanguageProvider>\n        <QueryClientProvider client={queryClient}>'
        )
        content = content.replace(
            '</QueryClientProvider>',
            '</QueryClientProvider>\n      </LanguageProvider>'
        )
        
        providers_path.write_text(content, encoding='utf-8')
        print("   [OK] Updated providers.tsx")

# ============================================================
# 8. UPDATE NAVBAR
# ============================================================
print("\n8. Updating Navbar with LanguageSwitcher...")

navbar_path = FRONTEND / 'app' / 'Navbar.tsx'
if navbar_path.exists():
    content = navbar_path.read_text(encoding='utf-8')
    
    # Add LanguageSwitcher import
    if 'LanguageSwitcher' not in content:
        content = content.replace(
            "import {",
            "import { LanguageSwitcher } from '@/components/ui/LanguageSwitcher';\nimport {"
        )
        
        # Add LanguageSwitcher to navbar
        if '<button' in content and 'lg:hidden' in content:
            content = content.replace(
                '{/* Mobile Menu Button */}',
                '<LanguageSwitcher />\n          {/* Mobile Menu Button */}'
            )
        
        navbar_path.write_text(content, encoding='utf-8')
        print("   [OK] Updated Navbar.tsx")

# ============================================================
# 9. UPDATE LAYOUT
# ============================================================
print("\n9. Updating layout for RTL/LTR...")

layout_path = FRONTEND / 'app' / 'layout.tsx'
if layout_path.exists():
    content = layout_path.read_text(encoding='utf-8')
    
    # Add dir and lang attributes dynamically
    if 'document.documentElement.dir' not in content:
        # Add script to set dir on load
        script = '''
      <script
        dangerouslySetInnerHTML={{
          __html: `
            const lang = localStorage.getItem('language') || 'fa';
            const dirs = { fa: 'rtl', en: 'ltr', ar: 'rtl', zh: 'ltr', es: 'ltr', fr: 'ltr' };
            document.documentElement.dir = dirs[lang] || 'rtl';
            document.documentElement.lang = lang;
          `
        }}
      />'''
        
        if '</head>' in content:
            content = content.replace('</head>', f'{script}\n    </head>')
            layout_path.write_text(content, encoding='utf-8')
            print("   [OK] Updated layout.tsx")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 100)
print("✅ MULTI-LANGUAGE SYSTEM IMPLEMENTED")
print("=" * 100)

print("""
🌍 Supported Languages:
   🇮🇷 Persian (فارسی) - RTL - Default
   🇺🇸 English - LTR
   🇸🇦 Arabic (العربية) - RTL
   🇨🇳 Chinese (中文) - LTR
   🇪🇸 Spanish (Español) - LTR
   🇫🇷 French (Français) - LTR

📁 Files Created:
   ✅ lib/i18n/config.ts
   ✅ lib/i18n/translations/fa.json
   ✅ lib/i18n/translations/en.json
   ✅ lib/i18n/translations/ar.json
   ✅ lib/i18n/translations/zh.json
   ✅ lib/i18n/translations/es.json
   ✅ lib/i18n/translations/fr.json
   ✅ contexts/LanguageContext.tsx
   ✅ hooks/useTranslation.ts
   ✅ components/ui/LanguageSwitcher.tsx

🔧 Files Updated:
   ✅ app/providers.tsx
   ✅ app/Navbar.tsx
   ✅ app/layout.tsx

🎯 How to Use:

1. In any component:
   import { useTranslation } from '@/hooks/useTranslation';
   
   const { t } = useTranslation();
   <h1>{t('weather.title')}</h1>

2. Language switcher is in navbar
3. Language preference is saved in localStorage
4. RTL/LTR is automatically handled

🚀 Next Steps:
   1. Restart frontend: npx next dev -p 3001
   2. Test language switcher
   3. Update page components to use translations
""")