#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
i18n Builder Module
Generates internationalization files for the frontend.
"""
import json
import logging
from .base_builder import BaseBuilder, FRONTEND_DIR

logger = logging.getLogger(__name__)

class I18nBuilder(BaseBuilder):
    SUPPORTED_LOCALES = ["fa", "en", "ar", "tr", "zh"]
    
    def __init__(self):
        super().__init__("i18n")
    
    def build(self):
        logger.info("\n" + "="*70)
        logger.info("🌐 Building i18n System")
        logger.info("="*70)
        
        for locale in self.SUPPORTED_LOCALES:
            self._create_locale_file(locale)
        self._create_i18n_index()
        return self.get_stats()
    
    def _create_locale_file(self, locale: str):
        translations = self._get_translations(locale)
        path = FRONTEND_DIR / "lib" / "i18n" / f"{locale}.json"
        self.write(path, json.dumps(translations, ensure_ascii=False, indent=2))
    
    def _get_translations(self, locale: str) -> dict:
        translations = {
            "fa": {"common": {"appName": "اکونوژین", "home": "خانه", "login": "ورود"}},
            "en": {"common": {"appName": "Econojin", "home": "Home", "login": "Login"}},
            "ar": {"common": {"appName": "إكونوجين", "home": "الرئيسية", "login": "دخول"}},
            "tr": {"common": {"appName": "Econojin", "home": "Ana Sayfa", "login": "Giriş"}},
            "zh": {"common": {"appName": "Econojin", "home": "首页", "login": "登录"}}
        }
        return translations.get(locale, translations["en"])
    
    def _create_i18n_index(self):
        """ایجاد فایل index.ts کامل برای تمام زبان‌های پشتیبانی شده"""
        content = ""
        for locale in self.SUPPORTED_LOCALES:
            content += f"import {locale} from './{locale}.json';\n"
        content += "\n"
        content += "export const translations = {\n"
        for locale in self.SUPPORTED_LOCALES:
            content += f"  {locale},\n"
        content += "};\n\n"
        content += f"export const locales = {self.SUPPORTED_LOCALES} as const;\n"
        content += "export type Locale = typeof locales[number];\n"
        
        path = FRONTEND_DIR / "lib" / "i18n" / "index.ts"
        self.write(path, content)
