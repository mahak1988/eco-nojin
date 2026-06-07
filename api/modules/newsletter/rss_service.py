# api/modules/newsletter/rss_service.py
"""
سرویس خواندن RSS feeds از منابع معتبر جهانی و ملی
بدون نیاز به ذخیره‌سازی محلی - فقط لینک‌ها را جمع‌آوری می‌کند
"""
import feedparser
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict
import aiohttp


class RSSNewsAggregator:
    """جمع‌آوری اخبار از منابع RSS"""

    # منابع معتبر جهانی و ملی (۲۵ منبع)
    NEWS_SOURCES = [
        # ==========================================
        # منابع معتبر ملی ایران (۱۰ منبع)
        # ==========================================
        {
            "name": "خبرگزاری ایرنا - کشاورزی",
            "name_en": "IRNA Agriculture",
            "rss_url": "https://www.irna.ir/rss/82002",
            "website": "https://www.irna.ir/",
            "category": "agriculture",
            "language": "fa",
            "country": "Iran",
            "logo": "https://www.irna.ir/favicon.ico"
        },
        {
            "name": "خبرگزاری ایرنا - محیط زیست",
            "name_en": "IRNA Environment",
            "rss_url": "https://www.irna.ir/rss/82006",
            "website": "https://www.irna.ir/",
            "category": "environment",
            "language": "fa",
            "country": "Iran",
            "logo": "https://www.irna.ir/favicon.ico"
        },
        {
            "name": "وزارت جهاد کشاورزی",
            "name_en": "Ministry of Agriculture Jihad",
            "rss_url": "https://www.maj.ir/fa/rss",
            "website": "https://www.maj.ir/",
            "category": "agriculture",
            "language": "fa",
            "country": "Iran",
            "logo": "https://www.maj.ir/favicon.ico"
        },
        {
            "name": "سازمان حفاظت محیط زیست",
            "name_en": "Department of Environment Iran",
            "rss_url": "https://www.doe.ir/fa/rss",
            "website": "https://www.doe.ir/",
            "category": "environment",
            "language": "fa",
            "country": "Iran",
            "logo": "https://www.doe.ir/favicon.ico"
        },
        {
            "name": "شرکت مدیریت منابع آب ایران",
            "name_en": "Iran Water Resources Management",
            "rss_url": "https://www.wrm.ir/fa/rss",
            "website": "https://www.wrm.ir/",
            "category": "water",
            "language": "fa",
            "country": "Iran",
            "logo": "https://www.wrm.ir/favicon.ico"
        },
        {
            "name": "سازمان منابع طبیعی و آبخیزداری",
            "name_en": "Forest, Range and Watershed Management",
            "rss_url": "https://www.frw.ir/fa/rss",
            "website": "https://www.frw.ir/",
            "category": "environment",
            "language": "fa",
            "country": "Iran",
            "logo": "https://www.frw.ir/favicon.ico"
        },
        {
            "name": "سازمان تحقیقات کشاورزی (AREEO)",
            "name_en": "Agricultural Research, Education and Extension",
            "rss_url": "https://www.areeo.ac.ir/fa/rss",
            "website": "https://www.areeo.ac.ir/",
            "category": "research",
            "language": "fa",
            "country": "Iran",
            "logo": "https://www.areeo.ac.ir/favicon.ico"
        },
        {
            "name": "سازمان هواشناسی کشور",
            "name_en": "Iran Meteorological Organization",
            "rss_url": "https://www.irimo.ir/fa/rss",
            "website": "https://www.irimo.ir/",
            "category": "climate",
            "language": "fa",
            "country": "Iran",
            "logo": "https://www.irimo.ir/favicon.ico"
        },
        {
            "name": "خبرگزاری ایسنا",
            "name_en": "ISNA",
            "rss_url": "https://www.isna.ir/rss",
            "website": "https://www.isna.ir/",
            "category": "development",
            "language": "fa",
            "country": "Iran",
            "logo": "https://www.isna.ir/favicon.ico"
        },
        {
            "name": "خبرگزاری مهر",
            "name_en": "Mehr News",
            "rss_url": "https://www.mehrnews.com/rss",
            "website": "https://www.mehrnews.com/",
            "category": "agriculture",
            "language": "fa",
            "country": "Iran",
            "logo": "https://www.mehrnews.com/favicon.ico"
        },
        # ==========================================
        # منابع معتبر بین‌المللی (۱۵ منبع)
        # ==========================================
        {
            "name": "FAO News",
            "name_en": "FAO News",
            "rss_url": "http://www.fao.org/news/rss-feed-en.xml",
            "website": "http://www.fao.org/news/news-detail/en/",
            "category": "agriculture",
            "language": "en",
            "country": "International",
            "logo": "https://www.fao.org/fileadmin/templates/faoweb/images/FAO.gif"
        },
        {
            "name": "UNCCD News",
            "name_en": "UN Convention to Combat Desertification",
            "rss_url": "https://www.unccd.int/news/rss.xml",
            "website": "https://www.unccd.int/news",
            "category": "environment",
            "language": "en",
            "country": "International",
            "logo": "https://www.unccd.int/themes/custom/unccd/logo.svg"
        },
        {
            "name": "NASA Earth Observatory",
            "name_en": "NASA Earth Observatory",
            "rss_url": "https://earthobservatory.nasa.gov/feeds/earth-observatory.rss",
            "website": "https://earthobservatory.nasa.gov/",
            "category": "climate",
            "language": "en",
            "country": "USA",
            "logo": "https://earthobservatory.nasa.gov/favicon.ico"
        },
        {
            "name": "Nature Sustainability",
            "name_en": "Nature Sustainability",
            "rss_url": "http://feeds.nature.com/natsustain",
            "website": "https://www.nature.com/natsustain/",
            "category": "research",
            "language": "en",
            "country": "International",
            "logo": "https://www.nature.com/nature-portfolio-assets/global/nature-brand/safari-pinned-tab.svg"
        },
        {
            "name": "The Guardian Environment",
            "name_en": "The Guardian Environment",
            "rss_url": "https://www.theguardian.com/environment/rss",
            "website": "https://www.theguardian.com/environment",
            "category": "environment",
            "language": "en",
            "country": "UK",
            "logo": "https://assets.guim.co.uk/images/favicons/74d410f87c584d5f8e6e52f2a14e27a2/32x32.ico"
        },
        {
            "name": "Reuters Environment",
            "name_en": "Reuters Environment",
            "rss_url": "https://www.reuters.com/technology/environment/rss",
            "website": "https://www.reuters.com/technology/environment/",
            "category": "environment",
            "language": "en",
            "country": "International",
            "logo": "https://www.reuters.com/pf/resources/images/reuters/favicon/tr_fvcn_kinesis_32x32_v2.ico"
        },
        {
            "name": "CGIAR",
            "name_en": "CGIAR Research",
            "rss_url": "https://www.cgiar.org/feed/",
            "website": "https://www.cgiar.org/",
            "category": "agriculture",
            "language": "en",
            "country": "International",
            "logo": "https://www.cgiar.org/wp-content/themes/cgiar/assets/images/favicon.ico"
        },
        {
            "name": "World Resources Institute",
            "name_en": "World Resources Institute",
            "rss_url": "https://www.wri.org/rss.xml",
            "website": "https://www.wri.org/",
            "category": "environment",
            "language": "en",
            "country": "USA",
            "logo": "https://www.wri.org/themes/custom/wri_theme/favicon.ico"
        },
        {
            "name": "IUCN",
            "name_en": "International Union for Conservation of Nature",
            "rss_url": "https://www.iucn.org/news/feed",
            "website": "https://www.iucn.org/",
            "category": "environment",
            "language": "en",
            "country": "International",
            "logo": "https://www.iucn.org/themes/custom/iucn_theme/favicon.ico"
        },
        {
            "name": "IPCC Reports",
            "name_en": "Intergovernmental Panel on Climate Change",
            "rss_url": "https://www.ipcc.ch/feed/",
            "website": "https://www.ipcc.ch/",
            "category": "climate",
            "language": "en",
            "country": "International",
            "logo": "https://www.ipcc.ch/site/assets/uploads/2019/08/ipcc_logo.png"
        },
        {
            "name": "Devex",
            "name_en": "Devex - International Development",
            "rss_url": "https://www.devex.com/en/articles.rss",
            "website": "https://www.devex.com/",
            "category": "development",
            "language": "en",
            "country": "International",
            "logo": "https://www.devex.com/favicon.ico"
        },
        {
            "name": "World Bank Agriculture",
            "name_en": "World Bank Agriculture",
            "rss_url": "https://www.worldbank.org/en/topic/agriculture/rss",
            "website": "https://www.worldbank.org/en/topic/agriculture",
            "category": "agriculture",
            "language": "en",
            "country": "International",
            "logo": "https://www.worldbank.org/favicon.ico"
        },
        {
            "name": "UN Environment Programme",
            "name_en": "UN Environment Programme",
            "rss_url": "https://www.unep.org/news-and-stories/rss.xml",
            "website": "https://www.unep.org/",
            "category": "environment",
            "language": "en",
            "country": "International",
            "logo": "https://www.unep.org/themes/custom/unep/favicon.ico"
        },
        {
            "name": "Climate Change News",
            "name_en": "Climate Change News",
            "rss_url": "https://www.climatechangenews.com/feed/",
            "website": "https://www.climatechangenews.com/",
            "category": "climate",
            "language": "en",
            "country": "UK",
            "logo": "https://www.climatechangenews.com/favicon.ico"
        },
        {
            "name": "Agriculture.com",
            "name_en": "Successful Farming",
            "rss_url": "https://www.agriculture.com/rss/latest",
            "website": "https://www.agriculture.com/",
            "category": "agriculture",
            "language": "en",
            "country": "USA",
            "logo": "https://www.agriculture.com/favicon.ico"
        }
    ]

    @classmethod
    async def fetch_rss_feed(cls, source: Dict, max_items: int = 10) -> List[Dict]:
        """خواندن یک RSS feed"""
        try:
            feed = feedparser.parse(source["rss_url"])

            articles = []
            for entry in feed.entries[:max_items]:
                article = {
                    "title": entry.get("title", ""),
                    "title_en": entry.get("title", ""),
                    "summary": entry.get("summary", ""),
                    "url": entry.get("link", ""),
                    "published_at": entry.get("published", ""),
                    "author": entry.get("author", ""),
                    "image_url": cls._extract_image(entry),
                    "source_name": source["name"],
                    "source_logo": source.get("logo", ""),
                    "category": source["category"],
                    "language": source["language"],
                }
                articles.append(article)

            return articles
        except Exception as e:
            print(f"Error fetching {source['name']}: {e}")
            return []

    @staticmethod
    def _extract_image(entry) -> str:
        """استخراج تصویر از entry"""
        if hasattr(entry, "media_content") and entry.media_content:
            for media in entry.media_content:
                if "image" in media.get("type", ""):
                    return media.get("url", "")

        if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
            return entry.media_thumbnail[0].get("url", "")

        if hasattr(entry, "enclosures") and entry.enclosures:
            for enclosure in entry.enclosures:
                if "image" in enclosure.get("type", ""):
                    return enclosure.get("href", "")

        return ""

    @classmethod
    async def fetch_all_news(cls, category: str = None, limit: int = 50) -> List[Dict]:
        """دریافت اخبار از تمام منابع"""
        sources = cls.NEWS_SOURCES

        if category:
            sources = [s for s in sources if s["category"] == category]

        tasks = [cls.fetch_rss_feed(source, max_items=10) for source in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_articles = []
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)

        all_articles.sort(key=lambda x: x.get("published_at", ""), reverse=True)

        return all_articles[:limit]

    @classmethod
    def get_sources(cls, category: str = None) -> List[Dict]:
        """دریافت لیست منابع"""
        sources = cls.NEWS_SOURCES

        if category:
            sources = [s for s in sources if s["category"] == category]

        return sources
