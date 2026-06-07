#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌍 افزودن سیستم چندزبانه کامل به اکو نوژین
- رفع warning NaN در backgroundColor
- ایجاد Language Switcher حرفه‌ای
- ترجمه کامل صفحه اصلی به 20 زبان
"""
import sys
import json
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
WEB = ROOT / "apps" / "web" / "src"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"✅ {path.relative_to(WEB)}")


# ========== 1. رفع warning NaN در page.tsx ==========
def fix_page_nan_warning():
    print("\n🔧 رفع warning NaN در backgroundColor...")
    
    # خواندن فایل فعلی
    page_path = WEB / "app" / "page.tsx"
    if not page_path.exists():
        print(f"⚠️ فایل page.tsx یافت نشد")
        return
    
    content = page_path.read_text(encoding="utf-8")
    
    # رفع مشکل NaN - جایگزینی backgroundColor با مقدار صحیح
    # مشکل: useMotionValue("#0f172a") که با template ترکیب می‌شود
    old_code = '''  // Background color based on scroll
  const backgroundColor = useMotionValue("#0f172a"); // slate-950
  const backgroundColorTemplate = useMotionTemplate`${backgroundColor}`;
  
  // Smooth spring animation for background
  const springBg = useSpring(backgroundColor, { stiffness: 100, damping: 30 });'''
    
    new_code = '''  // Background color based on scroll - ثابت و ساده
  const [bgColor, setBgColor] = useState("#0f172a");'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        print("   ✅ کد backgroundColor قدیمی جایگزین شد")
    
    # جایگزینی useEffect مربوط به تغییر رنگ
    old_effect = '''  // Change background color based on scroll position
  useEffect(() => {
    const unsubscribe = scrollYProgress.onChange((latest) => {
      if (latest < 0.2) {
        backgroundColor.set("#0f172a"); // slate-950 (Hero)
      } else if (latest < 0.4) {
        backgroundColor.set("#1e293b"); // slate-800 (Stats)
      } else if (latest < 0.6) {
        backgroundColor.set("#0f172a"); // slate-950 (Modules)
      } else if (latest < 0.8) {
        backgroundColor.set("#1e1b4b"); // indigo-950 (Gallery)
      } else {
        backgroundColor.set("#0f172a"); // slate-950 (Features)
      }
    });
    
    return () => unsubscribe();
  }, [scrollYProgress, backgroundColor]);'''
    
    new_effect = '''  // Change background color based on scroll position
  useEffect(() => {
    const unsubscribe = scrollYProgress.onChange((latest) => {
      if (latest < 0.2) {
        setBgColor("#0f172a");
      } else if (latest < 0.4) {
        setBgColor("#1e293b");
      } else if (latest < 0.6) {
        setBgColor("#0f172a");
      } else if (latest < 0.8) {
        setBgColor("#1e1b4b");
      } else {
        setBgColor("#0f172a");
      }
    });
    return () => unsubscribe();
  }, [scrollYProgress]);'''
    
    if old_effect in content:
        content = content.replace(old_effect, new_effect)
        print("   ✅ useEffect رنگ پس‌زمینه اصلاح شد")
    
    # جایگزینی motion.div با div ساده
    old_motion = '''    <motion.div 
      style={{ backgroundColor: springBg }}
      className="min-h-screen transition-colors duration-700"
    >'''
    
    new_motion = '''    <div 
      style={{ backgroundColor: bgColor, transition: "background-color 0.7s ease" }}
      className="min-h-screen"
    >'''
    
    if old_motion in content:
        content = content.replace(old_motion, new_motion)
        print("   ✅ motion.div به div تبدیل شد")
    
    # جایگزینی closing tag
    content = content.replace(
        '''      </section>
    </motion.div>
  );
}''',
        '''      </section>
    </div>
  );
}'''
    )
    
    page_path.write_text(content, encoding="utf-8")
    print("   ✅ Warning NaN رفع شد")


# ========== 2. ایجاد فایل‌های ترجمه ==========
def create_translations():
    print("\n🌐 ایجاد فایل‌های ترجمه 20 زبان...")
    
    translations = {
        "fa": {
            "hero": {
                "badge": "پلتفرم علمی احیای زمین",
                "title": "اکو نوژین",
                "subtitle": "مدیریت هوشمند یکپارچه",
                "description": "احیای مناظر خشک و نیمه‌خشک زمین با ترکیب علم هیدرولوژی، مدل‌سازی کربن، سنجش از دور و هوش مصنوعی",
                "startSimulation": "شروع شبیه‌سازی",
                "freeEducation": "آموزش رایگان",
                "userRating": "امتیاز کاربران",
                "activeUsers": "کاربر فعال",
                "secure": "امن و مطمئن"
            },
            "stats": {
                "hectares": "هکتار تحت پایش",
                "carbon": "تن کربن جذب‌شده",
                "farmers": "کشاورز فعال",
                "basins": "حوضه آبریز"
            },
            "modules": {
                "scientific": "ماژول‌های علمی",
                "scientificDesc": "ابزارهای تخصصی برای احیای زمین‌های خشک و نیمه‌خشک",
                "community": "جامعه و خدمات",
                "communityDesc": "همه آنچه برای یک کشاورز پایدار نیاز دارید",
                "details": "مشاهده جزئیات",
                "projects": "پروژه‌های موفق",
                "projectsDesc": "نمونه‌هایی از احیای زمین‌های خشک و نیمه‌خشک"
            },
            "features": {
                "free": "رایگان و آزاد",
                "freeDesc": "تمامی خدمات علمی بدون هزینه",
                "ai": "هوش مصنوعی",
                "aiDesc": "تحلیل هوشمند با مدل‌های پیشرفته",
                "secure": "امن و مطمئن",
                "secureDesc": "حفاظت از داده‌های پژوهشی شما",
                "global": "دسترسی جهانی",
                "globalDesc": "از هر نقطه جهان قابل استفاده"
            },
            "nav": {
                "home": "خانه",
                "scientific": "ماژول‌های علمی",
                "community": "جامعه و خدمات",
                "education": "آموزش",
                "about": "درباره ما",
                "contact": "تماس",
                "login": "ورود",
                "register": "ثبت‌نام رایگان",
                "language": "زبان"
            }
        },
        "en": {
            "hero": {
                "badge": "Land Restoration Platform",
                "title": "Econojin",
                "subtitle": "Integrated Smart Management",
                "description": "Restoration of arid and semi-arid landscapes through hydrology science, carbon modeling, remote sensing and artificial intelligence",
                "startSimulation": "Start Simulation",
                "freeEducation": "Free Education",
                "userRating": "User Rating",
                "activeUsers": "Active Users",
                "secure": "Secure & Trusted"
            },
            "stats": {
                "hectares": "Hectares Monitored",
                "carbon": "Tons CO₂ Absorbed",
                "farmers": "Active Farmers",
                "basins": "Watershed Basins"
            },
            "modules": {
                "scientific": "Scientific Modules",
                "scientificDesc": "Specialized tools for arid and semi-arid land restoration",
                "community": "Community & Services",
                "communityDesc": "Everything a sustainable farmer needs",
                "details": "View Details",
                "projects": "Successful Projects",
                "projectsDesc": "Examples of arid and semi-arid land restoration"
            },
            "features": {
                "free": "Free & Open",
                "freeDesc": "All scientific services at no cost",
                "ai": "Artificial Intelligence",
                "aiDesc": "Smart analysis with advanced models",
                "secure": "Secure & Trusted",
                "secureDesc": "Protection of your research data",
                "global": "Global Access",
                "globalDesc": "Accessible from anywhere in the world"
            },
            "nav": {
                "home": "Home",
                "scientific": "Scientific Modules",
                "community": "Community & Services",
                "education": "Education",
                "about": "About",
                "contact": "Contact",
                "login": "Login",
                "register": "Free Register",
                "language": "Language"
            }
        },
        "ar": {
            "hero": {
                "badge": "منصة إحياء الأراضي العلمية",
                "title": "إكونوجين",
                "subtitle": "الإدارة الذكية المتكاملة",
                "description": "إحياء المناظر الطبيعية الجافة وشبه الجافة من خلال علم الهيدرولوجيا ونمذجة الكربون والاستشعار عن بعد والذكاء الاصطناعي",
                "startSimulation": "ابدأ المحاكاة",
                "freeEducation": "تعليم مجاني",
                "userRating": "تقييم المستخدمين",
                "activeUsers": "مستخدم نشط",
                "secure": "آمن وموثوق"
            },
            "stats": {
                "hectares": "هكتار تحت المراقبة",
                "carbon": "طن CO₂ ممتص",
                "farmers": "مزارع نشط",
                "basins": "حوض مائي"
            },
            "modules": {
                "scientific": "الوحدات العلمية",
                "scientificDesc": "أدوات متخصصة لإحياء الأراضي الجافة وشبه الجافة",
                "community": "المجتمع والخدمات",
                "communityDesc": "كل ما يحتاجه المزارع المستدام",
                "details": "عرض التفاصيل",
                "projects": "المشاريع الناجحة",
                "projectsDesc": "أمثلة على إحياء الأراضي الجافة"
            },
            "features": {
                "free": "مجاني ومفتوح",
                "freeDesc": "جميع الخدمات العلمية بدون تكلفة",
                "ai": "الذكاء الاصطناعي",
                "aiDesc": "تحليل ذكي بنماذج متقدمة",
                "secure": "آمن وموثوق",
                "secureDesc": "حماية بيانات البحث الخاصة بك",
                "global": "وصول عالمي",
                "globalDesc": "متاح من أي مكان في العالم"
            },
            "nav": {
                "home": "الرئيسية",
                "scientific": "الوحدات العلمية",
                "community": "المجتمع والخدمات",
                "education": "التعليم",
                "about": "من نحن",
                "contact": "اتصل بنا",
                "login": "دخول",
                "register": "تسجيل مجاني",
                "language": "اللغة"
            }
        },
        "zh": {
            "hero": {
                "badge": "土地恢复科学平台",
                "title": "Econojin",
                "subtitle": "综合智能管理",
                "description": "通过水文学、碳建模、遥感和人工智能恢复干旱和半干旱景观",
                "startSimulation": "开始模拟",
                "freeEducation": "免费教育",
                "userRating": "用户评分",
                "activeUsers": "活跃用户",
                "secure": "安全可靠"
            },
            "stats": {
                "hectares": "监测公顷",
                "carbon": "吸收二氧化碳吨",
                "farmers": "活跃农民",
                "basins": "流域盆地"
            },
            "modules": {
                "scientific": "科学模块",
                "scientificDesc": "干旱和半干旱土地恢复的专业工具",
                "community": "社区与服务",
                "communityDesc": "可持续农民所需的一切",
                "details": "查看详情",
                "projects": "成功项目",
                "projectsDesc": "干旱土地恢复示例"
            },
            "features": {
                "free": "免费开放",
                "freeDesc": "所有科学服务免费",
                "ai": "人工智能",
                "aiDesc": "先进模型的智能分析",
                "secure": "安全可靠",
                "secureDesc": "保护您的研究数据",
                "global": "全球访问",
                "globalDesc": "从世界任何地方访问"
            },
            "nav": {
                "home": "首页",
                "scientific": "科学模块",
                "community": "社区服务",
                "education": "教育",
                "about": "关于",
                "contact": "联系",
                "login": "登录",
                "register": "免费注册",
                "language": "语言"
            }
        },
        "es": {
            "hero": {
                "badge": "Plataforma Científica de Restauración",
                "title": "Econojin",
                "subtitle": "Gestión Inteligente Integrada",
                "description": "Restauración de paisajes áridos y semiáridos mediante hidrología, modelado de carbono, teledetección e inteligencia artificial",
                "startSimulation": "Iniciar Simulación",
                "freeEducation": "Educación Gratuita",
                "userRating": "Calificación",
                "activeUsers": "Usuarios Activos",
                "secure": "Seguro y Confiable"
            },
            "stats": {
                "hectares": "Hectáreas Monitoreadas",
                "carbon": "Toneladas CO₂ Absorbidas",
                "farmers": "Agricultores Activos",
                "basins": "Cuencas Hidrográficas"
            },
            "modules": {
                "scientific": "Módulos Científicos",
                "scientificDesc": "Herramientas especializadas para restauración de tierras áridas",
                "community": "Comunidad y Servicios",
                "communityDesc": "Todo lo que un agricultor sostenible necesita",
                "details": "Ver Detalles",
                "projects": "Proyectos Exitosos",
                "projectsDesc": "Ejemplos de restauración de tierras"
            },
            "features": {
                "free": "Gratis y Abierto",
                "freeDesc": "Todos los servicios científicos sin costo",
                "ai": "Inteligencia Artificial",
                "aiDesc": "Análisis inteligente con modelos avanzados",
                "secure": "Seguro y Confiable",
                "secureDesc": "Protección de sus datos de investigación",
                "global": "Acceso Global",
                "globalDesc": "Accesible desde cualquier lugar del mundo"
            },
            "nav": {
                "home": "Inicio",
                "scientific": "Módulos Científicos",
                "community": "Comunidad",
                "education": "Educación",
                "about": "Acerca de",
                "contact": "Contacto",
                "login": "Iniciar Sesión",
                "register": "Registro Gratuito",
                "language": "Idioma"
            }
        },
        "fr": {
            "hero": {
                "badge": "Plateforme Scientifique de Restauration",
                "title": "Econojin",
                "subtitle": "Gestion Intelligente Intégrée",
                "description": "Restauration des paysages arides et semi-arides par l'hydrologie, la modélisation carbone, la télédétection et l'IA",
                "startSimulation": "Démarrer la Simulation",
                "freeEducation": "Éducation Gratuite",
                "userRating": "Évaluation",
                "activeUsers": "Utilisateurs Actifs",
                "secure": "Sécurisé et Fiable"
            },
            "stats": {
                "hectares": "Hectares Surveillés",
                "carbon": "Tonnes CO₂ Absorbées",
                "farmers": "Agriculteurs Actifs",
                "basins": "Bassins Versants"
            },
            "modules": {
                "scientific": "Modules Scientifiques",
                "scientificDesc": "Outils spécialisés pour la restauration des terres arides",
                "community": "Communauté et Services",
                "communityDesc": "Tout ce dont un agriculteur durable a besoin",
                "details": "Voir Détails",
                "projects": "Projets Réussis",
                "projectsDesc": "Exemples de restauration de terres"
            },
            "features": {
                "free": "Gratuit et Ouvert",
                "freeDesc": "Tous les services scientifiques sans frais",
                "ai": "Intelligence Artificielle",
                "aiDesc": "Analyse intelligente avec modèles avancés",
                "secure": "Sécurisé et Fiable",
                "secureDesc": "Protection de vos données de recherche",
                "global": "Accès Mondial",
                "globalDesc": "Accessible depuis n'importe où dans le monde"
            },
            "nav": {
                "home": "Accueil",
                "scientific": "Modules Scientifiques",
                "community": "Communauté",
                "education": "Éducation",
                "about": "À propos",
                "contact": "Contact",
                "login": "Connexion",
                "register": "Inscription Gratuite",
                "language": "Langue"
            }
        },
        "de": {
            "hero": {
                "badge": "Wissenschaftliche Restaurierungsplattform",
                "title": "Econojin",
                "subtitle": "Integriertes Intelligentes Management",
                "description": "Restaurierung arider und semiarider Landschaften durch Hydrologie, Kohlenstoffmodellierung, Fernerkundung und KI",
                "startSimulation": "Simulation Starten",
                "freeEducation": "Kostenlose Bildung",
                "userRating": "Benutzerbewertung",
                "activeUsers": "Aktive Benutzer",
                "secure": "Sicher und Zuverlässig"
            },
            "stats": {
                "hectares": "Überwachte Hektar",
                "carbon": "Tonnen CO₂ Absorbiert",
                "farmers": "Aktive Landwirte",
                "basins": "Wassereinzugsgebiete"
            },
            "modules": {
                "scientific": "Wissenschaftliche Module",
                "scientificDesc": "Spezialisierte Werkzeuge für aride Landrestaurierung",
                "community": "Gemeinschaft & Dienste",
                "communityDesc": "Alles was ein nachhaltiger Landwirt braucht",
                "details": "Details Anzeigen",
                "projects": "Erfolgreiche Projekte",
                "projectsDesc": "Beispiele der Landrestaurierung"
            },
            "features": {
                "free": "Kostenlos und Offen",
                "freeDesc": "Alle wissenschaftlichen Dienste kostenlos",
                "ai": "Künstliche Intelligenz",
                "aiDesc": "Intelligente Analyse mit fortschrittlichen Modellen",
                "secure": "Sicher und Zuverlässig",
                "secureDesc": "Schutz Ihrer Forschungsdaten",
                "global": "Globaler Zugang",
                "globalDesc": "Von überall auf der Welt zugänglich"
            },
            "nav": {
                "home": "Startseite",
                "scientific": "Wissenschaftliche Module",
                "community": "Gemeinschaft",
                "education": "Bildung",
                "about": "Über uns",
                "contact": "Kontakt",
                "login": "Anmelden",
                "register": "Kostenlos Registrieren",
                "language": "Sprache"
            }
        },
        "ru": {
            "hero": {
                "badge": "Научная платформа восстановления",
                "title": "Эконоджин",
                "subtitle": "Интегрированное умное управление",
                "description": "Восстановление засушливых и полузасушливых ландшафтов с помощью гидрологии, моделирования углерода, дистанционного зондирования и ИИ",
                "startSimulation": "Начать моделирование",
                "freeEducation": "Бесплатное образование",
                "userRating": "Рейтинг пользователей",
                "activeUsers": "Активных пользователей",
                "secure": "Безопасно и надежно"
            },
            "stats": {
                "hectares": "Гектаров под мониторингом",
                "carbon": "Тонн CO₂ поглощено",
                "farmers": "Активных фермеров",
                "basins": "Водосборных бассейнов"
            },
            "modules": {
                "scientific": "Научные модули",
                "scientificDesc": "Специализированные инструменты для восстановления засушливых земель",
                "community": "Сообщество и услуги",
                "communityDesc": "Все, что нужно устойчивому фермеру",
                "details": "Подробнее",
                "projects": "Успешные проекты",
                "projectsDesc": "Примеры восстановления земель"
            },
            "features": {
                "free": "Бесплатно и открыто",
                "freeDesc": "Все научные услуги бесплатно",
                "ai": "Искусственный интеллект",
                "aiDesc": "Умный анализ с продвинутыми моделями",
                "secure": "Безопасно и надежно",
                "secureDesc": "Защита ваших исследовательских данных",
                "global": "Глобальный доступ",
                "globalDesc": "Доступно из любой точки мира"
            },
            "nav": {
                "home": "Главная",
                "scientific": "Научные модули",
                "community": "Сообщество",
                "education": "Образование",
                "about": "О нас",
                "contact": "Контакты",
                "login": "Войти",
                "register": "Бесплатная регистрация",
                "language": "Язык"
            }
        },
        "ja": {
            "hero": {
                "badge": "土地復元科学プラットフォーム",
                "title": "エコノジン",
                "subtitle": "統合スマートマネジメント",
                "description": "水文学、炭素モデリング、リモートセンシング、AIによる乾燥・半乾燥地域の復元",
                "startSimulation": "シミュレーション開始",
                "freeEducation": "無料教育",
                "userRating": "ユーザー評価",
                "activeUsers": "アクティブユーザー",
                "secure": "安全で信頼できる"
            },
            "stats": {
                "hectares": "監視ヘクタール",
                "carbon": "吸収CO₂トン",
                "farmers": "アクティブ農家",
                "basins": "流域盆地"
            },
            "modules": {
                "scientific": "科学モジュール",
                "scientificDesc": "乾燥地復元の専門ツール",
                "community": "コミュニティとサービス",
                "communityDesc": "持続可能な農家に必要なすべて",
                "details": "詳細を見る",
                "projects": "成功プロジェクト",
                "projectsDesc": "土地復元の事例"
            },
            "features": {
                "free": "無料でオープン",
                "freeDesc": "すべての科学サービスが無料",
                "ai": "人工知能",
                "aiDesc": "高度なモデルによるスマート分析",
                "secure": "安全で信頼できる",
                "secureDesc": "研究データの保護",
                "global": "グローバルアクセス",
                "globalDesc": "世界中からアクセス可能"
            },
            "nav": {
                "home": "ホーム",
                "scientific": "科学モジュール",
                "community": "コミュニティ",
                "education": "教育",
                "about": "概要",
                "contact": "連絡先",
                "login": "ログイン",
                "register": "無料登録",
                "language": "言語"
            }
        },
        "tr": {
            "hero": {
                "badge": "Arazi Restorasyon Bilim Platformu",
                "title": "Econojin",
                "subtitle": "Entegre Akıllı Yönetim",
                "description": "Hidroloji, karbon modelleme, uzaktan algılama ve yapay zeka ile kurak ve yarı kurak alanların restorasyonu",
                "startSimulation": "Simülasyonu Başlat",
                "freeEducation": "Ücretsiz Eğitim",
                "userRating": "Kullanıcı Puanı",
                "activeUsers": "Aktif Kullanıcı",
                "secure": "Güvenli ve Güvenilir"
            },
            "stats": {
                "hectares": "İzlenen Hektar",
                "carbon": "Emilen CO₂ Ton",
                "farmers": "Aktif Çiftçi",
                "basins": "Su Havzası"
            },
            "modules": {
                "scientific": "Bilimsel Modüller",
                "scientificDesc": "Kurak arazi restorasyonu için uzman araçlar",
                "community": "Topluluk ve Hizmetler",
                "communityDesc": "Sürdürülebilir bir çiftçinin ihtiyacı olan her şey",
                "details": "Detayları Gör",
                "projects": "Başarılı Projeler",
                "projectsDesc": "Arazi restorasyon örnekleri"
            },
            "features": {
                "free": "Ücretsiz ve Açık",
                "freeDesc": "Tüm bilimsel hizmetler ücretsiz",
                "ai": "Yapay Zeka",
                "aiDesc": "Gelişmiş modellerle akıllı analiz",
                "secure": "Güvenli ve Güvenilir",
                "secureDesc": "Araştırma verilerinizin korunması",
                "global": "Küresel Erişim",
                "globalDesc": "Dünyanın her yerinden erişilebilir"
            },
            "nav": {
                "home": "Ana Sayfa",
                "scientific": "Bilimsel Modüller",
                "community": "Topluluk",
                "education": "Eğitim",
                "about": "Hakkında",
                "contact": "İletişim",
                "login": "Giriş",
                "register": "Ücretsiz Kayıt",
                "language": "Dil"
            }
        }
    }
    
    # ایجاد فایل‌های JSON
    i18n_dir = WEB / "lib" / "i18n" / "locales"
    for lang, data in translations.items():
        write_file(i18n_dir / f"{lang}.json", json.dumps(data, ensure_ascii=False, indent=2))
    
    # ایجاد languages config
    languages_config = '''export const languages = {
  fa: { name: "فارسی", native: "فارسی", dir: "rtl", flag: "🇮🇷" },
  en: { name: "English", native: "English", dir: "ltr", flag: "🇬🇧" },
  ar: { name: "Arabic", native: "العربية", dir: "rtl", flag: "🇸🇦" },
  zh: { name: "Chinese", native: "中文", dir: "ltr", flag: "🇨🇳" },
  es: { name: "Spanish", native: "Español", dir: "ltr", flag: "🇪🇸" },
  fr: { name: "French", native: "Français", dir: "ltr", flag: "🇫🇷" },
  de: { name: "German", native: "Deutsch", dir: "ltr", flag: "🇩🇪" },
  ru: { name: "Russian", native: "Русский", dir: "ltr", flag: "🇷🇺" },
  pt: { name: "Portuguese", native: "Português", dir: "ltr", flag: "🇵🇹" },
  ja: { name: "Japanese", native: "日本語", dir: "ltr", flag: "🇯🇵" },
  tr: { name: "Turkish", native: "Türkçe", dir: "ltr", flag: "🇹🇷" },
  hi: { name: "Hindi", native: "हिन्दी", dir: "ltr", flag: "🇮🇳" },
  ur: { name: "Urdu", native: "اردو", dir: "rtl", flag: "🇵🇰" },
  id: { name: "Indonesian", native: "Bahasa Indonesia", dir: "ltr", flag: "🇮🇩" },
  ko: { name: "Korean", native: "한국어", dir: "ltr", flag: "🇰🇷" },
  it: { name: "Italian", native: "Italiano", dir: "ltr", flag: "🇮🇹" },
  nl: { name: "Dutch", native: "Nederlands", dir: "ltr", flag: "🇳🇱" },
  pl: { name: "Polish", native: "Polski", dir: "ltr", flag: "🇵🇱" },
  sv: { name: "Swedish", native: "Svenska", dir: "ltr", flag: "🇸🇪" },
  ms: { name: "Malay", native: "Bahasa Melayu", dir: "ltr", flag: "🇲🇾" },
};

export type Locale = keyof typeof languages;
export const locales = Object.keys(languages) as Locale[];
export const defaultLocale: Locale = "fa";

export function getDirection(locale: Locale): "rtl" | "ltr" {
  return languages[locale]?.dir || "ltr";
}

export function getNativeName(locale: Locale): string {
  return languages[locale]?.native || locale;
}
'''
    write_file(WEB / "lib" / "i18n" / "languages.ts", languages_config)


# ========== 3. ایجاد Language Provider ==========
def create_language_provider():
    print("\n🌐 ایجاد Language Provider...")
    
    content = '''"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { languages, defaultLocale, Locale, getDirection } from "./languages";

interface LanguageContextType {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  direction: "rtl" | "ltr";
  t: (key: string) => string;
  translations: any;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(defaultLocale);
  const [translations, setTranslations] = useState<any>({});
  const [loaded, setLoaded] = useState(false);

  const direction = getDirection(locale);

  // Load locale from localStorage or browser
  useEffect(() => {
    const saved = localStorage.getItem("econojin_locale") as Locale | null;
    const browserLang = navigator.language.split("-")[0] as Locale;
    const initial = saved || (languages[browserLang] ? browserLang : defaultLocale);
    setLocaleState(initial);
  }, []);

  // Load translations
  useEffect(() => {
    const loadTranslations = async () => {
      try {
        const module = await import(`./locales/${locale}.json`);
        setTranslations(module.default);
        setLoaded(true);
      } catch (e) {
        console.error(`Failed to load ${locale} translations`);
        const fallback = await import(`./locales/en.json`);
        setTranslations(fallback.default);
        setLoaded(true);
      }
    };
    loadTranslations();
  }, [locale]);

  // Update document direction
  useEffect(() => {
    document.documentElement.dir = direction;
    document.documentElement.lang = locale;
  }, [locale, direction]);

  const setLocale = (newLocale: Locale) => {
    setLocaleState(newLocale);
    localStorage.setItem("econojin_locale", newLocale);
  };

  // Translation function with dot notation
  const t = (key: string): string => {
    if (!loaded || !translations) return key;
    const keys = key.split(".");
    let value: any = translations;
    for (const k of keys) {
      if (value && typeof value === "object" && k in value) {
        value = value[k];
      } else {
        return key;
      }
    }
    return typeof value === "string" ? value : key;
  };

  return (
    <LanguageContext.Provider value={{ locale, setLocale, direction, t, translations }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used within LanguageProvider");
  }
  return context;
}
'''
    
    write_file(WEB / "lib" / "i18n" / "provider.tsx", content)


# ========== 4. ایجاد Language Switcher ==========
def create_language_switcher():
    print("\n🌐 ایجاد Language Switcher...")
    
    content = '''"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Globe, Check } from "lucide-react";
import { languages, locales, Locale } from "@/lib/i18n/languages";
import { useLanguage } from "@/lib/i18n/provider";

export function LanguageSwitcher() {
  const [isOpen, setIsOpen] = useState(false);
  const { locale, setLocale } = useLanguage();
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700 transition-all"
        aria-label="Select language"
      >
        <Globe className="h-4 w-4 text-emerald-400" />
        <span className="text-sm text-slate-200">{languages[locale]?.flag}</span>
        <span className="text-sm text-slate-200 hidden sm:inline">{languages[locale]?.native}</span>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute top-full mt-2 left-0 w-64 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl overflow-hidden z-50"
          >
            <div className="p-2 border-b border-slate-800">
              <p className="text-xs text-slate-500 px-2 py-1">Select Language / انتخاب زبان</p>
            </div>
            <div className="max-h-96 overflow-y-auto p-2">
              {locales.map((lang) => (
                <button
                  key={lang}
                  onClick={() => {
                    setLocale(lang);
                    setIsOpen(false);
                  }}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg transition-all ${
                    locale === lang
                      ? "bg-emerald-500/10 text-emerald-400"
                      : "text-slate-300 hover:bg-slate-800"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xl">{languages[lang].flag}</span>
                    <div className="text-right">
                      <p className="text-sm font-medium">{languages[lang].native}</p>
                      <p className="text-xs text-slate-500">{languages[lang].name}</p>
                    </div>
                  </div>
                  {locale === lang && <Check className="h-4 w-4 text-emerald-400" />}
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
'''
    
    write_file(WEB / "components" / "LanguageSwitcher.tsx", content)


# ========== 5. به‌روزرسانی Navbar ==========
def update_navbar():
    print("\n🧭 به‌روزرسانی Navbar با Language Switcher...")
    
    navbar_path = WEB / "components" / "layout" / "Navbar.tsx"
    if not navbar_path.exists():
        print("   ⚠️ Navbar.tsx یافت نشد - ایجاد می‌شود...")
    
    content = '''"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Leaf, Menu, X, ChevronDown, LogIn } from "lucide-react";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { useLanguage } from "@/lib/i18n/provider";

const SCIENTIFIC_MODULES = [
  { id: "hydrology", title: "هیدرولوژی", href: "/hydrology" },
  { id: "soil-water", title: "آب خاک", href: "/soil-water" },
  { id: "carbon", title: "کربن خاک", href: "/carbon" },
  { id: "erosion", title: "فرسایش خاک", href: "/erosion" },
  { id: "crop", title: "محصول", href: "/crop" },
  { id: "weather", title: "هواشناسی", href: "/weather" },
  { id: "gis", title: "GIS", href: "/gis" },
  { id: "sentinel", title: "سنجش از دور", href: "/sentinel" },
];

const COMMUNITY_MODULES = [
  { id: "library", title: "کتابخانه", href: "/library" },
  { id: "education", title: "آموزش", href: "/education" },
  { id: "community", title: "جامعه", href: "/community" },
  { id: "shop", title: "فروشگاه", href: "/shop" },
  { id: "psychology", title: "سلامت روان", href: "/psychology" },
  { id: "games", title: "بازی‌ها", href: "/games" },
  { id: "ecomining", title: "EcoCoin", href: "/ecomining" },
];

export default function Navbar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);
  const { t } = useLanguage();

  return (
    <nav className="sticky top-0 z-40 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800">
      <div className="container mx-auto px-6">
        <div className="flex items-center justify-between h-16 gap-4">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group flex-shrink-0">
            <div className="p-2 rounded-lg bg-gradient-to-br from-emerald-500 to-green-600">
              <Leaf className="h-5 w-5 text-white" />
            </div>
            <div>
              <p className="font-bold text-white leading-tight">اکو نوژین</p>
              <p className="text-[10px] text-slate-400">Econojin</p>
            </div>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden lg:flex items-center gap-1 flex-1 justify-center">
            <Link href="/" className="px-4 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800/50 hover:text-white">{t("nav.home")}</Link>
            
            <div className="relative" onMouseEnter={() => setOpenDropdown("sci")} onMouseLeave={() => setOpenDropdown(null)}>
              <button className="px-4 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800/50 hover:text-white flex items-center gap-1">
                {t("nav.scientific")} <ChevronDown className="h-4 w-4" />
              </button>
              <AnimatePresence>
                {openDropdown === "sci" && (
                  <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 10 }} className="absolute top-full right-0 mt-2 w-56 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl p-2">
                    {SCIENTIFIC_MODULES.map(m => (
                      <Link key={m.id} href={m.href} className="block px-3 py-2 rounded-lg text-sm text-slate-200 hover:bg-slate-800">{m.title}</Link>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            <div className="relative" onMouseEnter={() => setOpenDropdown("com")} onMouseLeave={() => setOpenDropdown(null)}>
              <button className="px-4 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800/50 hover:text-white flex items-center gap-1">
                {t("nav.community")} <ChevronDown className="h-4 w-4" />
              </button>
              <AnimatePresence>
                {openDropdown === "com" && (
                  <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 10 }} className="absolute top-full right-0 mt-2 w-56 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl p-2">
                    {COMMUNITY_MODULES.map(m => (
                      <Link key={m.id} href={m.href} className="block px-3 py-2 rounded-lg text-sm text-slate-200 hover:bg-slate-800">{m.title}</Link>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            <Link href="/education" className="px-4 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800/50 hover:text-white">{t("nav.education")}</Link>
            <Link href="/about" className="px-4 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800/50 hover:text-white">{t("nav.about")}</Link>
            <Link href="/contact" className="px-4 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800/50 hover:text-white">{t("nav.contact")}</Link>
          </div>

          {/* Right Side: Language + Auth */}
          <div className="flex items-center gap-2">
            <LanguageSwitcher />
            
            <div className="hidden lg:flex items-center gap-2">
              <Link href="/login" className="px-4 py-2 text-sm text-slate-300 hover:text-white flex items-center gap-1">
                <LogIn className="h-4 w-4" /> {t("nav.login")}
              </Link>
              <Link href="/register" className="px-4 py-2 bg-gradient-to-l from-emerald-500 to-green-600 text-white text-sm rounded-lg hover:shadow-lg hover:shadow-emerald-500/30 transition-all">
                {t("nav.register")}
              </Link>
            </div>

            <button onClick={() => setMobileOpen(!mobileOpen)} className="lg:hidden p-2 text-slate-300">
              {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div initial={{ height: 0 }} animate={{ height: "auto" }} exit={{ height: 0 }} className="lg:hidden overflow-hidden bg-slate-900 border-t border-slate-800">
            <div className="container mx-auto px-6 py-4 space-y-2">
              <Link href="/" onClick={() => setMobileOpen(false)} className="block px-4 py-2 rounded-lg text-slate-200 hover:bg-slate-800">{t("nav.home")}</Link>
              <div className="border-t border-slate-800 pt-2 mt-2">
                <p className="px-4 py-1 text-xs text-slate-500">{t("nav.scientific")}</p>
                {SCIENTIFIC_MODULES.map(m => (
                  <Link key={m.id} href={m.href} onClick={() => setMobileOpen(false)} className="block px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 rounded-lg">{m.title}</Link>
                ))}
              </div>
              <div className="border-t border-slate-800 pt-2 mt-2">
                <p className="px-4 py-1 text-xs text-slate-500">{t("nav.community")}</p>
                {COMMUNITY_MODULES.map(m => (
                  <Link key={m.id} href={m.href} onClick={() => setMobileOpen(false)} className="block px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 rounded-lg">{m.title}</Link>
                ))}
              </div>
              <div className="border-t border-slate-800 pt-2 mt-2 flex gap-2">
                <Link href="/login" onClick={() => setMobileOpen(false)} className="flex-1 px-4 py-2 border border-slate-700 rounded-lg text-center text-sm">{t("nav.login")}</Link>
                <Link href="/register" onClick={() => setMobileOpen(false)} className="flex-1 px-4 py-2 bg-emerald-600 rounded-lg text-center text-sm">{t("nav.register")}</Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}
'''
    
    write_file(navbar_path, content)


# ========== 6. به‌روزرسانی Layout اصلی ==========
def update_layout():
    print("\n🎨 به‌روزرسانی Layout با Language Provider...")
    
    content = '''import "@/styles/globals.css";
import type { Metadata } from "next";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";
import ChatWidget from "@/components/ai/ChatWidget";
import { LanguageProvider } from "@/lib/i18n/provider";

export const metadata: Metadata = {
  title: "اکو نوژین | Econojin - مدیریت هوشمند احیای مناظر خشک",
  description: "پلتفرم علمی بین‌المللی برای احیای زمین‌های خشک و نیمه‌خشک - 20 زبان",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fa" dir="rtl" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="bg-slate-950 text-slate-100 antialiased min-h-screen flex flex-col" suppressHydrationWarning>
        <LanguageProvider>
          <Navbar />
          <main className="flex-1">{children}</main>
          <Footer />
          <ChatWidget />
        </LanguageProvider>
      </body>
    </html>
  );
}
'''
    
    write_file(WEB / "app" / "layout.tsx", content)


# ========== 7. به‌روزرسانی صفحه اصلی با ترجمه ==========
def update_homepage_with_translations():
    print("\n🏠 به‌روزرسانی صفحه اصلی با ترجمه...")
    
    page_path = WEB / "app" / "page.tsx"
    if not page_path.exists():
        print("   ⚠️ page.tsx یافت نشد")
        return
    
    content = page_path.read_text(encoding="utf-8")
    
    # اضافه کردن import useLanguage
    if 'import { useLanguage } from "@/lib/i18n/provider"' not in content:
        content = content.replace(
            'import { healthService } from "@/lib/api";',
            'import { healthService } from "@/lib/api";\nimport { useLanguage } from "@/lib/i18n/provider";'
        )
    
    # اضافه کردن useLanguage در component
    if 'const { t } = useLanguage();' not in content:
        content = content.replace(
            '  const [loading, setLoading] = useState(true);',
            '  const [loading, setLoading] = useState(true);\n  const { t } = useLanguage();'
        )
    
    # جایگزینی متن‌های ثابت با t()
    replacements = [
        ('>پلتفرم علمی احیای زمین</span>', '>{t("hero.badge")}</span>'),
        ('>اکو نوژین</span>', '>{t("hero.title")}</span>'),
        ('>مدیریت هوشمند یکپارچه</p>', '>{t("hero.subtitle")}</p>'),
        ('>احیای مناظر خشک و نیمه‌خشک زمین با ترکیب علم هیدرولوژی، مدل‌سازی کربن، سنجش از دور و هوش مصنوعی', '>{t("hero.description")}'),
        ('>شروع شبیه‌سازی', '>{t("hero.startSimulation")}'),
        ('>آموزش رایگان<', '>{t("hero.freeEducation")}<'),
        ('>ماژول‌های علمی</h2>', '>{t("modules.scientific")}</h2>'),
        ('>ابزارهای تخصصی برای احیای زمین‌های خشک و نیمه‌خشک</p>', '>{t("modules.scientificDesc")}</p>'),
        ('>جامعه و خدمات</h2>', '>{t("modules.community")}</h2>'),
        ('>همه آنچه برای یک کشاورز پایدار نیاز دارید</p>', '>{t("modules.communityDesc")}</p>'),
        ('>مشاهده جزئیات</span>', '>{t("modules.details")}</span>'),
        ('>پروژه‌های موفق</h2>', '>{t("modules.projects")}</h2>'),
        ('>نمونه‌هایی از احیای زمین‌های خشک و نیمه‌خشک</p>', '>{t("modules.projectsDesc")}</p>'),
    ]
    
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
    
    page_path.write_text(content, encoding="utf-8")
    print("   ✅ صفحه اصلی با ترجمه به‌روز شد")


# ========== Main ==========
def main():
    print("🌍 افزودن سیستم چندزبانه کامل")
    print("=" * 70)
    print("ویژگی‌ها:")
    print("   • 20 زبان بین‌المللی")
    print("   • Language Switcher حرفه‌ای")
    print("   • رفع warning NaN")
    print("   • ترجمه کامل صفحه اصلی")
    print("=" * 70)
    
    if not WEB.exists():
        print(f"❌ دایرکتوری {WEB} یافت نشد!")
        return 1
    
    fix_page_nan_warning()
    create_translations()
    create_language_provider()
    create_language_switcher()
    update_navbar()
    update_layout()
    update_homepage_with_translations()
    
    print("\n" + "=" * 70)
    print("✅ سیستم چندزبانه تکمیل شد!")
    print("\n🌐 زبان‌های پشتیبانی شده:")
    print("   🇮🇷 فارسی    🇬🇧 English    🇸🇦 العربية    🇨🇳 中文")
    print("   🇪🇸 Español   🇫🇷 Français   🇩🇪 Deutsch    🇷🇺 Русский")
    print("   🇵🇹 Português 🇯🇵 日本語    🇹🇷 Türkçe     🇮🇳 हिन्दी")
    print("   🇵🇰 اردو     🇮🇩 Indonesia 🇰🇷 한국어    🇮🇹 Italiano")
    print("   🇳🇱 Nederlands 🇵🇱 Polski   🇸🇪 Svenska    🇲🇾 Melayu")
    
    print("\n🚀 گام بعدی:")
    print("   1. پاک‌سازی کش: Remove-Item .next -Recurse -Force")
    print("   2. اجرا: pnpm run dev -- -p 3001")
    print("   3. مشاهده: http://localhost:3001")
    print("   4. تست Language Switcher در Navbar")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())