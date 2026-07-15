#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 apps/web — 10-Language Expansion Script
================================================================================
 Run from D:\\econojin.com\\apps\\web

   python generate_languages.py

 CREATES
 -------
  8 new language locale files:
    - src/i18n/locales/ar.json  (Arabic, RTL)
    - src/i18n/locales/es.json  (Spanish)
    - src/i18n/locales/fr.json  (French)
    - src/i18n/locales/de.json  (German)
    - src/i18n/locales/ru.json  (Russian)
    - src/i18n/locales/zh.json  (Chinese)
    - src/i18n/locales/tr.json  (Turkish)
    - src/i18n/locales/hi.json  (Hindi)

 UPDATES
 -------
  - src/i18n/index.ts          (registers 10 languages)
  - src/lib/i18n-utils.ts      (LANGUAGE_META for 10 languages)

 STRATEGY
 --------
  Each new locale file is created by:
  1. Loading the existing en.json as the base template (all 496 keys)
  2. Overriding the most critical ~80 keys with proper translations
     (common, nav, auth, dashboard, user, error)
  3. Domain-specific keys (carbon, soil, hydrology, etc.) remain in English
     with a clear "_needs_translation: true" marker for future professional
     translation pass

  This pragmatic approach lets us ship 10 languages immediately while
  clearly marking what still needs human translation.
================================================================================
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Detect project root
# ---------------------------------------------------------------------------

def detect_root() -> Path:
    cwd = Path.cwd()
    for candidate in [cwd, *cwd.parents]:
        if (candidate / "tsconfig.json").exists() and (candidate / "package.json").exists():
            return candidate
    return cwd

# ---------------------------------------------------------------------------
# Critical key translations for each language
# These cover: common, nav, navGroups, user, auth (login/register), dashboard,
# error — the strings users see most often.
# Domain-specific keys remain as English fallback.
# ---------------------------------------------------------------------------

LANGUAGES = {
    "ar": {
        "_meta": {"name": "العربية", "englishName": "Arabic", "flag": "🇸🇦", "dir": "rtl"},
        "translations": {
            "common": {
                "appName": "إيكونوجين",
                "appTagline": "منصة رصد البيئة والاقتصاد الأخضر",
                "loading": "جارٍ التحميل…",
                "retry": "إعادة المحاولة",
                "cancel": "إلغاء",
                "save": "حفظ",
                "delete": "حذف",
                "edit": "تحرير",
                "search": "بحث",
                "close": "إغلاق",
                "back": "رجوع",
                "yes": "نعم",
                "no": "لا",
                "all": "الكل",
                "soon": "قريباً",
                "notFound": "الصفحة غير موجودة",
                "notFoundDescription": "العنوان المطلوب غير متاح.",
                "backToDashboard": "العودة إلى لوحة التحكم",
                "language": "اللغة",
                "persian": "فارسی",
                "english": "English",
                "toman": "تومان"
            },
            "nav": {
                "dashboard": "لوحة التحكم",
                "documents": "المستندات",
                "carbon": "الكربون",
                "watersheds": "أحواض المياه",
                "soil": "التربة",
                "animations": "الرسوم المتحركة",
                "about": "من نحن",
                "accounting": "المحاسبة",
                "agricultureSchools": "مدارس الزراعة",
                "blog": "المدونة",
                "contact": "اتصل بنا",
                "faq": "الأسئلة الشائعة"
            },
            "navGroups": {"main": "القائمة الرئيسية", "tools": "الأدوات"},
            "user": {
                "myProfile": "ملفي الشخصي",
                "logout": "تسجيل الخروج",
                "login": "تسجيل الدخول",
                "register": "إنشاء حساب",
                "sessionExpired": "انتهت الجلسة. يرجى تسجيل الدخول مرة أخرى.",
                "unknownError": "خطأ غير معروف في الاتصال بالخادم"
            },
            "auth": {
                "loginTitle": "تسجيل الدخول إلى إيكونوجين",
                "loginSubtitle": "مرحباً بك في منصة رصد البيئة",
                "registerTitle": "إنشاء حساب جديد",
                "registerSubtitle": "انضم إلى مجتمع إيكونوجين الأخضر",
                "identifier": "البريد الإلكتروني أو اسم المستخدم",
                "identifierPlaceholder": "name@econojin.com أو @username",
                "username": "اسم المستخدم",
                "usernamePlaceholder": "ali_mohammadi",
                "usernameHint": "٣ إلى ٣٢ حرفاً: أحرف إنجليزية وأرقام وشرطة سفلية",
                "displayName": "الاسم المعروض",
                "displayNamePlaceholder": "مثال: Ali Mohammadi",
                "email": "البريد الإلكتروني",
                "emailPlaceholder": "name@econojin.com",
                "password": "كلمة المرور",
                "passwordPlaceholder": "••••••••",
                "confirmPassword": "تأكيد كلمة المرور",
                "rememberMe": "تذكرني",
                "forgotPassword": "نسيت كلمة المرور؟",
                "acceptTerms": "أوافق على شروط الخدمة وسياسة الخصوصية.",
                "terms": "شروط الخدمة",
                "privacy": "سياسة الخصوصية",
                "signInButton": "تسجيل الدخول",
                "signUpButton": "إنشاء حساب",
                "noAccount": "ليس لديك حساب؟",
                "haveAccount": "لديك حساب بالفعل؟",
                "passwordStrength": "قوة كلمة المرور",
                "passwordWeak": "ضعيفة",
                "passwordMedium": "متوسطة",
                "passwordStrong": "قوية",
                "loginLoading": "جارٍ تسجيل الدخول…",
                "registerLoading": "جارٍ إنشاء الحساب…",
                "errors": {
                    "identifierRequired": "البريد الإلكتروني أو اسم المستخدم مطلوب",
                    "passwordRequired": "كلمة المرور مطلوبة",
                    "passwordTooShort": "يجب أن تكون كلمة المرور ٨ أحرف على الأقل",
                    "usernameRequired": "اسم المستخدم مطلوب",
                    "usernameInvalid": "يجب أن يكون اسم المستخدم ٣-٣٢ حرفاً، أحرف إنجليزية وأرقام وشرطة سفلية فقط",
                    "emailRequired": "البريد الإلكتروني مطلوب",
                    "emailInvalid": "صيغة بريد إلكتروني غير صالحة",
                    "confirmMismatch": "تأكيد كلمة المرور غير مطابق",
                    "termsRequired": "يجب قبول الشروط",
                    "loginFailed": "فشل تسجيل الدخول. يرجى المحاولة مرة أخرى.",
                    "registerFailed": "فشل إنشاء الحساب. يرجى المحاولة مرة أخرى."
                }
            },
            "dashboard": {
                "title": "لوحة التحكم",
                "greetingMorning": "صباح الخير",
                "greetingNoon": "مساء الخير",
                "greetingEvening": "مساء الخير",
                "welcomeMessage": "مرحباً بك في منصة رصد البيئة. إليك حالة اليوم.",
                "sustainabilityScore": "درجة الاستدامة",
                "activeReports": "التقارير النشطة",
                "monitoredRegions": "المناطق المرصودة",
                "ecoCoin": "إيكوكوين",
                "newReports": "تقارير جديدة",
                "newRegions": "مناطق جديدة",
                "pointsUp": "نقاط",
                "quickAccess": "وصول سريع",
                "viewReports": "عرض التقارير",
                "welcomeBannerTitle": "مرحباً بك في مجتمع إيكونوجين الأخضر",
                "welcomeBannerText": "ساهم في الإبلاغ البيئي وإرسال بيانات الرصد للمساعدة في حماية طبيعة إيران — واكسب مكافآت إيكوكوين."
            },
            "error": {
                "boundaryTitle": "حدث خطأ ما",
                "boundaryDescription": "حدث خطأ أثناء عرض هذا القسم. يرجى المحاولة مرة أخرى.",
                "boundaryRetry": "إعادة المحاولة",
                "loadingSession": "جارٍ تحميل الجلسة…",
                "loadingPage": "جارٍ تحميل الصفحة…"
            }
        }
    },
    "es": {
        "_meta": {"name": "Español", "englishName": "Spanish", "flag": "🇪🇸", "dir": "ltr"},
        "translations": {
            "common": {
                "appName": "Econojin",
                "appTagline": "Plataforma de monitoreo ambiental y economía verde",
                "loading": "Cargando…",
                "retry": "Reintentar",
                "cancel": "Cancelar",
                "save": "Guardar",
                "delete": "Eliminar",
                "edit": "Editar",
                "search": "Buscar",
                "close": "Cerrar",
                "back": "Volver",
                "yes": "Sí",
                "no": "No",
                "all": "Todos",
                "soon": "Próximamente",
                "notFound": "Página no encontrada",
                "notFoundDescription": "La URL solicitada no está disponible.",
                "backToDashboard": "Volver al panel",
                "language": "Idioma",
                "persian": "فارسی",
                "english": "English",
                "toman": "Toman"
            },
            "nav": {
                "dashboard": "Panel",
                "documents": "Documentos",
                "carbon": "Carbono",
                "watersheds": "Cuencas",
                "soil": "Suelo",
                "animations": "Animaciones",
                "about": "Acerca de",
                "accounting": "Contabilidad",
                "agricultureSchools": "Escuelas de Agricultura",
                "blog": "Blog",
                "contact": "Contacto",
                "faq": "FAQ"
            },
            "navGroups": {"main": "Menú principal", "tools": "Herramientas"},
            "user": {
                "myProfile": "Mi perfil",
                "logout": "Cerrar sesión",
                "login": "Iniciar sesión",
                "register": "Registrarse",
                "sessionExpired": "Su sesión ha expirado. Inicie sesión de nuevo.",
                "unknownError": "Error desconocido de comunicación con el servidor"
            },
            "auth": {
                "loginTitle": "Iniciar sesión en Econojin",
                "loginSubtitle": "Bienvenido a la plataforma de monitoreo ambiental",
                "registerTitle": "Crear una cuenta nueva",
                "registerSubtitle": "Únase a la comunidad verde de Econojin",
                "identifier": "Correo o nombre de usuario",
                "identifierPlaceholder": "name@econojin.com o @username",
                "username": "Nombre de usuario",
                "usernamePlaceholder": "ali_mohammadi",
                "usernameHint": "3 a 32 caracteres: letras, números y guion bajo",
                "displayName": "Nombre para mostrar",
                "displayNamePlaceholder": "ej. Ali Mohammadi",
                "email": "Correo electrónico",
                "emailPlaceholder": "name@econojin.com",
                "password": "Contraseña",
                "passwordPlaceholder": "••••••••",
                "confirmPassword": "Confirmar contraseña",
                "rememberMe": "Recuérdame",
                "forgotPassword": "¿Olvidó su contraseña?",
                "acceptTerms": "Acepto los Términos de Servicio y la Política de Privacidad.",
                "terms": "Términos de Servicio",
                "privacy": "Política de Privacidad",
                "signInButton": "Iniciar sesión",
                "signUpButton": "Registrarse",
                "noAccount": "¿No tiene cuenta?",
                "haveAccount": "¿Ya tiene cuenta?",
                "passwordStrength": "Fortaleza de la contraseña",
                "passwordWeak": "débil",
                "passwordMedium": "media",
                "passwordStrong": "fuerte",
                "loginLoading": "Iniciando sesión…",
                "registerLoading": "Creando cuenta…",
                "errors": {
                    "identifierRequired": "Correo o nombre de usuario requerido",
                    "passwordRequired": "Contraseña requerida",
                    "passwordTooShort": "La contraseña debe tener al menos 8 caracteres",
                    "usernameRequired": "Nombre de usuario requerido",
                    "usernameInvalid": "El nombre de usuario debe tener 3-32 caracteres, solo letras, números y guion bajo",
                    "emailRequired": "Correo requerido",
                    "emailInvalid": "Formato de correo inválido",
                    "confirmMismatch": "La confirmación no coincide",
                    "termsRequired": "Debe aceptar los términos",
                    "loginFailed": "Error al iniciar sesión. Intente de nuevo.",
                    "registerFailed": "Error al registrarse. Intente de nuevo."
                }
            },
            "dashboard": {
                "title": "Panel",
                "greetingMorning": "Buenos días",
                "greetingNoon": "Buenas tardes",
                "greetingEvening": "Buenas noches",
                "welcomeMessage": "Bienvenido a la plataforma de monitoreo ambiental. Aquí está el estado de hoy.",
                "sustainabilityScore": "Puntuación de sostenibilidad",
                "activeReports": "Informes activos",
                "monitoredRegions": "Regiones monitoreadas",
                "ecoCoin": "EcoCoin",
                "newReports": "nuevos informes",
                "newRegions": "nuevas regiones",
                "pointsUp": "puntos",
                "quickAccess": "Acceso rápido",
                "viewReports": "Ver informes",
                "welcomeBannerTitle": "Bienvenido a la comunidad verde de Econojin",
                "welcomeBannerText": "Contribuya con reportes ambientales y datos de monitoreo para proteger la naturaleza."
            },
            "error": {
                "boundaryTitle": "Algo salió mal",
                "boundaryDescription": "Ocurrió un error al renderizar esta sección. Intente de nuevo.",
                "boundaryRetry": "Reintentar",
                "loadingSession": "Cargando sesión…",
                "loadingPage": "Cargando página…"
            }
        }
    },
    "fr": {
        "_meta": {"name": "Français", "englishName": "French", "flag": "🇫🇷", "dir": "ltr"},
        "translations": {
            "common": {
                "appName": "Econojin",
                "appTagline": "Plateforme de surveillance environnementale et économie verte",
                "loading": "Chargement…",
                "retry": "Réessayer",
                "cancel": "Annuler",
                "save": "Enregistrer",
                "delete": "Supprimer",
                "edit": "Modifier",
                "search": "Rechercher",
                "close": "Fermer",
                "back": "Retour",
                "yes": "Oui",
                "no": "Non",
                "all": "Tous",
                "soon": "Bientôt disponible",
                "notFound": "Page non trouvée",
                "notFoundDescription": "L'URL demandée n'est pas disponible.",
                "backToDashboard": "Retour au tableau de bord",
                "language": "Langue",
                "persian": "فارسی",
                "english": "English",
                "toman": "Toman"
            },
            "nav": {
                "dashboard": "Tableau de bord",
                "documents": "Documents",
                "carbon": "Carbone",
                "watersheds": "Bassins versants",
                "soil": "Sol",
                "animations": "Animations",
                "about": "À propos",
                "accounting": "Comptabilité",
                "agricultureSchools": "Écoles d'agriculture",
                "blog": "Blog",
                "contact": "Contact",
                "faq": "FAQ"
            },
            "navGroups": {"main": "Menu principal", "tools": "Outils"},
            "user": {
                "myProfile": "Mon profil",
                "logout": "Déconnexion",
                "login": "Connexion",
                "register": "Inscription",
                "sessionExpired": "Votre session a expiré. Veuillez vous reconnecter.",
                "unknownError": "Erreur inconnue de communication avec le serveur"
            },
            "auth": {
                "loginTitle": "Connexion à Econojin",
                "loginSubtitle": "Bienvenue sur la plateforme de surveillance environnementale",
                "registerTitle": "Créer un nouveau compte",
                "registerSubtitle": "Rejoignez la communauté verte d'Econojin",
                "identifier": "E-mail ou nom d'utilisateur",
                "identifierPlaceholder": "name@econojin.com ou @username",
                "username": "Nom d'utilisateur",
                "usernamePlaceholder": "ali_mohammadi",
                "usernameHint": "3 à 32 caractères : lettres, chiffres et tiret bas",
                "displayName": "Nom d'affichage",
                "displayNamePlaceholder": "ex. Ali Mohammadi",
                "email": "E-mail",
                "emailPlaceholder": "name@econojin.com",
                "password": "Mot de passe",
                "passwordPlaceholder": "••••••••",
                "confirmPassword": "Confirmer le mot de passe",
                "rememberMe": "Se souvenir de moi",
                "forgotPassword": "Mot de passe oublié ?",
                "acceptTerms": "J'accepte les Conditions d'utilisation et la Politique de confidentialité.",
                "terms": "Conditions d'utilisation",
                "privacy": "Politique de confidentialité",
                "signInButton": "Connexion",
                "signUpButton": "Inscription",
                "noAccount": "Pas de compte ?",
                "haveAccount": "Vous avez déjà un compte ?",
                "passwordStrength": "Force du mot de passe",
                "passwordWeak": "faible",
                "passwordMedium": "moyen",
                "passwordStrong": "fort",
                "loginLoading": "Connexion…",
                "registerLoading": "Création du compte…",
                "errors": {
                    "identifierRequired": "E-mail ou nom d'utilisateur requis",
                    "passwordRequired": "Mot de passe requis",
                    "passwordTooShort": "Le mot de passe doit comporter au moins 8 caractères",
                    "usernameRequired": "Nom d'utilisateur requis",
                    "usernameInvalid": "Le nom d'utilisateur doit comporter 3 à 32 caractères, uniquement des lettres, chiffres et tiret bas",
                    "emailRequired": "E-mail requis",
                    "emailInvalid": "Format d'e-mail invalide",
                    "confirmMismatch": "La confirmation ne correspond pas",
                    "termsRequired": "Vous devez accepter les conditions",
                    "loginFailed": "Échec de la connexion. Veuillez réessayer.",
                    "registerFailed": "Échec de l'inscription. Veuillez réessayer."
                }
            },
            "dashboard": {
                "title": "Tableau de bord",
                "greetingMorning": "Bonjour",
                "greetingNoon": "Bon après-midi",
                "greetingEvening": "Bonsoir",
                "welcomeMessage": "Bienvenue sur la plateforme de surveillance environnementale. Voici l'état du jour.",
                "sustainabilityScore": "Score de durabilité",
                "activeReports": "Rapports actifs",
                "monitoredRegions": "Régions surveillées",
                "ecoCoin": "EcoCoin",
                "newReports": "nouveaux rapports",
                "newRegions": "nouvelles régions",
                "pointsUp": "points",
                "quickAccess": "Accès rapide",
                "viewReports": "Voir les rapports",
                "welcomeBannerTitle": "Bienvenue dans la communauté verte d'Econojin",
                "welcomeBannerText": "Contribuez aux rapports environnementaux et aux données de surveillance pour protéger la nature."
            },
            "error": {
                "boundaryTitle": "Une erreur s'est produite",
                "boundaryDescription": "Une erreur s'est produite lors de l'affichage de cette section. Veuillez réessayer.",
                "boundaryRetry": "Réessayer",
                "loadingSession": "Chargement de la session…",
                "loadingPage": "Chargement de la page…"
            }
        }
    },
    "de": {
        "_meta": {"name": "Deutsch", "englishName": "German", "flag": "🇩🇪", "dir": "ltr"},
        "translations": {
            "common": {
                "appName": "Econojin",
                "appTagline": "Plattform für Umweltüberwachung und grüne Wirtschaft",
                "loading": "Wird geladen…",
                "retry": "Erneut versuchen",
                "cancel": "Abbrechen",
                "save": "Speichern",
                "delete": "Löschen",
                "edit": "Bearbeiten",
                "search": "Suchen",
                "close": "Schließen",
                "back": "Zurück",
                "yes": "Ja",
                "no": "Nein",
                "all": "Alle",
                "soon": "Demnächst verfügbar",
                "notFound": "Seite nicht gefunden",
                "notFoundDescription": "Die angeforderte URL ist nicht verfügbar.",
                "backToDashboard": "Zurück zum Dashboard",
                "language": "Sprache",
                "persian": "فارسی",
                "english": "English",
                "toman": "Toman"
            },
            "nav": {
                "dashboard": "Dashboard",
                "documents": "Dokumente",
                "carbon": "Kohlenstoff",
                "watersheds": "Einzugsgebiete",
                "soil": "Boden",
                "animations": "Animationen",
                "about": "Über uns",
                "accounting": "Buchhaltung",
                "agricultureSchools": "Landwirtschaftsschulen",
                "blog": "Blog",
                "contact": "Kontakt",
                "faq": "FAQ"
            },
            "navGroups": {"main": "Hauptmenü", "tools": "Werkzeuge"},
            "user": {
                "myProfile": "Mein Profil",
                "logout": "Abmelden",
                "login": "Anmelden",
                "register": "Registrieren",
                "sessionExpired": "Ihre Sitzung ist abgelaufen. Bitte melden Sie sich erneut an.",
                "unknownError": "Unbekannter Fehler bei der Serverkommunikation"
            },
            "auth": {
                "loginTitle": "Bei Econojin anmelden",
                "loginSubtitle": "Willkommen auf der Umweltüberwachungsplattform",
                "registerTitle": "Neues Konto erstellen",
                "registerSubtitle": "Treten Sie der Econojin-Grünen-Community bei",
                "identifier": "E-Mail oder Benutzername",
                "identifierPlaceholder": "name@econojin.com oder @username",
                "username": "Benutzername",
                "usernamePlaceholder": "ali_mohammadi",
                "usernameHint": "3 bis 32 Zeichen: Buchstaben, Ziffern und Unterstrich",
                "displayName": "Anzeigename",
                "displayNamePlaceholder": "z.B. Ali Mohammadi",
                "email": "E-Mail",
                "emailPlaceholder": "name@econojin.com",
                "password": "Passwort",
                "passwordPlaceholder": "••••••••",
                "confirmPassword": "Passwort bestätigen",
                "rememberMe": "Angemeldet bleiben",
                "forgotPassword": "Passwort vergessen?",
                "acceptTerms": "Ich stimme den Nutzungsbedingungen und der Datenschutzrichtlinie zu.",
                "terms": "Nutzungsbedingungen",
                "privacy": "Datenschutzrichtlinie",
                "signInButton": "Anmelden",
                "signUpButton": "Registrieren",
                "noAccount": "Noch kein Konto?",
                "haveAccount": "Bereits ein Konto?",
                "passwordStrength": "Passwortstärke",
                "passwordWeak": "schwach",
                "passwordMedium": "mittel",
                "passwordStrong": "stark",
                "loginLoading": "Anmeldung…",
                "registerLoading": "Konto wird erstellt…",
                "errors": {
                    "identifierRequired": "E-Mail oder Benutzername erforderlich",
                    "passwordRequired": "Passwort erforderlich",
                    "passwordTooShort": "Passwort muss mindestens 8 Zeichen lang sein",
                    "usernameRequired": "Benutzername erforderlich",
                    "usernameInvalid": "Benutzername muss 3-32 Zeichen lang sein, nur Buchstaben, Ziffern und Unterstrich",
                    "emailRequired": "E-Mail erforderlich",
                    "emailInvalid": "Ungültiges E-Mail-Format",
                    "confirmMismatch": "Passwortbestätigung stimmt nicht überein",
                    "termsRequired": "Sie müssen den Bedingungen zustimmen",
                    "loginFailed": "Anmeldung fehlgeschlagen. Bitte erneut versuchen.",
                    "registerFailed": "Registrierung fehlgeschlagen. Bitte erneut versuchen."
                }
            },
            "dashboard": {
                "title": "Dashboard",
                "greetingMorning": "Guten Morgen",
                "greetingNoon": "Guten Tag",
                "greetingEvening": "Guten Abend",
                "welcomeMessage": "Willkommen auf der Umweltüberwachungsplattform. Hier ist der heutige Status.",
                "sustainabilityScore": "Nachhaltigkeitswert",
                "activeReports": "Aktive Berichte",
                "monitoredRegions": "Überwachte Regionen",
                "ecoCoin": "EcoCoin",
                "newReports": "neue Berichte",
                "newRegions": "neue Regionen",
                "pointsUp": "Punkte",
                "quickAccess": "Schnellzugriff",
                "viewReports": "Berichte anzeigen",
                "welcomeBannerTitle": "Willkommen in der Econojin-Grünen-Community",
                "welcomeBannerText": "Tragen Sie zu Umweltberichten und Überwachungsdaten bei, um die Natur zu schützen."
            },
            "error": {
                "boundaryTitle": "Etwas ist schiefgegangen",
                "boundaryDescription": "Beim Rendern dieses Abschnitts ist ein Fehler aufgetreten. Bitte erneut versuchen.",
                "boundaryRetry": "Erneut versuchen",
                "loadingSession": "Sitzung wird geladen…",
                "loadingPage": "Seite wird geladen…"
            }
        }
    },
    "ru": {
        "_meta": {"name": "Русский", "englishName": "Russian", "flag": "🇷🇺", "dir": "ltr"},
        "translations": {
            "common": {
                "appName": "Econojin",
                "appTagline": "Платформа экологического мониторинга и зелёной экономики",
                "loading": "Загрузка…",
                "retry": "Повторить",
                "cancel": "Отмена",
                "save": "Сохранить",
                "delete": "Удалить",
                "edit": "Изменить",
                "search": "Поиск",
                "close": "Закрыть",
                "back": "Назад",
                "yes": "Да",
                "no": "Нет",
                "all": "Все",
                "soon": "Скоро",
                "notFound": "Страница не найдена",
                "notFoundDescription": "Запрошенный URL недоступен.",
                "backToDashboard": "Вернуться на панель управления",
                "language": "Язык",
                "persian": "فارسی",
                "english": "English",
                "toman": "Томан"
            },
            "nav": {
                "dashboard": "Панель управления",
                "documents": "Документы",
                "carbon": "Углерод",
                "watersheds": "Водосборы",
                "soil": "Почва",
                "animations": "Анимации",
                "about": "О нас",
                "accounting": "Бухгалтерия",
                "agricultureSchools": "Сельскохозяйственные школы",
                "blog": "Блог",
                "contact": "Контакты",
                "faq": "FAQ"
            },
            "navGroups": {"main": "Главное меню", "tools": "Инструменты"},
            "user": {
                "myProfile": "Мой профиль",
                "logout": "Выйти",
                "login": "Войти",
                "register": "Регистрация",
                "sessionExpired": "Сессия истекла. Пожалуйста, войдите снова.",
                "unknownError": "Неизвестная ошибка связи с сервером"
            },
            "auth": {
                "loginTitle": "Вход в Econojin",
                "loginSubtitle": "Добро пожаловать на платформу экологического мониторинга",
                "registerTitle": "Создать новый аккаунт",
                "registerSubtitle": "Присоединяйтесь к зелёному сообществу Econojin",
                "identifier": "Email или имя пользователя",
                "identifierPlaceholder": "name@econojin.com или @username",
                "username": "Имя пользователя",
                "usernamePlaceholder": "ali_mohammadi",
                "usernameHint": "3–32 символа: буквы, цифры и подчёркивание",
                "displayName": "Отображаемое имя",
                "displayNamePlaceholder": "напр. Али Мохаммади",
                "email": "Email",
                "emailPlaceholder": "name@econojin.com",
                "password": "Пароль",
                "passwordPlaceholder": "••••••••",
                "confirmPassword": "Подтвердите пароль",
                "rememberMe": "Запомнить меня",
                "forgotPassword": "Забыли пароль?",
                "acceptTerms": "Я согласен с Условиями обслуживания и Политикой конфиденциальности.",
                "terms": "Условия обслуживания",
                "privacy": "Политика конфиденциальности",
                "signInButton": "Войти",
                "signUpButton": "Зарегистрироваться",
                "noAccount": "Нет аккаунта?",
                "haveAccount": "Уже есть аккаунт?",
                "passwordStrength": "Надёжность пароля",
                "passwordWeak": "слабый",
                "passwordMedium": "средний",
                "passwordStrong": "надёжный",
                "loginLoading": "Вход…",
                "registerLoading": "Создание аккаунта…",
                "errors": {
                    "identifierRequired": "Email или имя пользователя обязательно",
                    "passwordRequired": "Пароль обязателен",
                    "passwordTooShort": "Пароль должен содержать не менее 8 символов",
                    "usernameRequired": "Имя пользователя обязательно",
                    "usernameInvalid": "Имя пользователя должно быть 3–32 символа, только буквы, цифры и подчёркивание",
                    "emailRequired": "Email обязателен",
                    "emailInvalid": "Неверный формат email",
                    "confirmMismatch": "Подтверждение пароля не совпадает",
                    "termsRequired": "Необходимо принять условия",
                    "loginFailed": "Ошибка входа. Попробуйте снова.",
                    "registerFailed": "Ошибка регистрации. Попробуйте снова."
                }
            },
            "dashboard": {
                "title": "Панель управления",
                "greetingMorning": "Доброе утро",
                "greetingNoon": "Добрый день",
                "greetingEvening": "Добрый вечер",
                "welcomeMessage": "Добро пожаловать на платформу экологического мониторинга. Вот статус на сегодня.",
                "sustainabilityScore": "Оценка устойчивости",
                "activeReports": "Активные отчёты",
                "monitoredRegions": "Отслеживаемые регионы",
                "ecoCoin": "EcoCoin",
                "newReports": "новых отчётов",
                "newRegions": "новых регионов",
                "pointsUp": "баллов",
                "quickAccess": "Быстрый доступ",
                "viewReports": "Просмотр отчётов",
                "welcomeBannerTitle": "Добро пожаловать в зелёное сообщество Econojin",
                "welcomeBannerText": "Вносите вклад в экологические отчёты и данные мониторинга для защиты природы."
            },
            "error": {
                "boundaryTitle": "Что-то пошло не так",
                "boundaryDescription": "Произошла ошибка при отображении этого раздела. Попробуйте снова.",
                "boundaryRetry": "Повторить",
                "loadingSession": "Загрузка сессии…",
                "loadingPage": "Загрузка страницы…"
            }
        }
    },
    "zh": {
        "_meta": {"name": "中文", "englishName": "Chinese", "flag": "🇨🇳", "dir": "ltr"},
        "translations": {
            "common": {
                "appName": "Econojin",
                "appTagline": "环境监测与绿色经济平台",
                "loading": "加载中…",
                "retry": "重试",
                "cancel": "取消",
                "save": "保存",
                "delete": "删除",
                "edit": "编辑",
                "search": "搜索",
                "close": "关闭",
                "back": "返回",
                "yes": "是",
                "no": "否",
                "all": "全部",
                "soon": "即将推出",
                "notFound": "页面未找到",
                "notFoundDescription": "请求的URL不可用。",
                "backToDashboard": "返回仪表板",
                "language": "语言",
                "persian": "فارسی",
                "english": "English",
                "toman": "土曼"
            },
            "nav": {
                "dashboard": "仪表板",
                "documents": "文档",
                "carbon": "碳",
                "watersheds": "流域",
                "soil": "土壤",
                "animations": "动画",
                "about": "关于",
                "accounting": "会计",
                "agricultureSchools": "农业学校",
                "blog": "博客",
                "contact": "联系",
                "faq": "常见问题"
            },
            "navGroups": {"main": "主菜单", "tools": "工具"},
            "user": {
                "myProfile": "我的资料",
                "logout": "退出登录",
                "login": "登录",
                "register": "注册",
                "sessionExpired": "会话已过期。请重新登录。",
                "unknownError": "与服务器通信时发生未知错误"
            },
            "auth": {
                "loginTitle": "登录 Econojin",
                "loginSubtitle": "欢迎来到环境监测平台",
                "registerTitle": "创建新账户",
                "registerSubtitle": "加入 Econojin 绿色社区",
                "identifier": "邮箱或用户名",
                "identifierPlaceholder": "name@econojin.com 或 @username",
                "username": "用户名",
                "usernamePlaceholder": "ali_mohammadi",
                "usernameHint": "3至32个字符：字母、数字和下划线",
                "displayName": "显示名称",
                "displayNamePlaceholder": "例如：Ali Mohammadi",
                "email": "邮箱",
                "emailPlaceholder": "name@econojin.com",
                "password": "密码",
                "passwordPlaceholder": "••••••••",
                "confirmPassword": "确认密码",
                "rememberMe": "记住我",
                "forgotPassword": "忘记密码？",
                "acceptTerms": "我同意服务条款和隐私政策。",
                "terms": "服务条款",
                "privacy": "隐私政策",
                "signInButton": "登录",
                "signUpButton": "注册",
                "noAccount": "还没有账户？",
                "haveAccount": "已经有账户？",
                "passwordStrength": "密码强度",
                "passwordWeak": "弱",
                "passwordMedium": "中",
                "passwordStrong": "强",
                "loginLoading": "登录中…",
                "registerLoading": "创建账户中…",
                "errors": {
                    "identifierRequired": "邮箱或用户名为必填项",
                    "passwordRequired": "密码为必填项",
                    "passwordTooShort": "密码必须至少8个字符",
                    "usernameRequired": "用户名为必填项",
                    "usernameInvalid": "用户名必须为3-32个字符，仅限字母、数字和下划线",
                    "emailRequired": "邮箱为必填项",
                    "emailInvalid": "邮箱格式无效",
                    "confirmMismatch": "确认密码不匹配",
                    "termsRequired": "必须接受条款",
                    "loginFailed": "登录失败。请重试。",
                    "registerFailed": "注册失败。请重试。"
                }
            },
            "dashboard": {
                "title": "仪表板",
                "greetingMorning": "早上好",
                "greetingNoon": "下午好",
                "greetingEvening": "晚上好",
                "welcomeMessage": "欢迎来到环境监测平台。这是今日状态。",
                "sustainabilityScore": "可持续性评分",
                "activeReports": "活跃报告",
                "monitoredRegions": "监测区域",
                "ecoCoin": "EcoCoin",
                "newReports": "新报告",
                "newRegions": "新区域",
                "pointsUp": "分",
                "quickAccess": "快速访问",
                "viewReports": "查看报告",
                "welcomeBannerTitle": "欢迎加入 Econojin 绿色社区",
                "welcomeBannerText": "贡献环境报告和监测数据，帮助保护自然。"
            },
            "error": {
                "boundaryTitle": "出错了",
                "boundaryDescription": "渲染此部分时发生错误。请重试。",
                "boundaryRetry": "重试",
                "loadingSession": "加载会话中…",
                "loadingPage": "加载页面中…"
            }
        }
    },
    "tr": {
        "_meta": {"name": "Türkçe", "englishName": "Turkish", "flag": "🇹🇷", "dir": "ltr"},
        "translations": {
            "common": {
                "appName": "Econojin",
                "appTagline": "Çevre izleme ve yeşil ekonomi platformu",
                "loading": "Yükleniyor…",
                "retry": "Tekrar dene",
                "cancel": "İptal",
                "save": "Kaydet",
                "delete": "Sil",
                "edit": "Düzenle",
                "search": "Ara",
                "close": "Kapat",
                "back": "Geri",
                "yes": "Evet",
                "no": "Hayır",
                "all": "Tümü",
                "soon": "Yakında",
                "notFound": "Sayfa bulunamadı",
                "notFoundDescription": "İstenen URL mevcut değil.",
                "backToDashboard": "Panel'e dön",
                "language": "Dil",
                "persian": "فارسی",
                "english": "English",
                "toman": "Toman"
            },
            "nav": {
                "dashboard": "Panel",
                "documents": "Belgeler",
                "carbon": "Karbon",
                "watersheds": "Havzalar",
                "soil": "Toprak",
                "animations": "Animasyonlar",
                "about": "Hakkında",
                "accounting": "Muhasebe",
                "agricultureSchools": "Tarım Okulları",
                "blog": "Blog",
                "contact": "İletişim",
                "faq": "SSS"
            },
            "navGroups": {"main": "Ana menü", "tools": "Araçlar"},
            "user": {
                "myProfile": "Profilim",
                "logout": "Çıkış yap",
                "login": "Giriş yap",
                "register": "Kayıt ol",
                "sessionExpired": "Oturumunuzun süresi doldu. Lütfen tekrar giriş yapın.",
                "unknownError": "Sunucu ile iletişimde bilinmeyen hata"
            },
            "auth": {
                "loginTitle": "Econojin'e giriş yap",
                "loginSubtitle": "Çevre izleme platformuna hoş geldiniz",
                "registerTitle": "Yeni hesap oluştur",
                "registerSubtitle": "Econojin yeşil topluluğuna katılın",
                "identifier": "E-posta veya kullanıcı adı",
                "identifierPlaceholder": "name@econojin.com veya @username",
                "username": "Kullanıcı adı",
                "usernamePlaceholder": "ali_mohammadi",
                "usernameHint": "3-32 karakter: harf, rakam ve alt çizgi",
                "displayName": "Görünen ad",
                "displayNamePlaceholder": "örn. Ali Mohammadi",
                "email": "E-posta",
                "emailPlaceholder": "name@econojin.com",
                "password": "Şifre",
                "passwordPlaceholder": "••••••••",
                "confirmPassword": "Şifreyi onayla",
                "rememberMe": "Beni hatırla",
                "forgotPassword": "Şifremi unuttum?",
                "acceptTerms": "Kullanım Şartları ve Gizlilik Politikası'nı kabul ediyorum.",
                "terms": "Kullanım Şartları",
                "privacy": "Gizlilik Politikası",
                "signInButton": "Giriş yap",
                "signUpButton": "Kayıt ol",
                "noAccount": "Hesabınız yok mu?",
                "haveAccount": "Zaten hesabınız var mı?",
                "passwordStrength": "Şifre gücü",
                "passwordWeak": "zayıf",
                "passwordMedium": "orta",
                "passwordStrong": "güçlü",
                "loginLoading": "Giriş yapılıyor…",
                "registerLoading": "Hesap oluşturuluyor…",
                "errors": {
                    "identifierRequired": "E-posta veya kullanıcı adı gerekli",
                    "passwordRequired": "Şifre gerekli",
                    "passwordTooShort": "Şifre en az 8 karakter olmalıdır",
                    "usernameRequired": "Kullanıcı adı gerekli",
                    "usernameInvalid": "Kullanıcı adı 3-32 karakter olmalı, sadece harf, rakam ve alt çizgi",
                    "emailRequired": "E-posta gerekli",
                    "emailInvalid": "Geçersiz e-posta formatı",
                    "confirmMismatch": "Şifre onayı eşleşmiyor",
                    "termsRequired": "Şartları kabul etmelisiniz",
                    "loginFailed": "Giriş başarısız. Lütfen tekrar deneyin.",
                    "registerFailed": "Kayıt başarısız. Lütfen tekrar deneyin."
                }
            },
            "dashboard": {
                "title": "Panel",
                "greetingMorning": "Günaydın",
                "greetingNoon": "İyi günler",
                "greetingEvening": "İyi akşamlar",
                "welcomeMessage": "Çevre izleme platformuna hoş geldiniz. İşte bugünün durumu.",
                "sustainabilityScore": "Sürdürülebilirlik skoru",
                "activeReports": "Aktif raporlar",
                "monitoredRegions": "İzlenen bölgeler",
                "ecoCoin": "EcoCoin",
                "newReports": "yeni rapor",
                "newRegions": "yeni bölge",
                "pointsUp": "puan",
                "quickAccess": "Hızlı erişim",
                "viewReports": "Raporları görüntüle",
                "welcomeBannerTitle": "Econojin yeşil topluluğuna hoş geldiniz",
                "welcomeBannerText": "Doğayı korumak için çevre raporlarına ve izleme verilerine katkıda bulunun."
            },
            "error": {
                "boundaryTitle": "Bir şeyler ters gitti",
                "boundaryDescription": "Bu bölümü görüntülerken bir hata oluştu. Lütfen tekrar deneyin.",
                "boundaryRetry": "Tekrar dene",
                "loadingSession": "Oturum yükleniyor…",
                "loadingPage": "Sayfa yükleniyor…"
            }
        }
    },
    "hi": {
        "_meta": {"name": "हिन्दी", "englishName": "Hindi", "flag": "🇮🇳", "dir": "ltr"},
        "translations": {
            "common": {
                "appName": "Econojin",
                "appTagline": "पर्यावरण निगरानी और हरित अर्थव्यवस्था मंच",
                "loading": "लोड हो रहा है…",
                "retry": "पुनः प्रयास करें",
                "cancel": "रद्द करें",
                "save": "सहेजें",
                "delete": "हटाएं",
                "edit": "संपादित करें",
                "search": "खोजें",
                "close": "बंद करें",
                "back": "वापस",
                "yes": "हां",
                "no": "नहीं",
                "all": "सभी",
                "soon": "जल्द ही",
                "notFound": "पेज नहीं मिला",
                "notFoundDescription": "अनुरोधित URL उपलब्ध नहीं है।",
                "backToDashboard": "डैशबोर्ड पर वापस जाएं",
                "language": "भाषा",
                "persian": "فارسی",
                "english": "English",
                "toman": "तोमन"
            },
            "nav": {
                "dashboard": "डैशबोर्ड",
                "documents": "दस्तावेज़",
                "carbon": "कार्बन",
                "watersheds": "जलग्रहण क्षेत्र",
                "soil": "मिट्टी",
                "animations": "एनिमेशन",
                "about": "हमारे बारे में",
                "accounting": "लेखांकन",
                "agricultureSchools": "कृषि विद्यालय",
                "blog": "ब्लॉग",
                "contact": "संपर्क करें",
                "faq": "सामान्य प्रश्न"
            },
            "navGroups": {"main": "मुख्य मेनू", "tools": "उपकरण"},
            "user": {
                "myProfile": "मेरी प्रोफ़ाइल",
                "logout": "लॉग आउट",
                "login": "लॉग इन",
                "register": "रजिस्टर करें",
                "sessionExpired": "आपका सत्र समाप्त हो गया है। कृपया पुनः लॉग इन करें।",
                "unknownError": "सर्वर के साथ संवाद में अज्ञात त्रुटि"
            },
            "auth": {
                "loginTitle": "Econojin में लॉग इन करें",
                "loginSubtitle": "पर्यावरण निगरानी मंच में आपका स्वागत है",
                "registerTitle": "नया खाता बनाएं",
                "registerSubtitle": "Econojin हरित समुदाय में शामिल हों",
                "identifier": "ईमेल या उपयोगकर्ता नाम",
                "identifierPlaceholder": "name@econojin.com या @username",
                "username": "उपयोगकर्ता नाम",
                "usernamePlaceholder": "ali_mohammadi",
                "usernameHint": "3 से 32 अक्षर: अक्षर, अंक और अंडरस्कोर",
                "displayName": "प्रदर्शित नाम",
                "displayNamePlaceholder": "जैसे Ali Mohammadi",
                "email": "ईमेल",
                "emailPlaceholder": "name@econojin.com",
                "password": "पासवर्ड",
                "passwordPlaceholder": "••••••••",
                "confirmPassword": "पासवर्ड की पुष्टि करें",
                "rememberMe": "मुझे याद रखें",
                "forgotPassword": "पासवर्ड भूल गए?",
                "acceptTerms": "मैं सेवा की शर्तों और गोपनीयता नीति से सहमत हूं।",
                "terms": "सेवा की शर्तें",
                "privacy": "गोपनीयता नीति",
                "signInButton": "लॉग इन करें",
                "signUpButton": "रजिस्टर करें",
                "noAccount": "खाता नहीं है?",
                "haveAccount": "पहले से खाता है?",
                "passwordStrength": "पासवर्ड की ताकत",
                "passwordWeak": "कमजोर",
                "passwordMedium": "मध्यम",
                "passwordStrong": "मजबूत",
                "loginLoading": "लॉग इन हो रहा है…",
                "registerLoading": "खाता बनाया जा रहा है…",
                "errors": {
                    "identifierRequired": "ईमेल या उपयोगकर्ता नाम आवश्यक है",
                    "passwordRequired": "पासवर्ड आवश्यक है",
                    "passwordTooShort": "पासवर्ड कम से कम 8 अक्षर का होना चाहिए",
                    "usernameRequired": "उपयोगकर्ता नाम आवश्यक है",
                    "usernameInvalid": "उपयोगकर्ता नाम 3-32 अक्षर का होना चाहिए, केवल अक्षर, अंक और अंडरस्कोर",
                    "emailRequired": "ईमेल आवश्यक है",
                    "emailInvalid": "अमान्य ईमेल प्रारूप",
                    "confirmMismatch": "पासवर्ड पुष्टि मेल नहीं खाती",
                    "termsRequired": "आपको शर्तों को स्वीकार करना होगा",
                    "loginFailed": "लॉग इन विफल। कृपया पुनः प्रयास करें।",
                    "registerFailed": "रजिस्ट्रेशन विफल। कृपया पुनः प्रयास करें।"
                }
            },
            "dashboard": {
                "title": "डैशबोर्ड",
                "greetingMorning": "सुप्रभात",
                "greetingNoon": "नमस्कार",
                "greetingEvening": "शुभ संध्या",
                "welcomeMessage": "पर्यावरण निगरानी मंच में आपका स्वागत है। आज की स्थिति यहाँ है।",
                "sustainabilityScore": "स्थिरता स्कोर",
                "activeReports": "सक्रिय रिपोर्ट",
                "monitoredRegions": "निगरानी क्षेत्र",
                "ecoCoin": "EcoCoin",
                "newReports": "नई रिपोर्ट",
                "newRegions": "नए क्षेत्र",
                "pointsUp": "अंक",
                "quickAccess": "त्वरित पहुंच",
                "viewReports": "रिपोर्ट देखें",
                "welcomeBannerTitle": "Econojin हरित समुदाय में आपका स्वागत है",
                "welcomeBannerText": "प्रकृति की रक्षा के लिए पर्यावरण रिपोर्ट और निगरानी डेटा में योगदान दें।"
            },
            "error": {
                "boundaryTitle": "कुछ गलत हो गया",
                "boundaryDescription": "इस अनुभाग को प्रस्तुत करते समय त्रुटि हुई। कृपया पुनः प्रयास करें।",
                "boundaryRetry": "पुनः प्रयास करें",
                "loadingSession": "सत्र लोड हो रहा है…",
                "loadingPage": "पेज लोड हो रहा है…"
            }
        }
    },
}

# ---------------------------------------------------------------------------
# Updated i18n/index.ts (10 languages)
# ---------------------------------------------------------------------------

I18N_INDEX_TS = '''/**
 * ============================================================================
 *  i18n initialization — 10-language support (react-i18next)
 * ============================================================================
 *
 *  Supported languages:
 *    RTL: fa (Persian), ar (Arabic)
 *    LTR: en, es, fr, de, ru, zh, tr, hi
 *
 *  Total native speakers covered: ~4.8 billion (60% of world population)
 * ============================================================================
 */

import { createInstance, type i18n as I18nInstance } from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import { initReactI18next } from "react-i18next";

import fa from "./locales/fa.json";
import en from "./locales/en.json";
import ar from "./locales/ar.json";
import es from "./locales/es.json";
import fr from "./locales/fr.json";
import de from "./locales/de.json";
import ru from "./locales/ru.json";
import zh from "./locales/zh.json";
import tr from "./locales/tr.json";
import hi from "./locales/hi.json";

// ---------------------------------------------------------------------------
// Language constants
// ---------------------------------------------------------------------------

export const SUPPORTED_LANGUAGES = [
  "fa", "en", "ar", "es", "fr", "de", "ru", "zh", "tr", "hi"
] as const;
export type SupportedLanguage = (typeof SUPPORTED_LANGUAGES)[number];

export const DEFAULT_LANGUAGE: SupportedLanguage = (() => {
  const env = import.meta.env["VITE_DEFAULT_LANG"] as string | undefined;
  if (env && (SUPPORTED_LANGUAGES as readonly string[]).includes(env)) {
    return env as SupportedLanguage;
  }
  return "fa";
})();

export const RTL_LANGUAGES: ReadonlySet<string> = new Set([
  "fa",
  "ar",
  "ur",
  "he",
  "ps",
  "sd",
]);

// ---------------------------------------------------------------------------
// Resources
// ---------------------------------------------------------------------------

const resources = {
  fa: { translation: fa },
  en: { translation: en },
  ar: { translation: ar },
  es: { translation: es },
  fr: { translation: fr },
  de: { translation: de },
  ru: { translation: ru },
  zh: { translation: zh },
  tr: { translation: tr },
  hi: { translation: hi },
} as const;

// ---------------------------------------------------------------------------
// Create the i18n instance
// ---------------------------------------------------------------------------

export const i18n: I18nInstance = createInstance();

export const i18nReady: Promise<I18nInstance> = i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: DEFAULT_LANGUAGE,
    supportedLngs: SUPPORTED_LANGUAGES,
    nonExplicitSupportedLngs: true,
    interpolation: { escapeValue: false },
    detection: {
      order: ["localStorage", "navigator", "htmlTag"],
      lookupLocalStorage: "econojin.lang",
      caches: ["localStorage"],
    },
    react: { useSuspense: false },
  })
  .then(() => i18n);

// ---------------------------------------------------------------------------
// Direction helpers
// ---------------------------------------------------------------------------

export function getLanguageDir(language: string): "rtl" | "ltr" {
  return RTL_LANGUAGES.has(language) ? "rtl" : "ltr";
}

export function isLanguageRTL(language: string): boolean {
  return RTL_LANGUAGES.has(language);
}

export function isSupportedLanguage(value: string): value is SupportedLanguage {
  return (SUPPORTED_LANGUAGES as readonly string[]).includes(value);
}

export function coerceLanguage(value: string | undefined | null): SupportedLanguage {
  if (!value) return DEFAULT_LANGUAGE;
  if (isSupportedLanguage(value)) return value;
  const base = value.split("-")[0] ?? "";
  if (isSupportedLanguage(base)) return base;
  return DEFAULT_LANGUAGE;
}

// ---------------------------------------------------------------------------
// Development-only diagnostics
// ---------------------------------------------------------------------------

if (import.meta.env.DEV) {
  void i18nReady.then(() => {
    // eslint-disable-next-line no-console
    console.info(
      `[i18n] language="${i18n.language}" dir="${getLanguageDir(i18n.language)}"`,
    );
  });

  i18n.on("missingKey", (lngs, namespace, key) => {
    // eslint-disable-next-line no-console
    console.warn(`[i18n] missing key "${key}" in [${lngs.join(", ")}] / "${namespace}"`);
  });
}

export default i18n;
'''

# ---------------------------------------------------------------------------
# Updated i18n-utils.ts (10 languages metadata)
# ---------------------------------------------------------------------------

I18N_UTILS_TS = '''/**
 * ============================================================================
 *  i18n utilities — direction-aware helpers for 10 languages
 * ============================================================================
 */

import type { SupportedLanguage } from "@/i18n";

// ---------------------------------------------------------------------------
// Language → direction mapping
// ---------------------------------------------------------------------------

const RTL_LANGUAGES: ReadonlySet<string> = new Set(["fa", "ar", "ur", "he", "ps", "sd"]);

export function isRTL(language: string): boolean {
  return RTL_LANGUAGES.has(language);
}

export function getDir(language: string): "rtl" | "ltr" {
  return isRTL(language) ? "rtl" : "ltr";
}

// ---------------------------------------------------------------------------
// Locale-aware number/date formatting (cached)
// ---------------------------------------------------------------------------

const LOCALE_MAP: Record<string, string> = {
  fa: "fa-IR",
  en: "en-US",
  ar: "ar-SA",
  es: "es-ES",
  fr: "fr-FR",
  de: "de-DE",
  ru: "ru-RU",
  zh: "zh-CN",
  tr: "tr-TR",
  hi: "hi-IN",
};

const numberFormatters: Record<string, Intl.NumberFormat> = {};
const decimalFormatters: Record<string, Intl.NumberFormat> = {};
const dateFormatters: Record<string, Intl.DateTimeFormat> = {};
const dateTimeFormatters: Record<string, Intl.DateTimeFormat> = {};
const longDateFormatters: Record<string, Intl.DateTimeFormat> = {};

function getLocale(language: string): string {
  return LOCALE_MAP[language] ?? "en-US";
}

export function formatNumber(value: number, language: string = "fa"): string {
  const locale = getLocale(language);
  if (!numberFormatters[locale]) {
    numberFormatters[locale] = new Intl.NumberFormat(locale);
  }
  return numberFormatters[locale].format(value);
}

export function formatDecimal(value: number, language: string = "fa"): string {
  const locale = getLocale(language);
  if (!decimalFormatters[locale]) {
    decimalFormatters[locale] = new Intl.NumberFormat(locale, { maximumFractionDigits: 1 });
  }
  return decimalFormatters[locale].format(value);
}

export function formatDate(iso: string, language: string = "fa"): string {
  const locale = getLocale(language);
  if (!dateFormatters[locale]) {
    dateFormatters[locale] = new Intl.DateTimeFormat(locale, {
      year: "numeric",
      month: "numeric",
      day: "numeric",
    });
  }
  return dateFormatters[locale].format(new Date(iso));
}

export function formatDateTime(iso: string, language: string = "fa"): string {
  const locale = getLocale(language);
  if (!dateTimeFormatters[locale]) {
    dateTimeFormatters[locale] = new Intl.DateTimeFormat(locale, {
      year: "numeric",
      month: "numeric",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }
  return dateTimeFormatters[locale].format(new Date(iso));
}

export function formatLongDate(iso: string, language: string = "fa"): string {
  const locale = getLocale(language);
  if (!longDateFormatters[locale]) {
    longDateFormatters[locale] = new Intl.DateTimeFormat(locale, {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  }
  return longDateFormatters[locale].format(new Date(iso));
}

// ---------------------------------------------------------------------------
// Language metadata (10 languages)
// ---------------------------------------------------------------------------

export interface LanguageMeta {
  code: SupportedLanguage;
  nativeName: string;
  englishName: string;
  flag: string;
  dir: "rtl" | "ltr";
}

export const LANGUAGE_META: Readonly<Record<SupportedLanguage, LanguageMeta>> = {
  fa: { code: "fa", nativeName: "فارسی", englishName: "Persian", flag: "🇮🇷", dir: "rtl" },
  en: { code: "en", nativeName: "English", englishName: "English", flag: "🇬🇧", dir: "ltr" },
  ar: { code: "ar", nativeName: "العربية", englishName: "Arabic", flag: "🇸🇦", dir: "rtl" },
  es: { code: "es", nativeName: "Español", englishName: "Spanish", flag: "🇪🇸", dir: "ltr" },
  fr: { code: "fr", nativeName: "Français", englishName: "French", flag: "🇫🇷", dir: "ltr" },
  de: { code: "de", nativeName: "Deutsch", englishName: "German", flag: "🇩🇪", dir: "ltr" },
  ru: { code: "ru", nativeName: "Русский", englishName: "Russian", flag: "🇷🇺", dir: "ltr" },
  zh: { code: "zh", nativeName: "中文", englishName: "Chinese", flag: "🇨🇳", dir: "ltr" },
  tr: { code: "tr", nativeName: "Türkçe", englishName: "Turkish", flag: "🇹🇷", dir: "ltr" },
  hi: { code: "hi", nativeName: "हिन्दी", englishName: "Hindi", flag: "🇮🇳", dir: "ltr" },
};

export const AVAILABLE_LANGUAGES: readonly LanguageMeta[] = Object.values(LANGUAGE_META);
'''

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base."""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

def write_file(root: Path, rel_path: str, content: str) -> bool:
    full = root / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)
    content_bytes = content.encode("utf-8")
    if full.exists() and full.read_bytes() == content_bytes:
        return False
    full.write_bytes(content_bytes)
    return True

def main() -> int:
    root = detect_root()
    print(f"[INFO] Project root: {root}")
    print()

    print("=" * 72)
    print(" Generating 8 new language locale files")
    print("=" * 72)

    # Load en.json as base template
    en_path = root / "src/i18n/locales/en.json"
    if not en_path.exists():
        print(f"[ERROR] {en_path} not found. Run this script from the apps/web directory.")
        return 1

    en_data = json.loads(en_path.read_text(encoding="utf-8"))

    for code, info in LANGUAGES.items():
        meta = info["_meta"]
        translations = info["translations"]

        # Start with a deep copy of en.json, then override with translations
        merged = deep_merge(en_data, translations)

        # Add a _meta marker for translation status tracking
        merged["_translationStatus"] = {
            "language": code,
            "nativeName": meta["name"],
            "englishName": meta["englishName"],
            "direction": meta["dir"],
            "criticalKeysTranslated": True,
            "domainKeysNeedTranslation": True,
            "note": "Critical UI strings translated. Domain-specific terms use English fallback. Professional translation needed for full coverage."
        }

        out_path = root / f"src/i18n/locales/{code}.json"
        out_path.write_text(
            json.dumps(merged, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8"
        )
        print(f"  [created]  src/i18n/locales/{code}.json  ({meta['name']} / {meta['englishName']}, {meta['dir'].upper()})")

    print()
    print("=" * 72)
    print(" Updating i18n/index.ts (10 languages)")
    print("=" * 72)
    changed = write_file(root, "src/i18n/index.ts", I18N_INDEX_TS)
    print(f"  [{'updated' if changed else 'ok'}]  src/i18n/index.ts")

    print()
    print("=" * 72)
    print(" Updating lib/i18n-utils.ts (10 languages metadata)")
    print("=" * 72)
    changed = write_file(root, "src/lib/i18n-utils.ts", I18N_UTILS_TS)
    print(f"  [{'updated' if changed else 'ok'}]  src/lib/i18n-utils.ts")

    print()
    print("=" * 72)
    print(" DONE — 10 languages now supported")
    print("=" * 72)
    print()
    print("  Languages: fa, en, ar, es, fr, de, ru, zh, tr, hi")
    print("  RTL: fa (Persian), ar (Arabic)")
    print("  LTR: en, es, fr, de, ru, zh, tr, hi")
    print("  Total native speakers: ~4.8 billion (60% of world)")
    print()
    print("  Next step:")
    print("    pnpm run build")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
