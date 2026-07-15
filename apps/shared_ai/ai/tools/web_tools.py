from langchain_core.tools import tool
from typing import List, Dict, Any
import logging
import httpx

logger = logging.getLogger(__name__)

# ==========================================
# Web Search Tool
# ==========================================
@tool
async def web_search(query: str, max_results: int = 5) -> str:
    """
    جستجو در وب برای یافتن اطلاعات مرتبط.
    
    Args:
        query: عبارت جستجو
        max_results: حداکثر تعداد نتایج (پیش‌فرض: 5)
    
    Returns:
        نتایج جستجو به صورت متنی شامل عنوان، لینک و خلاصه
    """
    logger.info(f"🔍 Searching web for: {query}")
    
    try:
        # تلاش برای استفاده از DuckDuckGo
        from langchain_community.tools import DuckDuckGoSearchResults
        
        search = DuckDuckGoSearchResults(
            num_results=max_results,
            output_format="list"
        )
        
        results = await search.ainvoke(query)
        
        if not results:
            return "❌ هیچ نتیجه‌ای یافت نشد."
        
        output = [f"🔎 نتایج جستجو برای: {query}\n"]
        output.append(f"📊 تعداد نتایج: {len(results)}\n")
        
        for i, result in enumerate(results[:max_results], 1):
            title = result.get('title', 'بدون عنوان')
            link = result.get('link', '')
            snippet = result.get('snippet', 'بدون خلاصه')
            
            output.append(f"{i}. {title}")
            output.append(f"   🔗 {link}")
            output.append(f"   📝 {snippet}")
            output.append("")
        
        return "\n".join(output)
    
    except ImportError:
        logger.warning("⚠️ DuckDuckGo not available, using fallback")
        return await _fallback_search(query, max_results)
    
    except Exception as e:
        logger.error(f"❌ Search error: {e}")
        return f"❌ خطا در جستجو: {str(e)}"

async def _fallback_search(query: str, max_results: int) -> str:
    """جستجوی fallback بدون نیاز به کتابخانه خارجی."""
    try:
        # استفاده از Wikipedia API به عنوان fallback
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "format": "json",
                    "srlimit": max_results
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("query", {}).get("search", [])
                
                if not results:
                    return "❌ هیچ نتیجه‌ای یافت نشد."
                
                output = [f"🔎 نتایج جستجو (Wikipedia) برای: {query}\n"]
                output.append(f"📊 تعداد نتایج: {len(results)}\n")
                
                for i, result in enumerate(results[:max_results], 1):
                    title = result.get('title', 'بدون عنوان')
                    snippet = result.get('snippet', 'بدون خلاصه')
                    page_id = result.get('pageid', '')
                    link = f"https://en.wikipedia.org/wiki?curid={page_id}"
                    
                    # حذف HTML tags از snippet
                    import re
                    snippet = re.sub(r'<[^>]+>', '', snippet)
                    
                    output.append(f"{i}. {title}")
                    output.append(f"   🔗 {link}")
                    output.append(f"   📝 {snippet}")
                    output.append("")
                
                return "\n".join(output)
            else:
                return "❌ خطا در جستجو"
    
    except Exception as e:
        logger.error(f"❌ Fallback search error: {e}")
        return f"❌ خطا در جستجو: {str(e)}"

# ==========================================
# Document Summarization Tool
# ==========================================
@tool
async def summarize_text(text: str, max_length: int = 500) -> str:
    """
    خلاصه‌سازی یک متن طولانی.
    
    Args:
        text: متن ورودی برای خلاصه‌سازی
        max_length: حداکثر طول خلاصه (پیش‌فرض: 500 کاراکتر)
    
    Returns:
        خلاصه متن
    """
    logger.info(f"📝 Summarizing text ({len(text)} chars)")
    
    try:
        # اگر متن کوتاه است، همان را برگردان
        if len(text) <= max_length:
            return text
        
        # خلاصه‌سازی ساده: استخراج جملات اول
        sentences = text.replace('\n', ' ').split('.')
        summary = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            if current_length + len(sentence) > max_length:
                break
            
            summary.append(sentence)
            current_length += len(sentence)
        
        result = '. '.join(summary) + '.'
        logger.info(f"✅ Summary created ({len(result)} chars)")
        
        return result
    
    except Exception as e:
        logger.error(f"❌ Summarization error: {e}")
        return f"❌ خطا در خلاصه‌سازی: {str(e)}"

# ==========================================
# Key Points Extraction Tool
# ==========================================
@tool
async def extract_key_points(text: str, num_points: int = 5) -> str:
    """
    استخراج نکات کلیدی از یک متن.
    
    Args:
        text: متن ورودی
        num_points: تعداد نکات کلیدی (پیش‌فرض: 5)
    
    Returns:
        لیست نکات کلیدی
    """
    logger.info(f"🔑 Extracting key points from text ({len(text)} chars)")
    
    try:
        # تقسیم متن به جملات
        sentences = text.replace('\n', ' ').split('.')
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if not sentences:
            return "❌ متن کافی برای استخراج نکات کلیدی وجود ندارد."
        
        # انتخاب جملات با بیشترین کلمات کلیدی
        keywords = ['مهم', 'کلیدی', 'اصلی', 'نتیجه', 'یافته', 'نشان', 'اثبات', 'تحلیل']
        
        scored_sentences = []
        for sentence in sentences:
            score = sum(1 for keyword in keywords if keyword in sentence)
            score += len(sentence) / 100  # طول جمله
            scored_sentences.append((score, sentence))
        
        # مرتب‌سازی بر اساس امتیاز
        scored_sentences.sort(reverse=True, key=lambda x: x[0])
        
        # استخراج نکات برتر
        key_points = [sentence for _, sentence in scored_sentences[:num_points]]
        
        output = [f"🔑 نکات کلیدی ({len(key_points)} مورد):\n"]
        for i, point in enumerate(key_points, 1):
            output.append(f"{i}. {point}")
        
        result = "\n".join(output)
        logger.info(f"✅ Extracted {len(key_points)} key points")
        
        return result
    
    except Exception as e:
        logger.error(f"❌ Key points extraction error: {e}")
        return f"❌ خطا در استخراج نکات کلیدی: {str(e)}"

# ==========================================
# URL Content Fetcher
# ==========================================
@tool
async def fetch_url_content(url: str) -> str:
    """
    دریافت محتوای متنی از یک URL.
    
    Args:
        url: آدرس وب‌سایت
    
    Returns:
        محتوای متنی صفحه
    """
    logger.info(f"🌐 Fetching content from: {url}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Research Agent)"},
                timeout=15.0
            )
            
            if response.status_code == 200:
                # استخراج متن از HTML (ساده)
                import re
                html = response.text
                
                # حذف script و style tags
                html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
                html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
                
                # حذف HTML tags
                text = re.sub(r'<[^>]+>', ' ', html)
                
                # حذف فاصله‌های اضافی
                text = re.sub(r'\s+', ' ', text).strip()
                
                # محدود کردن طول
                if len(text) > 5000:
                    text = text[:5000] + "..."
                
                logger.info(f"✅ Content fetched ({len(text)} chars)")
                return text
            else:
                return f"❌ خطا در دریافت محتوا: HTTP {response.status_code}"
    
    except Exception as e:
        logger.error(f"❌ URL fetch error: {e}")
        return f"❌ خطا در دریافت محتوا: {str(e)}"