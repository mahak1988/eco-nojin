import os
# api/modules/library/services.py
"""
سرویس‌های کتابخانه دیجیتال
- اتصال به پایگاه‌های داده خارجی
- اعتبارسنجی علمی
- سیستم امتیازدهی
- پردازش متنی و صوتی
"""
import httpx
import aiohttp
from typing import Dict, List, Optional
from datetime import datetime
import hashlib
import json


# ============================================================
# External Database Connectors
# ============================================================
class ExternalDatabaseConnector:
    """اتصال به پایگاه‌های داده خارجی"""
    
    @staticmethod
    async def search_google_scholar(query: str, max_results: int = 20) -> List[Dict]:
        """جستجو در Google Scholar"""
        # استفاده از SerpAPI یا مشابه
        api_key = os.getenv("API_KEY")
        url = "https://serpapi.com/search"
        params = {
            "engine": "google_scholar",
            "q": query,
            "api_key": api_key,
            "num": max_results,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data.get("organic_results", [])
        return []
    
    @staticmethod
    async def search_crossref(query: str, rows: int = 20) -> List[Dict]:
        """جستجو در CrossRef"""
        url = "https://api.crossref.org/works"
        params = {
            "query": query,
            "rows": rows,
            "sort": "relevance",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("items", [])
        return []
    
    @staticmethod
    async def search_doaj(query: str, max_results: int = 20) -> List[Dict]:
        """جستجو در DOAJ (مجلات دسترسی آزاد)"""
        url = "https://doaj.org/api/v1/search/articles"
        data = {
            "query": {
                "query_string": {
                    "query": query,
                    "default_field": "title"
                }
            },
            "max_results": max_results
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result.get("results", [])
        return []
    
    @staticmethod
    async def search_semantic_scholar(query: str, limit: int = 20) -> List[Dict]:
        """جستجو در Semantic Scholar"""
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "limit": limit,
            "fields": "title,abstract,authors,venue,year,citationCount"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
        return []
    
    @staticmethod
    async def fetch_orcid_publications(orcid_id: str) -> List[Dict]:
        """دریافت انتشارات از ORCID"""
        url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
        headers = {"Accept": "application/json"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data.get("group", [])
        return []


# ============================================================
# Scientific Validation Service
# ============================================================
class ScientificValidationService:
    """اعتبارسنجی علمی منابع"""
    
    @staticmethod
    def calculate_quality_score(publication: Dict) -> float:
        """
        محاسبه نمره کیفیت منبع (0-100)
        معیارها:
        - وجود DOI
        - تعداد استنادات
        - اعتبار مجله/ناشر
        - تعداد نویسندگان
        - کامل بودن متادیتا
        """
        score = 0
        
        # وجود DOI (20 امتیاز)
        if publication.get("doi"):
            score += 20
        
        # تعداد استنادات (30 امتیاز)
        citations = publication.get("citation_count", 0)
        if citations > 100:
            score += 30
        elif citations > 50:
            score += 25
        elif citations > 20:
            score += 20
        elif citations > 10:
            score += 15
        elif citations > 5:
            score += 10
        elif citations > 0:
            score += 5
        
        # اعتبار مجله (25 امتیاز)
        journal = publication.get("journal_name", "").lower()
        if any(x in journal for x in ["nature", "science", "cell"]):
            score += 25
        elif "springer" in journal or "elsevier" in journal:
            score += 20
        elif publication.get("publisher"):
            score += 15
        
        # کامل بودن متادیتا (25 امتیاز)
        metadata_fields = [
            "title", "abstract", "authors", "publication_date",
            "keywords", "references"
        ]
        complete_fields = sum(1 for field in metadata_fields if publication.get(field))
        score += (complete_fields / len(metadata_fields)) * 25
        
        return min(100, score)
    
    @staticmethod
    def check_plagiarism(text: str, threshold: float = 0.8) -> Dict:
        """
        بررسی سرقت ادبی
        (نیاز به اتصال به سرویس‌هایی مانند Turnitin یا iThenticate)
        """
        # پیاده‌سازی ساده با hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        
        # در عمل باید به پایگاه داده متون متصل شود
        return {
            "similarity_score": 0.0,  # باید از سرویس خارجی دریافت شود
            "matched_sources": [],
            "is_plagiarized": False,
        }
    
    @staticmethod
    def validate_references(references: List[Dict]) -> Dict:
        """اعتبارسنجی منابع"""
        valid_count = 0
        invalid_count = 0
        missing_doi = 0
        
        for ref in references:
            if ref.get("doi"):
                valid_count += 1
            else:
                missing_doi += 1
                invalid_count += 1
        
        return {
            "total_references": len(references),
            "valid_with_doi": valid_count,
            "missing_doi": missing_doi,
            "validity_rate": valid_count / len(references) if references else 0,
        }


# ============================================================
# Text & Voice Processing Service
# ============================================================
class TextVoiceProcessor:
    """پردازش متنی و صوتی برای کارگاه‌های کتابخوانی"""
    
    @staticmethod
    async def extract_text_from_pdf(pdf_url: str) -> str:
        """استخراج متن از PDF"""
        # استفاده از PyPDF2 یا pdfplumber
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(pdf_url, timeout=60)
                if response.status_code == 200:
                    # پردازش PDF
                    # (نیاز به کتابخانه‌های مناسب دارد)
                    return "Extracted text content..."
        except Exception as e:
            print(f"Error extracting text: {e}")
        return ""
    
    @staticmethod
    async def text_to_speech(text: str, language: str = "fa") -> str:
        """تبدیل متن به صوت"""
        # استفاده از سرویس‌های TTS مانند Google TTS یا Azure TTS
        # برای زبان فارسی
        return "audio_file_url.mp3"
    
    @staticmethod
    async def speech_to_text(audio_url: str, language: str = "fa") -> str:
        """تبدیل صوت به متن (برای پیاده‌سازی جلسات)"""
        # استفاده از سرویس‌های STT مانند Google Speech-to-Text
        return "Transcribed text..."
    
    @staticmethod
    def generate_discussion_questions(text: str, num_questions: int = 5) -> List[str]:
        """تولید سؤالات بحث از متن"""
        # استفاده از NLP یا مدل‌های زبانی
        questions = [
            "نکته اصلی این فصل چیست؟",
            "چگونه می‌توان این مفاهیم را در عمل به کار برد؟",
            "چه ارتباطی با موضوعات قبلی دارد؟",
            "نقاط قوت و ضعف روش ارائه‌شده چیست؟",
            "چه سؤالاتی برای تحقیقات آینده پیشنهاد می‌شود؟",
        ]
        return questions[:num_questions]
    
    @staticmethod
    def summarize_text(text: str, max_length: int = 500) -> str:
        """خلاصه‌سازی متن"""
        # استفاده از الگوریتم‌های خلاصه‌سازی
        words = text.split()
        if len(words) <= max_length:
            return text
        return " ".join(words[:max_length]) + "..."


# ============================================================
# Recommendation Engine
# ============================================================
class RecommendationEngine:
    """موتور پیشنهاد منابع"""
    
    @staticmethod
    def recommend_by_similarity(publication_id: int, user_interests: List[str]) -> List[int]:
        """پیشنهاد منابع مشابه بر اساس علاقه‌مندی‌ها"""
        # پیاده‌سازی با Collaborative Filtering یا Content-Based Filtering
        return []
    
    @staticmethod
    def recommend_trending(area: str, limit: int = 10) -> List[int]:
        """پیشنهاد منابع پرطرفدار در حوزه خاص"""
        # بر اساس تعداد دانلود، مشاهده، استناد
        return []
    
    @staticmethod
    def recommend_for_user(user_id: int, limit: int = 20) -> List[int]:
        """پیشنهاد شخصی‌سازی‌شده برای کاربر"""
        # بر اساس تاریخچه مطالعه، علاقه‌مندی‌ها، همکاران
        return []


# ============================================================
# Statistics & Analytics
# ============================================================
class LibraryAnalytics:
    """تحلیل‌های کتابخانه"""
    
    @staticmethod
    def calculate_h_index(publications: List[Dict]) -> int:
        """محاسبه شاخص h"""
        citations = sorted([p.get("citation_count", 0) for p in publications], reverse=True)
        h_index = 0
        for i, c in enumerate(citations, 1):
            if c >= i:
                h_index = i
            else:
                break
        return h_index
    
    @staticmethod
    def calculate_i10_index(publications: List[Dict]) -> int:
        """محاسبه شاخص i10 (تعداد مقالات با حداقل ۱۰ استناد)"""
        return sum(1 for p in publications if p.get("citation_count", 0) >= 10)
    
    @staticmethod
    def generate_impact_report(user_id: int) -> Dict:
        """تولید گزارش تأثیر پژوهشی"""
        # جمع‌آوری آمار
        return {
            "total_publications": 0,
            "total_citations": 0,
            "h_index": 0,
            "i10_index": 0,
            "most_cited_paper": None,
            "recent_activity": [],
        }