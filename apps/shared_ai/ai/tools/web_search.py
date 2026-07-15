from langchain_core.tools import tool
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

@tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    جستجو در وب با استفاده از DuckDuckGo.
    
    Args:
        query: عبارت جستجو
        max_results: حداکثر تعداد نتایج (پیش‌فرض: 5)
    
    Returns:
        نتایج جستجو به صورت متنی ساختاریافته
    """
    try:
        from duckduckgo_search import DDGS
        
        logger.info(f"🔍 Searching web for: {query}")
        
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        
        if not results:
            return "❌ هیچ نتیجه‌ای یافت نشد."
        
        output = [f"🔍 نتایج جستجو برای: {query}\n"]
        output.append(f"📊 تعداد نتایج: {len(results)}\n")
        
        for i, result in enumerate(results, 1):
            title = result.get('title', 'بدون عنوان')
            href = result.get('href', '')
            body = result.get('body', 'بدون توضیحات')
            
            output.append(f"\n{'='*60}")
            output.append(f"📄 نتیجه {i}:")
            output.append(f"📌 عنوان: {title}")
            output.append(f"🔗 لینک: {href}")
            output.append(f"📝 خلاصه: {body}")
        
        output.append(f"\n{'='*60}")
        
        return "\n".join(output)
    
    except ImportError:
        logger.error("❌ duckduckgo-search package not installed")
        return "❌ خطا: پکیج duckduckgo-search نصب نیست. دستور 'pip install duckduckgo-search' را اجرا کنید."
    except Exception as e:
        logger.error(f"❌ Web search error: {e}")
        return f"❌ خطا در جستجو: {str(e)}"

@tool
def web_news_search(query: str, max_results: int = 5) -> str:
    """
    جستجوی اخبار در وب با استفاده از DuckDuckGo.
    
    Args:
        query: عبارت جستجو
        max_results: حداکثر تعداد نتایج (پیش‌فرض: 5)
    
    Returns:
        نتایج جستجوی اخبار به صورت متنی ساختاریافته
    """
    try:
        from duckduckgo_search import DDGS
        
        logger.info(f"📰 Searching news for: {query}")
        
        with DDGS() as ddgs:
            results = list(ddgs.news(query, max_results=max_results))
        
        if not results:
            return "❌ هیچ خبری یافت نشد."
        
        output = [f"📰 نتایج جستجوی اخبار برای: {query}\n"]
        output.append(f"📊 تعداد اخبار: {len(results)}\n")
        
        for i, result in enumerate(results, 1):
            title = result.get('title', 'بدون عنوان')
            url = result.get('url', '')
            body = result.get('body', 'بدون توضیحات')
            date = result.get('date', 'تاریخ نامشخص')
            source = result.get('source', 'منبع نامشخص')
            
            output.append(f"\n{'='*60}")
            output.append(f"📰 خبر {i}:")
            output.append(f"📌 عنوان: {title}")
            output.append(f"🔗 لینک: {url}")
            output.append(f"📅 تاریخ: {date}")
            output.append(f"📡 منبع: {source}")
            output.append(f"📝 خلاصه: {body}")
        
        output.append(f"\n{'='*60}")
        
        return "\n".join(output)
    
    except ImportError:
        logger.error("❌ duckduckgo-search package not installed")
        return "❌ خطا: پکیج duckduckgo-search نصب نیست."
    except Exception as e:
        logger.error(f"❌ News search error: {e}")
        return f"❌ خطا در جستجوی اخبار: {str(e)}"