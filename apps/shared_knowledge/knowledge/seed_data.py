"""seed_data module."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from apps.shared_knowledge.knowledge.models import (
    KnowledgeArticle,
    BusinessRule,
    ResponseTemplate
)

logger = logging.getLogger(__name__)


# ==========================================
# ط¯ط§ظ†ط´â€Œظ†ط§ظ…ظ‡ ط§غŒط¬ظ†طھ ظ…ط§ظ„غŒ
# ==========================================
FINANCIAL_KNOWLEDGE = [
    {
        "agent_type": "financial",
        "category": "ط§طµظˆظ„ طھط­ظ„غŒظ„",
        "title": "ظ†ط³ط¨طھâ€Œظ‡ط§غŒ ظ…ط§ظ„غŒ ع©ظ„غŒط¯غŒ",
        "content": """
ظ†ط³ط¨طھâ€Œظ‡ط§غŒ ظ…ط§ظ„غŒ ظ…ظ‡ظ… ط¨ط±ط§غŒ طھط­ظ„غŒظ„:

1. ظ†ط³ط¨طھ ظ†ظ‚ط¯غŒظ†ع¯غŒ (Liquidity Ratio):
   - ظ†ط³ط¨طھ ط¬ط§ط±غŒ = ط¯ط§ط±ط§غŒغŒâ€Œظ‡ط§غŒ ط¬ط§ط±غŒ / ط¨ط¯ظ‡غŒâ€Œظ‡ط§غŒ ط¬ط§ط±غŒ
   - ظ†ط³ط¨طھ ط³ط±غŒط¹ = (ط¯ط§ط±ط§غŒغŒâ€Œظ‡ط§غŒ ط¬ط§ط±غŒ - ظ…ظˆط¬ظˆط¯غŒ ع©ط§ظ„ط§) / ط¨ط¯ظ‡غŒâ€Œظ‡ط§غŒ ط¬ط§ط±غŒ
   
2. ظ†ط³ط¨طھ ط§ظ‡ط±ظ…غŒ (Leverage Ratio):
   - ظ†ط³ط¨طھ ط¨ط¯ظ‡غŒ = ع©ظ„ ط¨ط¯ظ‡غŒâ€Œظ‡ط§ / ع©ظ„ ط¯ط§ط±ط§غŒغŒâ€Œظ‡ط§
   - ظ¾ظˆط´ط´ ط¨ظ‡ط±ظ‡ = EBIT / ظ‡ط²غŒظ†ظ‡ ط¨ظ‡ط±ظ‡
   
3. ظ†ط³ط¨طھ ط³ظˆط¯ط¢ظˆط±غŒ (Profitability Ratio):
   - ط­ط§ط´غŒظ‡ ط³ظˆط¯ ط®ط§ظ„طµ = ط³ظˆط¯ ط®ط§ظ„طµ / ط¯ط±ط¢ظ…ط¯
   - ROE = ط³ظˆط¯ ط®ط§ظ„طµ / ط­ظ‚ظˆظ‚ طµط§ط­ط¨ط§ظ† ط³ظ‡ط§ظ…
   - ROA = ط³ظˆط¯ ط®ط§ظ„طµ / ع©ظ„ ط¯ط§ط±ط§غŒغŒâ€Œظ‡ط§
   
4. ظ†ط³ط¨طھ ع©ط§ط±ط§غŒغŒ (Efficiency Ratio):
   - ع¯ط±ط¯ط´ ظ…ظˆط¬ظˆط¯غŒ ع©ط§ظ„ط§ = ط¨ظ‡ط§غŒ طھظ…ط§ظ… ط´ط¯ظ‡ ع©ط§ظ„ط§غŒ ظپط±ظˆط´ ط±ظپطھظ‡ / ظ…غŒط§ظ†ع¯غŒظ† ظ…ظˆط¬ظˆط¯غŒ
   - ط¯ظˆط±ظ‡ ظˆطµظˆظ„ ظ…ط·ط§ظ„ط¨ط§طھ = (ظ…غŒط§ظ†ع¯غŒظ† ط­ط³ط§ط¨â€Œظ‡ط§غŒ ط¯ط±غŒط§ظپطھظ†غŒ / ظپط±ظˆط´ ط§ط¹طھط¨ط§ط±غŒ) أ— 365
""",
        "keywords": "ظ†ط³ط¨طھ ظ…ط§ظ„غŒ, ظ†ظ‚ط¯غŒظ†ع¯غŒ, ط§ظ‡ط±ظ…غŒ, ط³ظˆط¯ط¢ظˆط±غŒ, ع©ط§ط±ط§غŒغŒ, ROE, ROA",
        "priority": 10
    },
    {
        "agent_type": "financial",
        "category": "طھط­ظ„غŒظ„ طھع©ظ†غŒع©ط§ظ„",
        "title": "ط§ظ†ط¯غŒع©ط§طھظˆط±ظ‡ط§غŒ طھع©ظ†غŒع©ط§ظ„ ظ¾ط±ع©ط§ط±ط¨ط±ط¯",
        "content": """
ط§ظ†ط¯غŒع©ط§طھظˆط±ظ‡ط§غŒ ظ…ظ‡ظ… طھط­ظ„غŒظ„ طھع©ظ†غŒع©ط§ظ„:

1. ظ…غŒط§ظ†ع¯غŒظ† ظ…طھط­ط±ع© (Moving Average):
   - SMA: ظ…غŒط§ظ†ع¯غŒظ† ط³ط§ط¯ظ‡
   - EMA: ظ…غŒط§ظ†ع¯غŒظ† ظ†ظ…ط§غŒغŒ (ظˆط§ع©ظ†ط´ ط³ط±غŒط¹â€Œطھط±)
   
2. RSI (Relative Strength Index):
   - ط¨ط§ظ„ط§غŒ 70: ط§ط´ط¨ط§ط¹ ط®ط±غŒط¯
   - ط²غŒط± 30: ط§ط´ط¨ط§ط¹ ظپط±ظˆط´
   
3. MACD:
   - طھظ‚ط§ط·ط¹ ط®ط· ط³غŒع¯ظ†ط§ظ„: ط³غŒع¯ظ†ط§ظ„ ط®ط±غŒط¯/ظپط±ظˆط´
   - ظˆط§ع¯ط±ط§غŒغŒ: طھط؛غŒغŒط± ط±ظˆظ†ط¯
   
4. Bollinger Bands:
   - ط¨ط§ظ†ط¯ ط¨ط§ظ„ط§ ظˆ ظ¾ط§غŒغŒظ†: ظ†ظˆط³ط§ظ†ط§طھ
   - ظپط´ط±ط¯ع¯غŒ: ط§ط­طھظ…ط§ظ„ ط­ط±ع©طھ ط¨ط²ط±ع¯
""",
        "keywords": "طھع©ظ†غŒع©ط§ظ„, RSI, MACD, ظ…غŒط§ظ†ع¯غŒظ† ظ…طھط­ط±ع©, Bollinger",
        "priority": 9
    },
    {
        "agent_type": "financial",
        "category": "ظ…ط¯غŒط±غŒطھ ط±غŒط³ع©",
        "title": "ط§طµظˆظ„ ظ…ط¯غŒط±غŒطھ ط±غŒط³ع©",
        "content": """
ط§طµظˆظ„ ظ…ط¯غŒط±غŒطھ ط±غŒط³ع© ط¯ط± ط³ط±ظ…ط§غŒظ‡â€Œع¯ط°ط§ط±غŒ:

1. طھظ†ظˆط¹â€Œط¨ط®ط´غŒ (Diversification):
   - ط¹ط¯ظ… طھظ…ط±ع©ط² ط¯ط± غŒع© ط¯ط§ط±ط§غŒغŒ
   - طھظˆط²غŒط¹ ط¨غŒظ† طµظ†ط§غŒط¹ ظ…ط®طھظ„ظپ
   
2. ط­ط¯ ط¶ط±ط± (Stop Loss):
   - طھط¹غŒغŒظ† ط­ط¯ ط¶ط±ط± ظ‚ط¨ظ„ ط§ط² ظˆط±ظˆط¯
   - ظ…ط¹ظ…ظˆظ„ط§ظ‹ 2-5% ط§ط² ظ‚غŒظ…طھ ظˆط±ظˆط¯
   
3. ط§ظ†ط¯ط§ط²ظ‡ ظ¾ظˆط²غŒط´ظ†:
   - ط­ط¯ط§ع©ط«ط± 2% ط³ط±ظ…ط§غŒظ‡ ط¯ط± ظ‡ط± ظ…ط¹ط§ظ…ظ„ظ‡
   - ط±غŒط³ع© ط¨ظ‡ ط±غŒظˆط§ط±ط¯ ط­ط¯ط§ظ‚ظ„ 1:2
   
4. ظ‡ظ…ط¨ط³طھع¯غŒ (Correlation):
   - ط¯ط§ط±ط§غŒغŒâ€Œظ‡ط§غŒ ط¨ط§ ظ‡ظ…ط¨ط³طھع¯غŒ ظ…ظ†ظپغŒ
   - ع©ط§ظ‡ط´ ط±غŒط³ع© ع©ظ„غŒ ظ¾ظˆط±طھظپظˆغŒ
""",
        "keywords": "ط±غŒط³ع©, طھظ†ظˆط¹, ط­ط¯ ط¶ط±ط±, ظ¾ظˆط²غŒط´ظ†, ظ‡ظ…ط¨ط³طھع¯غŒ",
        "priority": 8
    }
]

# ==========================================
# ط¯ط§ظ†ط´â€Œظ†ط§ظ…ظ‡ ط§غŒط¬ظ†طھ ظ¾ط´طھغŒط¨ط§ظ†غŒ
# ==========================================
SUPPORT_KNOWLEDGE = [
    {
        "agent_type": "support",
        "category": "FAQ",
        "title": "ط³ظˆط§ظ„ط§طھ ظ…طھط¯ط§ظˆظ„ - ط§ط­ط±ط§ط² ظ‡ظˆغŒطھ",
        "content": """
ط³ظˆط§ظ„ط§طھ ظ…طھط¯ط§ظˆظ„ ط¯ط±ط¨ط§ط±ظ‡ ط§ط­ط±ط§ط² ظ‡ظˆغŒطھ:

1. ظپط±ط§ظ…ظˆط´غŒ ط±ظ…ط² ط¹ط¨ظˆط±:
   - ع©ظ„غŒع© ط±ظˆغŒ "ظپط±ط§ظ…ظˆط´غŒ ط±ظ…ط²"
   - ظˆط§ط±ط¯ ع©ط±ط¯ظ† ط§غŒظ…غŒظ„
   - ط¨ط±ط±ط³غŒ ط§غŒظ…غŒظ„ ظˆ ع©ظ„غŒع© ط±ظˆغŒ ظ„غŒظ†ع©
   - طھظ†ط¸غŒظ… ط±ظ…ط² ط¬ط¯غŒط¯
   
2. طھط؛غŒغŒط± ط§غŒظ…غŒظ„:
   - ظˆط±ظˆط¯ ط¨ظ‡ طھظ†ط¸غŒظ…ط§طھ ظ¾ط±ظˆظپط§غŒظ„
   - ع©ظ„غŒع© ط±ظˆغŒ "ظˆغŒط±ط§غŒط´ ط§غŒظ…غŒظ„"
   - طھط§غŒغŒط¯ ط§غŒظ…غŒظ„ ط¬ط¯غŒط¯
   
3. ظپط¹ط§ظ„â€Œط³ط§ط²غŒ ط¯ظˆ ظ…ط±ط­ظ„ظ‡â€Œط§غŒ:
   - طھظ†ط¸غŒظ…ط§طھ > ط§ظ…ظ†غŒطھ
   - ظپط¹ط§ظ„â€Œط³ط§ط²غŒ 2FA
   - ط§ط³ع©ظ† QR ط¨ط§ Google Authenticator
""",
        "keywords": "ط§ط­ط±ط§ط² ظ‡ظˆغŒطھ, ط±ظ…ط² ط¹ط¨ظˆط±, ط§غŒظ…غŒظ„, 2FA, ط§ظ…ظ†غŒطھ",
        "priority": 10
    },
    {
        "agent_type": "support",
        "category": "ط±ط§ظ‡ظ†ظ…ط§",
        "title": "ط±ط§ظ‡ظ†ظ…ط§غŒ ط§ط³طھظپط§ط¯ظ‡ ط§ط² ط§غŒط¬ظ†طھâ€Œظ‡ط§",
        "content": """
ط±ط§ظ‡ظ†ظ…ط§غŒ ط§ط³طھظپط§ط¯ظ‡ ط§ط² ط§غŒط¬ظ†طھâ€Œظ‡ط§غŒ Econojin:

1. ط§ظ†طھط®ط§ط¨ ط§غŒط¬ظ†طھ ظ…ظ†ط§ط³ط¨:
   - طھط­ظ„غŒظ„ع¯ط± ظ…ط§ظ„غŒ: ط¨ط±ط§غŒ ط³ظˆط§ظ„ط§طھ ظ…ط§ظ„غŒ ظˆ ط³ط±ظ…ط§غŒظ‡â€Œع¯ط°ط§ط±غŒ
   - ظ¾ط´طھغŒط¨ط§ظ†غŒ: ط¨ط±ط§غŒ ظ…ط´ع©ظ„ط§طھ ظپظ†غŒ ظˆ ط±ط§ظ‡ظ†ظ…ط§غŒغŒ
   - ع©ظ…ع© ط§ط¯ظ…غŒظ†: ط¨ط±ط§غŒ ظ…ط¯غŒط±غŒطھ ظ¾ط±ظˆعکظ‡
   - ظ…ط­ظ‚ظ‚: ط¨ط±ط§غŒ طھط­ظ‚غŒظ‚ ظˆ ط¬ظ…ط¹â€Œط¢ظˆط±غŒ ط§ط·ظ„ط§ط¹ط§طھ
   - طھط­ظ„غŒظ„ع¯ط± ط¯ط§ط¯ظ‡: ط¨ط±ط§غŒ طھط­ظ„غŒظ„ ط¢ظ…ط§ط±غŒ
   - ط¯ط³طھغŒط§ط± ع©ط¯ظ†ظˆغŒط³غŒ: ط¨ط±ط§غŒ ع©ظ…ع© ط¯ط± ط¨ط±ظ†ط§ظ…ظ‡â€Œظ†ظˆغŒط³غŒ
   
2. ظ†ط­ظˆظ‡ طھط¹ط§ظ…ظ„:
   - ط³ظˆط§ظ„ ظˆط§ط¶ط­ ظˆ ظ…ط´ط®طµ ط¨ظ¾ط±ط³غŒط¯
   - ط¯ط± طµظˆط±طھ ظ†غŒط§ط²طŒ ط¯ط§ط¯ظ‡â€Œظ‡ط§ ط±ط§ ط§ط±ط§ط¦ظ‡ ط¯ظ‡غŒط¯
   - ط§ط² ط§غŒط¬ظ†طھ ط¨ط®ظˆط§ظ‡غŒط¯ طھظˆط¶غŒط­ ط¯ظ‡ط¯
   
3. ظ†ع©ط§طھ ظ…ظ‡ظ…:
   - ط§غŒط¬ظ†طھâ€Œظ‡ط§ ط¨ط±ط§غŒ ع©ظ…ع© ظ‡ط³طھظ†ط¯طŒ ظ†ظ‡ ط¬ط§غŒع¯ط²غŒظ† طھطµظ…غŒظ…â€Œع¯غŒط±غŒ
   - ظ‡ظ…غŒط´ظ‡ ظ†طھط§غŒط¬ ط±ط§ ط¨ط±ط±ط³غŒ ع©ظ†غŒط¯
   - ط¯ط± ظ…ظˆط§ط±ط¯ ط­ط³ط§ط³طŒ ط¨ط§ ظ…طھط®طµطµ ظ…ط´ظˆط±طھ ع©ظ†غŒط¯
""",
        "keywords": "ط§غŒط¬ظ†طھ, ط±ط§ظ‡ظ†ظ…ط§, ط§ط³طھظپط§ط¯ظ‡, طھط¹ط§ظ…ظ„",
        "priority": 9
    }
]

# ==========================================
# ط¯ط§ظ†ط´â€Œظ†ط§ظ…ظ‡ ط§غŒط¬ظ†طھ ط§ط¯ظ…غŒظ†
# ==========================================
ADMIN_KNOWLEDGE = [
    {
        "agent_type": "admin",
        "category": "ظ…ط¯غŒط±غŒطھ ظ¾ط±ظˆعکظ‡",
        "title": "ظ…طھط¯ظˆظ„ظˆعکغŒâ€Œظ‡ط§غŒ ظ…ط¯غŒط±غŒطھ ظ¾ط±ظˆعکظ‡",
        "content": """
ظ…طھط¯ظˆظ„ظˆعکغŒâ€Œظ‡ط§غŒ ظ…ط¯غŒط±غŒطھ ظ¾ط±ظˆعکظ‡:

1. Agile:
   - Scrum: Sprintظ‡ط§غŒ 2-4 ظ‡ظپطھظ‡â€Œط§غŒ
   - Kanban: ط¬ط±غŒط§ظ† ع©ط§ط± ظ…ط¯ط§ظˆظ…
   - ظ…ظ†ط§ط³ط¨ ط¨ط±ط§غŒ ظ¾ط±ظˆعکظ‡â€Œظ‡ط§غŒ ط¨ط§ ظ†غŒط§ط²ظ‡ط§غŒ ظ…طھط؛غŒط±
   
2. Waterfall:
   - ظ…ط±ط§ط­ظ„ ط®ط·غŒ ظˆ ظ…طھظˆط§ظ„غŒ
   - ظ…ظ†ط§ط³ط¨ ط¨ط±ط§غŒ ظ¾ط±ظˆعکظ‡â€Œظ‡ط§غŒ ط¨ط§ ظ†غŒط§ط²ظ‡ط§غŒ ط«ط§ط¨طھ
   
3. Hybrid:
   - طھط±ع©غŒط¨ Agile ظˆ Waterfall
   - ط§ظ†ط¹ط·ط§ظپâ€Œظ¾ط°غŒط±غŒ ط¨ط§ ط³ط§ط®طھط§ط±
   
4. KPIظ‡ط§غŒ ظ…ظ‡ظ…:
   - Velocity: ط³ط±ط¹طھ طھغŒظ…
   - Burndown: ظ¾غŒط´ط±ظپطھ ع©ط§ط±
   - Cycle Time: ط²ظ…ط§ظ† طھع©ظ…غŒظ„ طھط³ع©
   - Lead Time: ط²ظ…ط§ظ† ط§ط² ط¯ط±ط®ظˆط§ط³طھ طھط§ طھط­ظˆغŒظ„
""",
        "keywords": "ظ…ط¯غŒط±غŒطھ ظ¾ط±ظˆعکظ‡, Agile, Scrum, Kanban, KPI",
        "priority": 10
    },
    {
        "agent_type": "admin",
        "category": "طھطµظ…غŒظ…â€Œع¯غŒط±غŒ",
        "title": "ع†ظ‡ط§ط±ع†ظˆط¨â€Œظ‡ط§غŒ طھطµظ…غŒظ…â€Œع¯غŒط±غŒ",
        "content": """
ع†ظ‡ط§ط±ع†ظˆط¨â€Œظ‡ط§غŒ طھطµظ…غŒظ…â€Œع¯غŒط±غŒ:

1. SWOT Analysis:
   - Strengths: ظ†ظ‚ط§ط· ظ‚ظˆطھ
   - Weaknesses: ظ†ظ‚ط§ط· ط¶ط¹ظپ
   - Opportunities: ظپط±طµطھâ€Œظ‡ط§
   - Threats: طھظ‡ط¯غŒط¯ظ‡ط§
   
2. Decision Matrix:
   - ظ„غŒط³طھ ع¯ط²غŒظ†ظ‡â€Œظ‡ط§
   - ظ…ط¹غŒط§ط±ظ‡ط§غŒ طھطµظ…غŒظ…â€Œع¯غŒط±غŒ
   - ظˆط²ظ†â€Œط¯ظ‡غŒ ط¨ظ‡ ظ…ط¹غŒط§ط±ظ‡ط§
   - ط§ظ…طھغŒط§ط²ط¯ظ‡غŒ ظˆ ط§ظ†طھط®ط§ط¨
   
3. Cost-Benefit Analysis:
   - ظ…ط­ط§ط³ط¨ظ‡ ظ‡ط²غŒظ†ظ‡â€Œظ‡ط§
   - ظ…ط­ط§ط³ط¨ظ‡ ظ…ظ†ط§ظپط¹
   - ظ…ظ‚ط§غŒط³ظ‡ ظˆ طھطµظ…غŒظ…â€Œع¯غŒط±غŒ
   
4. Risk Assessment:
   - ط´ظ†ط§ط³ط§غŒغŒ ط±غŒط³ع©â€Œظ‡ط§
   - ط§ط±ط²غŒط§ط¨غŒ ط§ط­طھظ…ط§ظ„ ظˆ طھط§ط«غŒط±
   - ط¨ط±ظ†ط§ظ…ظ‡â€Œط±غŒط²غŒ ظ¾ط§ط³ط®
""",
        "keywords": "طھطµظ…غŒظ…â€Œع¯غŒط±غŒ, SWOT, Matrix, ط±غŒط³ع©",
        "priority": 9
    }
]

# ==========================================
# ط¯ط§ظ†ط´â€Œظ†ط§ظ…ظ‡ ط§غŒط¬ظ†طھ ظ…ط­ظ‚ظ‚
# ==========================================
RESEARCH_KNOWLEDGE = [
    {
        "agent_type": "research",
        "category": "ظ…طھط¯ظˆظ„ظˆعکغŒ",
        "title": "ط±ظˆط´â€Œظ‡ط§غŒ طھط­ظ‚غŒظ‚ ط¹ظ„ظ…غŒ",
        "content": """
ط±ظˆط´â€Œظ‡ط§غŒ طھط­ظ‚غŒظ‚ ط¹ظ„ظ…غŒ:

1. طھط­ظ‚غŒظ‚ ع©ظ…غŒ (Quantitative):
   - ط¯ط§ط¯ظ‡â€Œظ‡ط§غŒ ط¹ط¯ط¯غŒ
   - طھط­ظ„غŒظ„ ط¢ظ…ط§ط±غŒ
   - ط¢ط²ظ…ظˆظ† ظپط±ط¶غŒظ‡â€Œظ‡ط§
   
2. طھط­ظ‚غŒظ‚ ع©غŒظپغŒ (Qualitative):
   - ظ…طµط§ط­ط¨ظ‡
   - ظ…ط´ط§ظ‡ط¯ظ‡
   - طھط­ظ„غŒظ„ ظ…ط­طھظˆط§
   
3. طھط­ظ‚غŒظ‚ طھط±ع©غŒط¨غŒ (Mixed Methods):
   - طھط±ع©غŒط¨ ع©ظ…غŒ ظˆ ع©غŒظپغŒ
   - ط§ط¹طھط¨ط§ط± ط¨ط§ظ„ط§طھط±
   
4. ظ…ط±ط§ط­ظ„ طھط­ظ‚غŒظ‚:
   - طھط¹ط±غŒظپ ظ…ط³ط¦ظ„ظ‡
   - ظ…ط±ظˆط± ط§ط¯ط¨غŒط§طھ
   - ط·ط±ط§ط­غŒ ط±ظˆط´
   - ط¬ظ…ط¹â€Œط¢ظˆط±غŒ ط¯ط§ط¯ظ‡
   - طھط­ظ„غŒظ„
   - ظ†طھغŒط¬ظ‡â€Œع¯غŒط±غŒ
""",
        "keywords": "طھط­ظ‚غŒظ‚, ظ…طھط¯ظˆظ„ظˆعکغŒ, ع©ظ…غŒ, ع©غŒظپغŒ",
        "priority": 10
    }
]

# ==========================================
# ط¯ط§ظ†ط´â€Œظ†ط§ظ…ظ‡ ط§غŒط¬ظ†طھ طھط­ظ„غŒظ„ع¯ط± ط¯ط§ط¯ظ‡
# ==========================================
DATA_ANALYST_KNOWLEDGE = [
    {
        "agent_type": "data_analyst",
        "category": "ط¢ظ…ط§ط±",
        "title": "ظ…ظپط§ظ‡غŒظ… ط¢ظ…ط§ط±غŒ ظ¾ط§غŒظ‡",
        "content": """
ظ…ظپط§ظ‡غŒظ… ط¢ظ…ط§ط±غŒ ظ¾ط§غŒظ‡:

1. ط¢ظ…ط§ط± طھظˆطµغŒظپغŒ:
   - ظ…غŒط§ظ†ع¯غŒظ† (Mean): ظ…ط¬ظ…ظˆط¹ / طھط¹ط¯ط§ط¯
   - ظ…غŒط§ظ†ظ‡ (Median): ظ…ظ‚ط¯ط§ط± ظˆط³ط·غŒ
   - ظ…ط¯ (Mode): ظ¾ط±طھع©ط±ط§ط±طھط±غŒظ† ظ…ظ‚ط¯ط§ط±
   - ط§ظ†ط­ط±ط§ظپ ظ…ط¹غŒط§ط± (Std): ظ¾ط±ط§ع©ظ†ط¯ع¯غŒ ط¯ط§ط¯ظ‡â€Œظ‡ط§
   
2. ط¢ظ…ط§ط± ط§ط³طھظ†ط¨ط§ط·غŒ:
   - ط¢ط²ظ…ظˆظ† t: ظ…ظ‚ط§غŒط³ظ‡ ط¯ظˆ ع¯ط±ظˆظ‡
   - ANOVA: ظ…ظ‚ط§غŒط³ظ‡ ع†ظ†ط¯ ع¯ط±ظˆظ‡
   - Chi-square: ط¢ط²ظ…ظˆظ† ط§ط³طھظ‚ظ„ط§ظ„
   - Regression: ظ¾غŒط´â€Œط¨غŒظ†غŒ
   
3. ظ…ظپط§ظ‡غŒظ… ظ…ظ‡ظ…:
   - p-value: ط§ط­طھظ…ط§ظ„ ظ…ط´ط§ظ‡ط¯ظ‡ ظ†طھط§غŒط¬ طھطµط§ط¯ظپغŒ
   - Confidence Interval: ط¨ط§ط²ظ‡ ط§ط·ظ…غŒظ†ط§ظ†
   - Power: طھظˆط§ظ† ط¢ط²ظ…ظˆظ†
   - Effect Size: ط§ظ†ط¯ط§ط²ظ‡ ط§ط«ط±
""",
        "keywords": "ط¢ظ…ط§ط±, ظ…غŒط§ظ†ع¯غŒظ†, ظ…غŒط§ظ†ظ‡, ط§ظ†ط­ط±ط§ظپ ظ…ط¹غŒط§ط±, p-value",
        "priority": 10
    },
    {
        "agent_type": "data_analyst",
        "category": "visualization",
        "title": "ط§طµظˆظ„ ظ…طµظˆط±ط³ط§ط²غŒ ط¯ط§ط¯ظ‡",
        "content": """
ط§طµظˆظ„ ظ…طµظˆط±ط³ط§ط²غŒ ط¯ط§ط¯ظ‡:

1. ط§ظ†طھط®ط§ط¨ ظ†ظ…ظˆط¯ط§ط± ظ…ظ†ط§ط³ط¨:
   - Line: ط±ظˆظ†ط¯ ط²ظ…ط§ظ†غŒ
   - Bar: ظ…ظ‚ط§غŒط³ظ‡ ط¯ط³طھظ‡â€Œظ‡ط§
   - Scatter: ط±ط§ط¨ط·ظ‡ ط¯ظˆ ظ…طھط؛غŒط±
   - Histogram: طھظˆط²غŒط¹ ط¯ط§ط¯ظ‡
   - Pie: ظ†ط³ط¨طھ ط§ط¬ط²ط§
   
2. ط§طµظˆظ„ ط·ط±ط§ط­غŒ:
   - ط³ط§ط¯ع¯غŒ ظˆ ظˆط¶ظˆط­
   - ط¨ط±ع†ط³ط¨â€Œع¯ط°ط§ط±غŒ ظ…ظ†ط§ط³ط¨
   - ط§ظ†طھط®ط§ط¨ ط±ظ†ع¯ ظ…ظ†ط§ط³ط¨
   - ط¹ط¯ظ… ط§ط؛ط±ط§ظ‚ ط¯ط± ظ…ظ‚غŒط§ط³
   
3. ط§ط¨ط²ط§ط±ظ‡ط§:
   - Matplotlib: ظ¾ط§غŒظ‡â€Œط§غŒ
   - Seaborn: ط¢ظ…ط§ط±غŒ
   - Plotly: طھط¹ط§ظ…ظ„غŒ
""",
        "keywords": "visualization, ظ†ظ…ظˆط¯ط§ط±, ظ…طµظˆط±ط³ط§ط²غŒ, Matplotlib",
        "priority": 9
    }
]

# ==========================================
# ط¯ط§ظ†ط´â€Œظ†ط§ظ…ظ‡ ط§غŒط¬ظ†طھ ط¯ط³طھغŒط§ط± ع©ط¯ظ†ظˆغŒط³غŒ
# ==========================================
CODE_ASSISTANT_KNOWLEDGE = [
    {
        "agent_type": "code_assistant",
        "category": "Best Practices",
        "title": "ط§طµظˆظ„ ع©ط¯ظ†ظˆغŒط³غŒ طھظ…غŒط²",
        "content": """
ط§طµظˆظ„ ع©ط¯ظ†ظˆغŒط³غŒ طھظ…غŒط² (Clean Code):

1. ظ†ط§ظ…â€Œع¯ط°ط§ط±غŒ:
   - ظ†ط§ظ…â€Œظ‡ط§غŒ ظ…ط¹ظ†ط§ط¯ط§ط± ظˆ طھظˆطµغŒظپغŒ
   - avoid abbreviations
   - functions: verbs
   - variables: nouns
   
2. طھظˆط§ط¨ط¹:
   - ع©ظˆع†ع© ظˆ ظ…طھظ…ط±ع©ط² (SRP)
   - ط­ط¯ط§ع©ط«ط± 20 ط®ط·
   - ط­ط¯ط§ع©ط«ط± 3-4 ظ¾ط§ط±ط§ظ…طھط±
   - ط¨ط¯ظˆظ† ط¹ظˆط§ط±ط¶ ط¬ط§ظ†ط¨غŒ
   
3. ع©ظ„ط§ط³â€Œظ‡ط§:
   - ظ…ط³ط¦ظˆظ„غŒطھ ظˆط§ط­ط¯
   - cohesion ط¨ط§ظ„ط§
   - coupling ظ¾ط§غŒغŒظ†
   
4. ط®ط·ط§ظ‡ط§:
   - ط§ط³طھظپط§ط¯ظ‡ ط§ط² exceptions
   - ظ¾غŒط§ظ…â€Œظ‡ط§غŒ ط®ط·ط§غŒ ظˆط§ط¶ط­
   - logging ظ…ظ†ط§ط³ط¨
""",
        "keywords": "Clean Code, ظ†ط§ظ…â€Œع¯ط°ط§ط±غŒ, طھظˆط§ط¨ط¹, ع©ظ„ط§ط³â€Œظ‡ط§",
        "priority": 10
    },
    {
        "agent_type": "code_assistant",
        "category": "ط§ظ„ع¯ظˆظ‡ط§غŒ ط·ط±ط§ط­غŒ",
        "title": "ط§ظ„ع¯ظˆظ‡ط§غŒ ط·ط±ط§ط­غŒ ط±ط§غŒط¬",
        "content": """
ط§ظ„ع¯ظˆظ‡ط§غŒ ط·ط±ط§ط­غŒ ط±ط§غŒط¬:

1. Creational Patterns:
   - Singleton: غŒع© ظ†ظ…ظˆظ†ظ‡
   - Factory: ط³ط§ط®طھ ط§ط´غŒط§ط،
   - Builder: ط³ط§ط®طھ ع¯ط§ظ…â€Œط¨ظ‡â€Œع¯ط§ظ…
   
2. Structural Patterns:
   - Adapter: طھط·ط¨غŒظ‚ interface
   - Decorator: ط§ظپط²ظˆط¯ظ† ظ‚ط§ط¨ظ„غŒطھ
   - Facade: interface ط³ط§ط¯ظ‡
   
3. Behavioral Patterns:
   - Observer: ط§ط·ظ„ط§ط¹â€Œط±ط³ط§ظ†غŒ طھط؛غŒغŒط±ط§طھ
   - Strategy: ط§ظ„ع¯ظˆط±غŒطھظ…â€Œظ‡ط§غŒ ظ‚ط§ط¨ظ„ طھط¹ظˆغŒط¶
   - Command: encapsulate ط¯ط±ط®ظˆط§ط³طھ
   
4. ط§طµظˆظ„ SOLID:
   - S: Single Responsibility
   - O: Open/Closed
   - L: Liskov Substitution
   - I: Interface Segregation
   - D: Dependency Inversion
""",
        "keywords": "Design Patterns, Singleton, Factory, SOLID",
        "priority": 9
    }
]

# ==========================================
# ظ‚ظˆط§ظ†غŒظ† ع©ط³ط¨â€Œظˆع©ط§ط±
# ==========================================
BUSINESS_RULES = [
    {
        "agent_type": "financial",
        "rule_name": "ظ‡ط´ط¯ط§ط± ط±غŒط³ع© ط¨ط§ظ„ط§",
        "condition": '{"keywords": ["ط±غŒط³ع© ط¨ط§ظ„ط§", "ط³ط±ظ…ط§غŒظ‡â€Œع¯ط°ط§ط±غŒ ظ¾ط±ط®ط·ط±"]}',
        "action": "ظ‡ظ…غŒط´ظ‡ ظ‡ط´ط¯ط§ط± ط±غŒط³ع© ظˆ طھظˆطµغŒظ‡ ظ…ط´ظˆط±طھ ط¨ط§ ظ…طھط®طµطµ ط±ط§ ط§ط±ط§ط¦ظ‡ ط¯ظ‡غŒط¯",
        "priority": 10
    },
    {
        "agent_type": "support",
        "rule_name": "ط§ط±ط¬ط§ط¹ ط¨ظ‡ ظ¾ط´طھغŒط¨ط§ظ†غŒ ط§ظ†ط³ط§ظ†غŒ",
        "condition": '{"keywords": ["ط´ع©ط§غŒطھ", "ظ†ط§ط±ط¶ط§غŒطھغŒ", "ظ…ط´ع©ظ„ ط­ظ„ ظ†ط´ط¯"]}',
        "action": "ط¯ط± طµظˆط±طھ ظ†ط§ط±ط¶ط§غŒطھغŒ ع©ط§ط±ط¨ط±طŒ ط§ط±ط¬ط§ط¹ ط¨ظ‡ ظ¾ط´طھغŒط¨ط§ظ†غŒ ط§ظ†ط³ط§ظ†غŒ ط±ط§ ظ¾غŒط´ظ†ظ‡ط§ط¯ ط¯ظ‡غŒط¯",
        "priority": 10
    },
    {
        "agent_type": "admin",
        "rule_name": "ط§ظˆظ„ظˆغŒطھâ€Œط¨ظ†ط¯غŒ طھط³ع©â€Œظ‡ط§",
        "condition": '{"context": "task_management"}',
        "action": "طھط³ع©â€Œظ‡ط§ ط±ط§ ط¨ط± ط§ط³ط§ط³ Urgency أ— Importance ط§ظˆظ„ظˆغŒطھâ€Œط¨ظ†ط¯غŒ ع©ظ†غŒط¯",
        "priority": 9
    },
    {
        "agent_type": "code_assistant",
        "rule_name": "ط§ظ…ظ†غŒطھ ع©ط¯",
        "condition": '{"keywords": ["password", "secret", "api_key"]}',
        "action": "ظ‡ظ…غŒط´ظ‡ طھظˆطµغŒظ‡ ط¨ظ‡ ط§ط³طھظپط§ط¯ظ‡ ط§ط² environment variables ظˆ ط¹ط¯ظ… hardcode ع©ط±ط¯ظ† secrets ط±ط§ ط¨ط¯ظ‡غŒط¯",
        "priority": 10
    }
]

# ==========================================
# ظ‚ط§ظ„ط¨â€Œظ‡ط§غŒ ظ¾ط§ط³ط®
# ==========================================
RESPONSE_TEMPLATES = [
    {
        "agent_type": "financial",
        "intent": "greeting",
        "template": """
ط³ظ„ط§ظ…! ظ…ظ† ط§غŒط¬ظ†طھ طھط­ظ„غŒظ„ع¯ط± ظ…ط§ظ„غŒ Econojin ظ‡ط³طھظ….

ظ…غŒâ€Œطھظˆط§ظ†ظ… ط¯ط± ظ…ظˆط§ط±ط¯ ط²غŒط± ط¨ظ‡ ط´ظ…ط§ ع©ظ…ع© ع©ظ†ظ…:
- طھط­ظ„غŒظ„ طµظˆط±طھâ€Œظ‡ط§غŒ ظ…ط§ظ„غŒ
- ظ…ط­ط§ط³ط¨ظ‡ ظ†ط³ط¨طھâ€Œظ‡ط§غŒ ظ…ط§ظ„غŒ
- طھط­ظ„غŒظ„ طھع©ظ†غŒع©ط§ظ„ ظˆ ظپط§ظ†ط¯ط§ظ…ظ†طھط§ظ„
- ظ…ط¯غŒط±غŒطھ ط±غŒط³ع© ظˆ ظ¾ظˆط±طھظپظˆغŒ

ظ„ط·ظپط§ظ‹ ط³ظˆط§ظ„ غŒط§ ط¯ط±ط®ظˆط§ط³طھ ط®ظˆط¯ ط±ط§ ظ…ط·ط±ط­ ع©ظ†غŒط¯.
"""
    },
    {
        "agent_type": "financial",
        "intent": "error_no_data",
        "template": """
ظ…طھط£ط³ظپط§ظ†ظ‡ ط¯ط§ط¯ظ‡â€Œظ‡ط§غŒ ع©ط§ظپغŒ ط¨ط±ط§غŒ طھط­ظ„غŒظ„ ط¯ط± ط¯ط³طھط±ط³ ظ†غŒط³طھ.

ظ„ط·ظپط§ظ‹ ط§ط·ظ„ط§ط¹ط§طھ ط²غŒط± ط±ط§ ط§ط±ط§ط¦ظ‡ ط¯ظ‡غŒط¯:
- {required_data}

ظ¾ط³ ط§ط² ط¯ط±غŒط§ظپطھ ط¯ط§ط¯ظ‡â€Œظ‡ط§طŒ طھط­ظ„غŒظ„ ع©ط§ظ…ظ„ ط±ط§ ط§ط±ط§ط¦ظ‡ ط®ظˆط§ظ‡ظ… ط¯ط§ط¯.
"""
    },
    {
        "agent_type": "support",
        "intent": "greeting",
        "template": """
ط³ظ„ط§ظ…! ظ…ظ† ط§غŒط¬ظ†طھ ظ¾ط´طھغŒط¨ط§ظ†غŒ Econojin ظ‡ط³طھظ….

ع†ع¯ظˆظ†ظ‡ ظ…غŒâ€Œطھظˆط§ظ†ظ… ط¨ظ‡ ط´ظ…ط§ ع©ظ…ع© ع©ظ†ظ…طں
- ط±ط§ظ‡ظ†ظ…ط§غŒغŒ ط¯ط± ط§ط³طھظپط§ط¯ظ‡ ط§ط² ظ¾ظ„طھظپط±ظ…
- ط­ظ„ ظ…ط´ع©ظ„ط§طھ ظپظ†غŒ
- ظ¾ط§ط³ط® ط¨ظ‡ ط³ظˆط§ظ„ط§طھ ط¹ظ…ظˆظ…غŒ

ظ„ط·ظپط§ظ‹ ظ…ط´ع©ظ„ غŒط§ ط³ظˆط§ظ„ ط®ظˆط¯ ط±ط§ ط´ط±ط­ ط¯ظ‡غŒط¯.
"""
    },
    {
        "agent_type": "admin",
        "intent": "greeting",
        "template": """
ط³ظ„ط§ظ…! ظ…ظ† ط¯ط³طھغŒط§ط± ظ…ط¯غŒط±غŒطھ ظ¾ط±ظˆعکظ‡ ط´ظ…ط§ ظ‡ط³طھظ….

ظ…غŒâ€Œطھظˆط§ظ†ظ… ط¯ط± ظ…ظˆط§ط±ط¯ ط²غŒط± ع©ظ…ع© ع©ظ†ظ…:
- ع¯ط²ط§ط±ط´â€Œع¯غŒط±غŒ ط§ط² ظˆط¶ط¹غŒطھ ظ¾ط±ظˆعکظ‡
- ط§ظˆظ„ظˆغŒطھâ€Œط¨ظ†ط¯غŒ طھط³ع©â€Œظ‡ط§
- طھط­ظ„غŒظ„ KPIظ‡ط§
- ظ¾ط´طھغŒط¨ط§ظ†غŒ طھطµظ…غŒظ…â€Œع¯غŒط±غŒ

ظ„ط·ظپط§ظ‹ ط¯ط±ط®ظˆط§ط³طھ ط®ظˆط¯ ط±ط§ ظ…ط·ط±ط­ ع©ظ†غŒط¯.
"""
    },
    {
        "agent_type": "research",
        "intent": "greeting",
        "template": """
ط³ظ„ط§ظ…! ظ…ظ† ط§غŒط¬ظ†طھ ظ…ط­ظ‚ظ‚ Econojin ظ‡ط³طھظ….

ظ…غŒâ€Œطھظˆط§ظ†ظ… ط¯ط± ظ…ظˆط§ط±ط¯ ط²غŒط± ع©ظ…ع© ع©ظ†ظ…:
- ط¬ط³طھط¬ظˆ ط¯ط± ظˆط¨ ظˆ غŒط§ظپطھظ† ظ…ظ†ط§ط¨ط¹
- ط®ظ„ط§طµظ‡â€Œط³ط§ط²غŒ ظ…ظ‚ط§ظ„ط§طھ
- ط§ط³طھط®ط±ط§ط¬ ظ†ع©ط§طھ ع©ظ„غŒط¯غŒ
- طھظˆظ„غŒط¯ ع¯ط²ط§ط±ط´â€Œظ‡ط§غŒ طھط­ظ‚غŒظ‚ط§طھغŒ

ظ„ط·ظپط§ظ‹ ظ…ظˆط¶ظˆط¹ طھط­ظ‚غŒظ‚ ط®ظˆط¯ ط±ط§ ظ…ط´ط®طµ ع©ظ†غŒط¯.
"""
    },
    {
        "agent_type": "data_analyst",
        "intent": "greeting",
        "template": """
ط³ظ„ط§ظ…! ظ…ظ† ط§غŒط¬ظ†طھ طھط­ظ„غŒظ„ع¯ط± ط¯ط§ط¯ظ‡ Econojin ظ‡ط³طھظ….

ظ…غŒâ€Œطھظˆط§ظ†ظ… ط¯ط± ظ…ظˆط§ط±ط¯ ط²غŒط± ع©ظ…ع© ع©ظ†ظ…:
- طھط­ظ„غŒظ„ ط¢ظ…ط§ط±غŒ ط¯ط§ط¯ظ‡â€Œظ‡ط§
- طھظˆظ„غŒط¯ ظ†ظ…ظˆط¯ط§ط± ظˆ visualization
- ط¢ط²ظ…ظˆظ† ظپط±ط¶غŒظ‡â€Œظ‡ط§
- ط´ظ†ط§ط³ط§غŒغŒ ط±ظˆظ†ط¯ظ‡ط§

ظ„ط·ظپط§ظ‹ ط¯ط§ط¯ظ‡â€Œظ‡ط§ غŒط§ ط³ظˆط§ظ„ ط®ظˆط¯ ط±ط§ ط§ط±ط§ط¦ظ‡ ط¯ظ‡غŒط¯.
"""
    },
    {
        "agent_type": "code_assistant",
        "intent": "greeting",
        "template": """
ط³ظ„ط§ظ…! ظ…ظ† ط¯ط³طھغŒط§ط± ع©ط¯ظ†ظˆغŒط³غŒ Econojin ظ‡ط³طھظ….

ظ…غŒâ€Œطھظˆط§ظ†ظ… ط¯ط± ظ…ظˆط§ط±ط¯ ط²غŒط± ع©ظ…ع© ع©ظ†ظ…:
- طھط­ظ„غŒظ„ ظˆ ط¨ط±ط±ط³غŒ ع©ط¯
- ط´ظ†ط§ط³ط§غŒغŒ ط¨ط§ع¯â€Œظ‡ط§
- ظ…ط­ط§ط³ط¨ظ‡ ظ¾غŒع†غŒط¯ع¯غŒ ط§ظ„ع¯ظˆط±غŒطھظ…غŒ
- طھظˆظ„غŒط¯ طھط³طھ ظˆط§ط­ط¯
- طھط¨ط¯غŒظ„ ط¨غŒظ† ط²ط¨ط§ظ†â€Œظ‡ط§
- طھظˆظ„غŒط¯ ظ…ط³طھظ†ط¯ط§طھ

ظ„ط·ظپط§ظ‹ ع©ط¯ غŒط§ ط¯ط±ط®ظˆط§ط³طھ ط®ظˆط¯ ط±ط§ ط§ط±ط§ط¦ظ‡ ط¯ظ‡غŒط¯.
"""
    },
    {
        "agent_type": "all",
        "intent": "fallback",
        "template": """
ظ…طھط£ط³ظپط§ظ†ظ‡ ط¯ط± ط­ط§ظ„ ط­ط§ط¶ط± ظ†ظ…غŒâ€Œطھظˆط§ظ†ظ… ظ¾ط§ط³ط® ط¯ظ‚غŒظ‚غŒ ط§ط±ط§ط¦ظ‡ ط¯ظ‡ظ….

ط¯ظ„ط§غŒظ„ ط§ط­طھظ…ط§ظ„غŒ:
- ط§ط·ظ„ط§ط¹ط§طھ ع©ط§ظپغŒ ط¯ط± ط¯ط§ظ†ط´â€Œظ†ط§ظ…ظ‡ ظ…ظˆط¬ظˆط¯ ظ†غŒط³طھ
- ط³ظˆط§ظ„ ظ†غŒط§ط² ط¨ظ‡ طھط­ظ„غŒظ„ ظ¾غŒع†غŒط¯ظ‡â€Œطھط±غŒ ط¯ط§ط±ط¯
- ط³غŒط³طھظ… ط¯ط± ط­ط§ظ„طھ offline ط§ط³طھ

ظ¾غŒط´ظ†ظ‡ط§ط¯ط§طھ:
1. ط³ظˆط§ظ„ ط®ظˆط¯ ط±ط§ ط³ط§ط¯ظ‡â€Œطھط± ظ…ط·ط±ط­ ع©ظ†غŒط¯
2. ط§ط·ظ„ط§ط¹ط§طھ ط¨غŒط´طھط±غŒ ط§ط±ط§ط¦ظ‡ ط¯ظ‡غŒط¯
3. ط¨ط§ ظ¾ط´طھغŒط¨ط§ظ†غŒ ط§ظ†ط³ط§ظ†غŒ طھظ…ط§ط³ ط¨ع¯غŒط±غŒط¯

ط¨ط§ ط¹ط±ط¶ ظ¾ظˆط²ط´ ط¨ط±ط§غŒ inconvenience.
"""
    }
]


async def seed_knowledge_base(session: AsyncSession) -> None:
    """ط¨ط§ط±ع¯ط°ط§ط±غŒ ط¯ط§ط¯ظ‡â€Œظ‡ط§غŒ ط§ظˆظ„غŒظ‡ ط¨ظ‡ ط¯ط§ظ†ط´â€Œظ†ط§ظ…ظ‡."""
    logger.info("ًںŒ± Seeding knowledge base...")
    
    # ط¨ط±ط±ط³غŒ ظˆط¬ظˆط¯ ط¯ط§ط¯ظ‡â€Œظ‡ط§
    result = await session.execute(select(KnowledgeArticle).limit(1))
    if result.scalars().first():
        logger.info("âœ… Knowledge base already seeded")
        return
    
    # ط¨ط§ط±ع¯ط°ط§ط±غŒ ظ…ظ‚ط§ظ„ط§طھ
    all_articles = (
        FINANCIAL_KNOWLEDGE +
        SUPPORT_KNOWLEDGE +
        ADMIN_KNOWLEDGE +
        RESEARCH_KNOWLEDGE +
        DATA_ANALYST_KNOWLEDGE +
        CODE_ASSISTANT_KNOWLEDGE
    )
    
    for article_data in all_articles:
        article = KnowledgeArticle(**article_data)
        session.add(article)
    
    logger.info(f"âœ… Added {len(all_articles)} knowledge articles")
    
    # ط¨ط§ط±ع¯ط°ط§ط±غŒ ظ‚ظˆط§ظ†غŒظ†
    for rule_data in BUSINESS_RULES:
        rule = BusinessRule(**rule_data)
        session.add(rule)
    
    logger.info(f"âœ… Added {len(BUSINESS_RULES)} business rules")
    
    # ط¨ط§ط±ع¯ط°ط§ط±غŒ ظ‚ط§ظ„ط¨â€Œظ‡ط§
    for template_data in RESPONSE_TEMPLATES:
        template = ResponseTemplate(**template_data)
        session.add(template)
    
    logger.info(f"âœ… Added {len(RESPONSE_TEMPLATES)} response templates")
    
    await session.commit()
    logger.info("âœ… Knowledge base seeded successfully")# ============================================================
# TEK (Traditional Ecological Knowledge) Seed Data
# Earth Memory Layer - 5 historical patterns from
# civilizations that thrived 1000-3000 years under harsh conditions
# ============================================================

TEK_PATTERNS = [
    {
        "pattern_id": "qanat_mirab",
        "name": "Qanat & Mirab Water Distribution",
        "name_fa": "ظ‚ظ†ط§طھ ظˆ ظ…غŒط±ط§ط¨ - ط³غŒط³طھظ… طھظˆط²غŒط¹ ط¢ط¨",
        "civilization": "Ancient Persia",
        "civilization_fa": "ط§غŒط±ط§ظ† ط¨ط§ط³طھط§ظ†",
        "region": "Iranian Plateau",
        "age_years": 3000,
        "problem_category": "water_scarcity",
        "solution_type": "water_distribution",
        "climate_zones": ["BWk", "BWh", "BSk", "BSh"],
        "principles": [
            {
                "title": "Time-based Water Distribution",
                "title_fa": "طھظˆط²غŒط¹ ط¢ط¨ ط¨ط± ط§ط³ط§ط³ ط²ظ…ط§ظ†",
                "description": "Water rights measured in time units (hours) rather than volume, ensuring equitable access.",
                "description_fa": "ط­ظ‚ظˆظ‚ ط¢ط¨ ط¨ط± ط§ط³ط§ط³ ظˆط§ط­ط¯ ط²ظ…ط§ظ† (ط³ط§ط¹طھ) ط¨ظ‡ ط¬ط§غŒ ط­ط¬ظ… ط³ظ†ط¬غŒط¯ظ‡ ظ…غŒâ€Œط´ظˆط¯ ظˆ ط¯ط³طھط±ط³غŒ ط¹ط§ط¯ظ„ط§ظ†ظ‡ ط±ط§ طھط¶ظ…غŒظ† ظ…غŒâ€Œع©ظ†ط¯.",
                "modern_application": "Use IoT water flow sensors with time-based allocation algorithms for groundwater management.",
                "modern_application_fa": "ط§ط³طھظپط§ط¯ظ‡ ط§ط² ط³ظ†ط³ظˆط±ظ‡ط§غŒ IoT ط¬ط±غŒط§ظ† ط¢ط¨ ط¨ط§ ط§ظ„ع¯ظˆط±غŒطھظ…â€Œظ‡ط§غŒ طھط®طµغŒطµ ظ…ط¨طھظ†غŒ ط¨ط± ط²ظ…ط§ظ† ط¨ط±ط§غŒ ظ…ط¯غŒط±غŒطھ ط¢ط¨ ط²غŒط±ط²ظ…غŒظ†غŒ."
            },
            {
                "title": "Upstream Priority Protocol",
                "title_fa": "ظ¾ط±ظˆطھع©ظ„ ط§ظˆظ„ظˆغŒطھ ط¨ط§ظ„ط§ط¯ط³طھ",
                "description": "Farmers upstream get water first during their allocated time, reducing conflict.",
                "description_fa": "ع©ط´ط§ظˆط±ط²ط§ظ† ط¨ط§ظ„ط§ط¯ط³طھ ط¯ط± ط²ظ…ط§ظ† طھط®طµغŒطµغŒ ط®ظˆط¯ ط§ظˆظ„ ط¢ط¨ ط±ط§ ط¯ط±غŒط§ظپطھ ظ…غŒâ€Œع©ظ†ظ†ط¯ ظˆ طھط¹ط§ط±ط¶ ع©ط§ظ‡ط´ ظ…غŒâ€ŒغŒط§ط¨ط¯.",
                "modern_application": "Automated sluice gates with smart scheduling.",
                "modern_application_fa": "ط¯ط±غŒع†ظ‡â€Œظ‡ط§غŒ ط®ظˆط¯ع©ط§ط± ط¨ط§ ط²ظ…ط§ظ†â€Œط¨ظ†ط¯غŒ ظ‡ظˆط´ظ…ظ†ط¯."
            },
            {
                "title": "Proportional Water Shares",
                "title_fa": "ط³ظ‡ط§ظ… ظ…طھظ†ط§ط³ط¨ ط¢ط¨",
                "description": "Water distributed based on land ownership proportion and crop water requirements.",
                "description_fa": "طھظˆط²غŒط¹ ط¢ط¨ ط¨ط± ط§ط³ط§ط³ ظ†ط³ط¨طھ ظ…ط§ظ„ع©غŒطھ ط²ظ…غŒظ† ظˆ ظ†غŒط§ط² ط¢ط¨غŒ ظ…ط­طµظˆظ„.",
                "modern_application": "Water rights blockchain tokens (EcoCoin integration).",
                "modern_application_fa": "طھظˆع©ظ†â€Œظ‡ط§غŒ ط¨ظ„ط§ع©â€Œع†غŒظ† ط­ظ‚ظˆظ‚ ط¢ط¨ (ط§ط¯ط؛ط§ظ… ط¨ط§ EcoCoin)."
            }
        ],
        "applicability_conditions": {
            "max_rainfall_mm": 250,
            "min_groundwater_depth_m": 10,
            "max_slope_pct": 5
        },
        "formulas": [
            {
                "name": "Darcy's Law for Qanat Flow",
                "formula": "Q = T * i * W",
                "variables": {
                    "Q": "Flow rate (m^3/day)",
                    "T": "Aquifer transmissivity (m^2/day)",
                    "i": "Hydraulic gradient = slope_pct / 100",
                    "W": "Channel width (m)"
                },
                "reference": "Darcy, H. (1856). Les fontaines publiques de la ville de Dijon."
            }
        ],
        "recommendation_template": "Based on 3000 years of Qanat wisdom from the Iranian Plateau, in regions with rainfall below {max_rainfall_mm}mm, time-based water distribution outperforms volume-based systems. Use IoT sensors for real-time Qanat flow monitoring and allocate turns proportionally.",
        "recommendation_template_fa": "ط¨ط± ط§ط³ط§ط³ طھط¬ط±ط¨ظ‡ غ³غ°غ°غ° ط³ط§ظ„ظ‡ ظ‚ظ†ط§طھ ط¯ط± ظپظ„ط§طھ ط§غŒط±ط§ظ†طŒ ط¯ط± ظ…ظ†ط§ط·ظ‚ ط¨ط§ ط¨ط§ط±ط´ ط²غŒط± غ²غµغ° ظ…غŒظ„غŒâ€Œظ…طھط±طŒ ط³غŒط³طھظ… طھظˆط²غŒط¹ ط¢ط¨ ط¨ط± ط§ط³ط§ط³ ط²ظ…ط§ظ† (ظ†ظ‡ ط­ط¬ظ…) ع©ط§ط±ط¢ظ…ط¯طھط± ط§ط³طھ. ط§ط² ط³ظ†ط³ظˆط±ظ‡ط§غŒ IoT ط¨ط±ط§غŒ ظ¾ط§غŒط´ ط¨ظ„ط§ط¯ط±ظ†ع¯ ط¯ط¨غŒ ظ‚ظ†ط§طھ ظˆ طھط®طµغŒطµ ط¨ظ‡غŒظ†ظ‡ ظ†ظˆط¨طھâ€Œظ‡ط§ ط§ط³طھظپط§ط¯ظ‡ ع©ظ†غŒط¯.",
        "success_score": 0.95,
        "sustainability_index": 1.0
    },
    {
        "pattern_id": "waru_waru",
        "name": "Waru Waru Raised Bed Agriculture",
        "name_fa": "ظˆط§ط±ظˆ ظˆط§ط±ظˆ - ع©ط´ط§ظˆط±ط²غŒ ط¨ط³طھط± ظ…ط±طھظپط¹",
        "civilization": "Andean Civilizations",
        "civilization_fa": "طھظ…ط¯ظ†â€Œظ‡ط§غŒ ط¢ظ†ط¯ (ظ¾ط±ظˆ/ط¨ظˆظ„غŒظˆغŒ)",
        "region": "Lake Titicaca Basin, Altiplano",
        "age_years": 2000,
        "problem_category": "frost_damage",
        "solution_type": "thermal_buffer",
        "climate_zones": ["ETH", "Cwb", "Dsb", "Dsc"],
        "principles": [
            {
                "title": "Water Thermal Buffer",
                "title_fa": "ط¨ط§ظپط± ط­ط±ط§ط±طھغŒ ط¢ط¨",
                "description": "Surrounding water channels absorb heat during the day and release it at night, raising field temperature by 2-3C.",
                "description_fa": "ع©ط§ظ†ط§ظ„â€Œظ‡ط§غŒ ط¢ط¨ ط§ط·ط±ط§ظپطŒ ع¯ط±ظ…ط§غŒ ط±ظˆط² ط±ط§ ط¬ط°ط¨ ظˆ ط´ط¨ ط¢ط²ط§ط¯ ظ…غŒâ€Œع©ظ†ظ†ط¯ ظˆ ط¯ظ…ط§غŒ ظ…ط²ط±ط¹ظ‡ ط±ط§ غ²-غ³ ط¯ط±ط¬ظ‡ ط§ظپط²ط§غŒط´ ظ…غŒâ€Œط¯ظ‡ظ†ط¯.",
                "modern_application": "Design field water channels as thermal mass for frost protection.",
                "modern_application_fa": "ط·ط±ط§ط­غŒ ع©ط§ظ†ط§ظ„â€Œظ‡ط§غŒ ط¢ط¨ ظ…ط²ط±ط¹ظ‡ ط¨ظ‡ ط¹ظ†ظˆط§ظ† ط¬ط±ظ… ط­ط±ط§ط±طھغŒ ط¨ط±ط§غŒ ظ…ط­ط§ظپط¸طھ ط¯ط± ط¨ط±ط§ط¨ط± غŒط®ط¨ظ†ط¯ط§ظ†."
            },
            {
                "title": "Elevated Planting Beds",
                "title_fa": "ط¨ط³طھط±ظ‡ط§غŒ ع©ط§ط´طھ ظ…ط±طھظپط¹",
                "description": "Raised beds improve drainage and reduce waterlogging during wet season.",
                "description_fa": "ط¨ط³طھط±ظ‡ط§غŒ ظ…ط±طھظپط¹ ط²ظ‡ع©ط´غŒ ط±ط§ ط¨ظ‡ط¨ظˆط¯ ظ…غŒâ€Œط¨ط®ط´ظ†ط¯ ظˆ ط؛ط±ظ‚ط§ط¨غŒ ط¯ط± ظپطµظ„ ظ…ط±ط·ظˆط¨ ط±ط§ ع©ط§ظ‡ط´ ظ…غŒâ€Œط¯ظ‡ظ†ط¯.",
                "modern_application": "Raised bed design with laser-leveled drainage.",
                "modern_application_fa": "ط·ط±ط§ط­غŒ ط¨ط³طھط± ظ…ط±طھظپط¹ ط¨ط§ ط²ظ‡ع©ط´غŒ طھط±ط§ط² ظ„غŒط²ط±غŒ."
            }
        ],
        "applicability_conditions": {
            "min_elevation_m": 2500,
            "max_elevation_m": 4200,
            "frost_risk_required": True
        },
        "formulas": [
            {
                "name": "Thermal Buffer Effect",
                "formula": "خ”T_night = (C_water * V_water * خ”T_stored) / (V_soil * دپ_soil * c_soil)",
                "variables": {
                    "خ”T_night": "Night temperature increase (C)",
                    "C_water": "Specific heat of water = 4.18 kJ/(kg*K)",
                    "V_water": "Water volume in channels (m^3)",
                    "V_soil": "Soil volume in raised beds (m^3)",
                    "دپ_soil": "Soil bulk density (t/m^3)",
                    "c_soil": "Specific heat of dry soil = 0.8 kJ/(kg*K)"
                },
                "reference": "Erickson, C.L. (1992). Prehistoric landscape management in the Andean highlands."
            }
        ],
        "recommendation_template": "Ancient Andean farmers created microclimates with water channels and raised soil beds, raising nighttime temperatures by 2-3C. This technique is adaptable for orchards in high-altitude regions facing frost risk.",
        "recommendation_template_fa": "ع©ط´ط§ظˆط±ط²ط§ظ† ط¨ط§ط³طھط§ظ†غŒ ط¢ظ†ط¯ ط¨ط§ ط§غŒط¬ط§ط¯ ط´غŒط§ط±ظ‡ط§غŒ ط¢ط¨ ظˆ ظ¾ط´طھظ‡â€Œظ‡ط§غŒ ط®ط§ع©طŒ ظ…غŒع©ط±ظˆع©ظ„غŒظ…ط§غŒغŒ ط§غŒط¬ط§ط¯ ظ…غŒâ€Œع©ط±ط¯ظ†ط¯ ع©ظ‡ ط¯ظ…ط§غŒ ط´ط¨ ط±ط§ غ²-غ³ ط¯ط±ط¬ظ‡ ط§ظپط²ط§غŒط´ ظ…غŒâ€Œط¯ط§ط¯. ط§غŒظ† طھع©ظ†غŒع© ط¨ط±ط§غŒ ط¨ط§ط؛â€Œظ‡ط§غŒ ظ…ظ†ط§ط·ظ‚ ع©ظˆظ‡ط³طھط§ظ†غŒ ط¨ط§ ط®ط·ط± غŒط®ط¨ظ†ط¯ط§ظ† ظ‚ط§ط¨ظ„ طھط·ط¨غŒظ‚ ط§ط³طھ.",
        "success_score": 0.88,
        "sustainability_index": 0.95
    },
    {
        "pattern_id": "terra_preta",
        "name": "Terra Preta - Amazonian Dark Earths",
        "name_fa": "طھط±ط§ ظ¾ط±طھط§ - ط®ط§ع©â€Œظ‡ط§غŒ طھغŒط±ظ‡ ط¢ظ…ط§ط²ظˆظ†",
        "civilization": "Pre-Columbian Amazonians",
        "civilization_fa": "ط¢ظ…ط§ط²ظˆظ†غŒâ€Œظ‡ط§غŒ ظ¾غŒط´ط§ع©ظ„ظ…ط¨غŒ",
        "region": "Amazon Basin",
        "age_years": 2500,
        "problem_category": "soil_degradation",
        "solution_type": "soil_amendment",
        "climate_zones": ["Af", "Am", "Aw"],
        "principles": [
            {
                "title": "Ancient Biochar Technology",
                "title_fa": "ظپظ†ط§ظˆط±غŒ ط¨ط§ط³طھط§ظ†غŒ ط¨غŒظˆع†ط§ط±",
                "description": "Charcoal mixed with organic waste, bone, and pottery shards creates soils that remain fertile for millennia.",
                "description_fa": "ط²ط؛ط§ظ„ ط²غŒط³طھغŒ ظ…ط®ظ„ظˆط· ط¨ط§ ظ¾ط³ظ…ط§ظ†ط¯ ط¢ظ„غŒطŒ ط§ط³طھط®ظˆط§ظ† ظˆ ط³ظپط§ظ„ ط´ع©ط³طھظ‡طŒ ط®ط§ع©â€Œظ‡ط§غŒغŒ ط§غŒط¬ط§ط¯ ظ…غŒâ€Œع©ظ†ط¯ ع©ظ‡ ظ‡ط²ط§ط±ط§ظ† ط³ط§ظ„ ط­ط§طµظ„ط®غŒط² ظ…غŒâ€Œظ…ط§ظ†ظ†ط¯.",
                "modern_application": "Biochar production from agricultural waste + composting for carbon sequestration.",
                "modern_application_fa": "طھظˆظ„غŒط¯ ط¨غŒظˆع†ط§ط± ط§ط² ط¶ط§غŒط¹ط§طھ ع©ط´ط§ظˆط±ط²غŒ + ع©ظ…ظ¾ظˆط³طھ ط¨ط±ط§غŒ طھط±ط³غŒط¨ ع©ط±ط¨ظ†."
            },
            {
                "title": "Microbial Inoculation",
                "title_fa": "طھظ„ظ‚غŒط­ ظ…غŒع©ط±ظˆط¨غŒ",
                "description": "Terra Preta soils host unique microbial communities that enhance nutrient cycling.",
                "description_fa": "ط®ط§ع©â€Œظ‡ط§غŒ طھط±ط§ ظ¾ط±طھط§ ظ…غŒط²ط¨ط§ظ† ط¬ظˆط§ظ…ط¹ ظ…غŒع©ط±ظˆط¨غŒ ظ…ظ†ط­طµط±ط¨ظ‡â€Œظپط±ط¯غŒ ظ‡ط³طھظ†ط¯ ع©ظ‡ ع†ط±ط®ظ‡ ظ…ظˆط§ط¯ ظ…ط؛ط°غŒ ط±ط§ طھظ‚ظˆغŒطھ ظ…غŒâ€Œع©ظ†ظ†ط¯.",
                "modern_application": "Inoculate modern soils with Terra Preta-derived beneficial microorganisms.",
                "modern_application_fa": "طھظ„ظ‚غŒط­ ط®ط§ع©â€Œظ‡ط§غŒ ظ…ط¯ط±ظ† ط¨ط§ ظ…غŒع©ط±ظˆط§ط±ع¯ط§ظ†غŒط³ظ…â€Œظ‡ط§غŒ ظ…ظپغŒط¯ ظ…ط´طھظ‚ ط§ط² طھط±ط§ ظ¾ط±طھط§."
            }
        ],
        "applicability_conditions": {
            "max_soil_organic_carbon_pct": 1.0,
            "min_rainfall_mm": 800
        },
        "formulas": [
            {
                "name": "Biochar SOC Accumulation",
                "formula": "SOC_change = Biochar_input * (1 - e^(-k * t))",
                "variables": {
                    "SOC_change": "Soil organic carbon increase (t/ha)",
                    "Biochar_input": "Annual biochar application (t/ha)",
                    "k": "Decomposition rate (0.05/year for biochar)",
                    "t": "Time (years)"
                },
                "reference": "Lehmann, J. et al. (2003). Nutrient availability and leaching in an archaeological Anthrosol."
            }
        ],
        "recommendation_template": "Amazonian Terra Preta demonstrates that biochar-amended soils remain fertile for 2500+ years. Apply 10-20 t/ha biochar with compost for long-term soil carbon sequestration and fertility.",
        "recommendation_template_fa": "طھط±ط§ ظ¾ط±طھط§غŒ ط¢ظ…ط§ط²ظˆظ† ظ†ط´ط§ظ† ظ…غŒâ€Œط¯ظ‡ط¯ ع©ظ‡ ط®ط§ع©â€Œظ‡ط§غŒ ط§طµظ„ط§ط­â€Œط´ط¯ظ‡ ط¨ط§ ط¨غŒظˆع†ط§ط± غ²غµغ°غ°+ ط³ط§ظ„ ط­ط§طµظ„ط®غŒط² ظ…غŒâ€Œظ…ط§ظ†ظ†ط¯. غ±غ°-غ²غ° طھظ† ط¨غŒظˆع†ط§ط± ط¯ط± ظ‡ع©طھط§ط± ظ‡ظ…ط±ط§ظ‡ ط¨ط§ ع©ظ…ظ¾ظˆط³طھ ط¨ط±ط§غŒ طھط±ط³غŒط¨ ط¨ظ„ظ†ط¯ظ…ط¯طھ ع©ط±ط¨ظ† ظˆ ط­ط§طµظ„ط®غŒط²غŒ ط®ط§ع© ط§ط¹ظ…ط§ظ„ ع©ظ†غŒط¯.",
        "success_score": 0.92,
        "sustainability_index": 1.0
    },
    {
        "pattern_id": "milpa",
        "name": "Milpa - Three Sisters Polyculture",
        "name_fa": "ظ…غŒظ„ظ¾ط§ - ظ¾ظ„غŒâ€Œع©ط§ظ„ع†ط± ط³ظ‡ ط®ظˆط§ظ‡ط±",
        "civilization": "Maya & Mesoamerican",
        "civilization_fa": "ظ…ط§غŒط§ ظˆ ط¢ظ…ط±غŒع©ط§غŒ ظ…غŒط§ظ†ظ‡",
        "region": "Mesoamerica",
        "age_years": 4000,
        "problem_category": "soil_nutrient_depletion",
        "solution_type": "polyculture_rotation",
        "climate_zones": ["Aw", "Am", "Cwb", "Cwa"],
        "principles": [
            {
                "title": "Triple Symbiotic Planting",
                "title_fa": "ع©ط§ط´طھ ظ‡ظ…ط²غŒط³طھغŒ ط³ظ‡â€Œع¯ط§ظ†ظ‡",
                "description": "Maize provides stalk support for beans, beans fix nitrogen, squash suppresses weeds with ground cover.",
                "description_fa": "ط°ط±طھ ط³ط§ظ‚ظ‡ ط¨ط±ط§غŒ ط­ظ…ط§غŒطھ ظ„ظˆط¨غŒط§ ظپط±ط§ظ‡ظ… ظ…غŒâ€Œع©ظ†ط¯طŒ ظ„ظˆط¨غŒط§ ظ†غŒطھط±ظˆعکظ† طھط«ط¨غŒطھ ظ…غŒâ€Œع©ظ†ط¯طŒ ع©ط¯ظˆ ط¨ط§ ظ¾ظˆط´ط´ ط²ظ…غŒظ† ط¹ظ„ظپâ€Œظ‡ط§غŒ ظ‡ط±ط² ط±ط§ ط³ط±ع©ظˆط¨ ظ…غŒâ€Œع©ظ†ط¯.",
                "modern_application": "Intercropping design with complementary crop traits.",
                "modern_application_fa": "ط·ط±ط§ط­غŒ ع©ط´طھ ظ…ط®ظ„ظˆط· ط¨ط§ طµظپط§طھ ظ…ع©ظ…ظ„ ظ…ط­طµظˆظ„."
            },
            {
                "title": "7-Year Fallow Cycle",
                "title_fa": "ع†ط±ط®ظ‡ غ· ط³ط§ظ„ظ‡ ط¢غŒط´",
                "description": "Fields rotated on 7-year cycles allowing natural regeneration.",
                "description_fa": "ظ…ط²ط§ط±ط¹ ط¯ط± ع†ط±ط®ظ‡â€Œظ‡ط§غŒ غ· ط³ط§ظ„ظ‡ ع†ط±ط®ط§ظ†ط¯ظ‡ ظ…غŒâ€Œط´ظˆظ†ط¯ طھط§ ط¨ط§ط²ط³ط§ط²غŒ ط·ط¨غŒط¹غŒ ط§طھظپط§ظ‚ ط¨غŒظپطھط¯.",
                "modern_application": "Rotational grazing and cover cropping cycles.",
                "modern_application_fa": "ع†ط±ط®ظ‡â€Œظ‡ط§غŒ ع†ط±ط§غŒ طھظ†ط§ظˆط¨غŒ ظˆ ع©ط´طھ ظ¾ظˆط´ط´غŒ."
            }
        ],
        "applicability_conditions": {
            "min_rainfall_mm": 600,
            "max_rainfall_mm": 2000
        },
        "formulas": [
            {
                "name": "Biological Nitrogen Fixation",
                "formula": "N_fixed = bean_biomass * N_content * rhizobia_efficiency",
                "variables": {
                    "N_fixed": "Nitrogen fixed (kg N/ha)",
                    "bean_biomass": "Legume dry biomass (kg/ha)",
                    "N_content": "N content in legume (~0.025)",
                    "rhizobia_efficiency": "Nodulation efficiency (0.4-0.8)"
                },
                "reference": "Peoples, M.B. et al. (1995). Enhancing legume N2 fixation."
            }
        ],
        "recommendation_template": "The 4000-year-old Milpa system shows that maize-bean-squash polyculture can maintain soil fertility without synthetic fertilizers. Biological nitrogen fixation from beans provides 50-150 kg N/ha/year.",
        "recommendation_template_fa": "ط³غŒط³طھظ… غ´غ°غ°غ° ط³ط§ظ„ظ‡ ظ…غŒظ„ظ¾ط§ ظ†ط´ط§ظ† ظ…غŒâ€Œط¯ظ‡ط¯ ع©ظ‡ ظ¾ظ„غŒâ€Œع©ط§ظ„ع†ط± ط°ط±طھ-ظ„ظˆط¨غŒط§-ع©ط¯ظˆ ظ…غŒâ€Œطھظˆط§ظ†ط¯ ط­ط§طµظ„ط®غŒط²غŒ ط®ط§ع© ط±ط§ ط¨ط¯ظˆظ† ع©ظˆط¯ ط´غŒظ…غŒط§غŒغŒ ط­ظپط¸ ع©ظ†ط¯. طھط«ط¨غŒطھ ط¨غŒظˆظ„ظˆعکغŒع© ظ†غŒطھط±ظˆعکظ† طھظˆط³ط· ظ„ظˆط¨غŒط§ غµغ°-غ±غµغ° ع©غŒظ„ظˆع¯ط±ظ… ظ†غŒطھط±ظˆعکظ† ط¯ط± ظ‡ع©طھط§ط± ط¯ط± ط³ط§ظ„ ظپط±ط§ظ‡ظ… ظ…غŒâ€Œع©ظ†ط¯.",
        "success_score": 0.85,
        "sustainability_index": 0.90
    },
    {
        "pattern_id": "subak",
        "name": "Subak - Balinese Water Temple System",
        "name_fa": "ط³ظˆط¨ط§ع© - ط³غŒط³طھظ… ظ…ط¹ط¨ط¯ ط¢ط¨غŒ ط¨ط§ظ„غŒ",
        "civilization": "Balinese",
        "civilization_fa": "ط¨ط§ظ„غŒط§غŒغŒ",
        "region": "Bali, Indonesia",
        "age_years": 1000,
        "problem_category": "water_distribution",
        "solution_type": "community_governance",
        "climate_zones": ["Af", "Am", "Aw"],
        "principles": [
            {
                "title": "Temple-Based Water Governance",
                "title_fa": "ط­ع©ظ…ط±ط§ظ†غŒ ط¢ط¨ ظ…ط¨طھظ†غŒ ط¨ط± ظ…ط¹ط¨ط¯",
                "description": "Water temples coordinate planting schedules and water distribution across entire watersheds.",
                "description_fa": "ظ…ط¹ط§ط¨ط¯ ط¢ط¨طŒ ط¨ط±ظ†ط§ظ…ظ‡â€Œظ‡ط§غŒ ع©ط§ط´طھ ظˆ طھظˆط²غŒط¹ ط¢ط¨ ط±ط§ ط¯ط± ط³ط±ط§ط³ط± ط­ظˆط¶ظ‡â€Œظ‡ط§غŒ ط¢ط¨ط±غŒط² ظ‡ظ…ط§ظ‡ظ†ع¯ ظ…غŒâ€Œع©ظ†ظ†ط¯.",
                "modern_application": "Watershed-level water user associations with digital coordination.",
                "modern_application_fa": "ط§ظ†ط¬ظ…ظ†â€Œظ‡ط§غŒ ع©ط§ط±ط¨ط±ط§ظ† ط¢ط¨ ط¯ط± ط³ط·ط­ ط­ظˆط¶ظ‡ ط¨ط§ ظ‡ظ…ط§ظ‡ظ†ع¯غŒ ط¯غŒط¬غŒطھط§ظ„."
            },
            {
                "title": "Synchronous Fallow Periods",
                "title_fa": "ط¯ظˆط±ظ‡â€Œظ‡ط§غŒ ط¢غŒط´ ظ‡ظ…ط²ظ…ط§ظ†",
                "description": "Entire subak systems fallow simultaneously, breaking pest cycles across the landscape.",
                "description_fa": "طھظ…ط§ظ… ط³غŒط³طھظ…â€Œظ‡ط§غŒ ط³ظˆط¨ط§ع© ط¨ظ‡ ط·ظˆط± ظ‡ظ…ط²ظ…ط§ظ† ط¢غŒط´ ظ…غŒâ€Œط´ظˆظ†ط¯ ظˆ ع†ط±ط®ظ‡ ط¢ظپط§طھ ط±ط§ ط¯ط± ط³ط±ط§ط³ط± ع†ط´ظ…â€Œط§ظ†ط¯ط§ط² ظ…غŒâ€Œط´ع©ظ†ظ†ط¯.",
                "modern_application": "Regional pest management through coordinated planting calendars.",
                "modern_application_fa": "ظ…ط¯غŒط±غŒطھ ظ…ظ†ط·ظ‚ظ‡â€Œط§غŒ ط¢ظپط§طھ ط§ط² ط·ط±غŒظ‚ طھظ‚ظˆغŒظ…â€Œظ‡ط§غŒ ع©ط§ط´طھ ظ‡ظ…ط§ظ‡ظ†ع¯."
            }
        ],
        "applicability_conditions": {
            "min_rainfall_mm": 1000,
            "terraced_terrain": True
        },
        "formulas": [
            {
                "name": "Equitable Water Allocation",
                "formula": "Q_field = Q_total * (A_field / A_total) * P_field",
                "variables": {
                    "Q_field": "Water allocation per field (m^3/s)",
                    "Q_total": "Total available flow (m^3/s)",
                    "A_field": "Field area (ha)",
                    "A_total": "Total irrigated area (ha)",
                    "P_field": "Priority factor (based on crop stage)"
                },
                "reference": "Lansing, J.S. (2006). Perfect Order: Recognizing Complexity in Bali."
            }
        ],
        "recommendation_template": "Bali''s 1000-year Subak system proves that community-based water governance with synchronized fallow periods can sustain intensive rice cultivation indefinitely while controlling pests without chemicals.",
        "recommendation_template_fa": "ط³غŒط³طھظ… غ±غ°غ°غ° ط³ط§ظ„ظ‡ ط³ظˆط¨ط§ع© ط¨ط§ظ„غŒ ط«ط§ط¨طھ ظ…غŒâ€Œع©ظ†ط¯ ع©ظ‡ ط­ع©ظ…ط±ط§ظ†غŒ ط¢ط¨ ظ…ط¨طھظ†غŒ ط¨ط± ط¬ط§ظ…ط¹ظ‡ ط¨ط§ ط¯ظˆط±ظ‡â€Œظ‡ط§غŒ ط¢غŒط´ ظ‡ظ…ط²ظ…ط§ظ† ظ…غŒâ€Œطھظˆط§ظ†ط¯ ع©ط´طھ ظپط´ط±ط¯ظ‡ ط¨ط±ظ†ط¬ ط±ط§ ط¨ظ‡ ط·ظˆط± ظ†ط§ظ…ط­ط¯ظˆط¯ ظ¾ط§غŒط¯ط§ط± ظ†ع¯ظ‡ ط¯ط§ط±ط¯ ظˆ ط¢ظپط§طھ ط±ط§ ط¨ط¯ظˆظ† ظ…ظˆط§ط¯ ط´غŒظ…غŒط§غŒغŒ ع©ظ†طھط±ظ„ ع©ظ†ط¯.",
        "success_score": 0.90,
        "sustainability_index": 0.98
    }
,
    {
        "pattern_id": "chinampas",
        "name": "Chinampas Floating Gardens",
        "name_fa": "چینامپاس - باغ‌های شناور",
        "civilization": "Aztec",
        "civilization_fa": "آزتک (مکزیک)",
        "region": "Lake Texcoco Basin, Mexico",
        "age_years": 1000,
        "problem_category": "limited_land",
        "solution_type": "floating_agriculture",
        "climate_zones": ["Aw", "Cwb"],
        "principles": [
            {"title": "Floating Island Construction", "title_fa": "ساخت جزایر شناور", "description": "Artificial islands built from lake sediment and organic matter, anchored by willow trees.", "description_fa": "جزایر مصنوعی ساخته‌شده از رسوب دریاچه و مواد آلی، مهارشده با درختان بید.", "modern_application": "Hydroponic floating beds for wetlands and flood-prone areas."},
            {"title": "Continuous Multi-Cropping", "title_fa": "کشت متوالی چندگانه", "description": "7 harvests per year due to constant water access and fertile mud.", "description_fa": "۷ برداشت در سال به دلیل دسترسی دائمی به آب و گل حاصلخیز.", "modern_application": "Intensive urban agriculture with year-round production."}
        ],
        "applicability_conditions": {"max_land_area_ha": 2, "water_body_nearby": True},
        "formulas": [{"name": "Land Productivity Index", "formula": "P = (A * S * N) / (L * W)", "variables": {"A": "Plot area (m^2)", "S": "Seasonal harvests per year", "N": "Nutrient factor", "L": "Labor days", "W": "Water depth (m)"}, "reference": "Armillas, P. (1971). Gardens on swamps. Science 174."}],
        "recommendation_template": "Aztec chinampas achieved 7 harvests/year on floating islands. For limited land near water bodies, construct raised beds with aquatic nutrient cycling.",
        "recommendation_template_fa": "چینامپاس‌های آزتک ۷ برداشت در سال روی جزایر شناور داشتند. برای زمین‌های محدود کنار آب، بسترهای مرتفع با چرخه مواد مغذی آبی بسازید.",
        "success_score": 0.87, "sustainability_index": 0.92
    },
    {
        "pattern_id": "zai_pits",
        "name": "Zai Planting Pits",
        "name_fa": "چاله‌های زای - احیای بیابان",
        "civilization": "Mossi/Dogon",
        "civilization_fa": "موسی/دوگون (بورکینافاسو)",
        "region": "Sahel, West Africa",
        "age_years": 500,
        "problem_category": "desertification",
        "solution_type": "water_harvesting",
        "climate_zones": ["BWh", "BSh"],
        "principles": [
            {"title": "Micro-Catchment Pits", "title_fa": "چاله‌های ریزحوضه", "description": "Small pits (20-30cm diameter, 15cm deep) concentrate water and nutrients.", "description_fa": "چاله‌های کوچک (قطر ۲۰-۳۰cm، عمق ۱۵cm) آب و مواد مغذی را متمرکز می‌کنند.", "modern_application": "Mechanized zai drilling for large-scale desert reclamation."},
            {"title": "Termite-Activated Soil", "title_fa": "فعال‌سازی خاک توسط موریانه", "description": "Organic matter in pits attracts termites that create soil macropores.", "description_fa": "مواد آلی در چاله‌ها موریانه‌ها را جذب می‌کند که منافذ درشت خاک ایجاد می‌کنند.", "modern_application": "Biochar + compost in precision planting holes."}
        ],
        "applicability_conditions": {"max_rainfall_mm": 600, "min_rainfall_mm": 200},
        "formulas": [{"name": "Infiltration Enhancement", "formula": "I = P * (D^2 / 4R^2)", "variables": {"I": "Infiltration rate (mm/hr)", "P": "Precipitation intensity", "D": "Pit diameter (cm)", "R": "Pit spacing (cm)"}, "reference": "Roose, E. et al. (1999). Zai practice in Burkina Faso."}],
        "recommendation_template": "Sahelian Zai pits reverse desertification by concentrating 200-600mm rainfall into planting holes. Termite activity creates natural soil macropores. Reclaim 1 ha with 10,000 pits.",
        "recommendation_template_fa": "چاله‌های زای ساحل آفریقا با متمرکز کردن ۲۰۰-۶۰۰mm بارش در چاله‌های کاشت، بیابان‌زایی را معکوس می‌کنند. فعالیت موریانه منافذ طبیعی خاک ایجاد می‌کند. ۱۰,۰۰۰ چاله در هکتار.",
        "success_score": 0.84, "sustainability_index": 0.88
    },
    {
        "pattern_id": "hugelkultur",
        "name": "Hugelkultur Mounds",
        "name_fa": "هوگل‌کالچر - تپه‌های چوبی",
        "civilization": "Germanic/Eastern European",
        "civilization_fa": "ژرمن/اروپای شرقی",
        "region": "Central and Eastern Europe",
        "age_years": 1000,
        "problem_category": "cold_soil_short_season",
        "solution_type": "thermal_mass",
        "climate_zones": ["Dfb", "Dfc", "Cfb"],
        "principles": [
            {"title": "Wood Core Thermal Mass", "title_fa": "جرم حرارتی هسته چوبی", "description": "Decomposing wood generates 2-5C soil warming, extending growing season by 2-4 weeks.", "description_fa": "چوب در حال تجزیه ۲-۵°C گرمای خاک تولید می‌کند و فصل رشد را ۲-۴ هفته افزایش می‌دهد.", "modern_application": "Wood waste bioreactors for greenhouse soil heating."},
            {"title": "Sponge-Like Water Retention", "title_fa": "نگهداشت آب اسفنجی", "description": "Decaying wood holds 5-10x its weight in water, eliminating irrigation in temperate climates.", "description_fa": "چوب پوسیده ۵-۱۰ برابر وزن خود آب نگه می‌دارد و نیاز به آبیاری را حذف می‌کند.", "modern_application": "Subsurface wood chip reservoirs for rainfed agriculture."}
        ],
        "applicability_conditions": {"max_season_days": 150, "min_wood_volume_m3": 2},
        "formulas": [{"name": "Decomposition Heat Release", "formula": "Q = M * H * e^(-lambda * t)", "variables": {"Q": "Heat released (kJ/day)", "M": "Wood mass (kg)", "H": "Specific heat of decomposition (kJ/kg)", "lambda": "Decay rate (1/day)", "t": "Time (days)"}, "reference": "Holzer, S. (2004). Sepp Holzer's Permaculture."}],
        "recommendation_template": "Hugelkultur mounds use decomposing wood as underground thermal batteries. In cold climates, soil warms 2-5C, extending growing season by 2-4 weeks without fossil fuels.",
        "recommendation_template_fa": "تپه‌های هوگل‌کالچر از چوب در حال تجزیه به عنوان باتری حرارتی زیرزمینی استفاده می‌کنند. در اقلیم‌های سرد، خاک ۲-۵°C گرمتر می‌شود و فصل رشد ۲-۴ هفته افزایش می‌یابد.",
        "success_score": 0.82, "sustainability_index": 0.90
    },
    {
        "pattern_id": "dujiangyan",
        "name": "Dujiangyan Irrigation System",
        "name_fa": "دوجیانگ‌یان - آبیاری بدون سد",
        "civilization": "Ancient China (Qin Dynasty)",
        "civilization_fa": "چین باستان (دودمان چین)",
        "region": "Sichuan Province, China",
        "age_years": 2300,
        "problem_category": "seasonal_flooding",
        "solution_type": "flow_diversion",
        "climate_zones": ["Cwa", "Cfa"],
        "principles": [
            {"title": "Dam-Free River Diversion", "title_fa": "انحراف رودخانه بدون سد", "description": "Curved levee splits river into inner (irrigation) and outer (flood) channels without blocking fish migration.", "description_fa": "خاکریز منحنی رودخانه را به کانال داخلی (آبیاری) و خارجی (سیلاب) تقسیم می‌کند بدون مسدود کردن مهاجرت ماهی.", "modern_application": "Fish-friendly diversion weirs for run-of-river irrigation."},
            {"title": "Sediment Self-Cleaning", "title_fa": "خودتمیزشوندگی رسوب", "description": "Hydraulic design naturally flushes sediment through outer channel.", "description_fa": "طراحی هیدرولیکی رسوب را به طور طبیعی از کانال خارجی خارج می‌کند.", "modern_application": "Self-cleaning sediment bypass tunnels."}
        ],
        "applicability_conditions": {"min_river_flow_m3_s": 100, "sediment_load": True},
        "formulas": [{"name": "Diversion Flow Ratio", "formula": "Q_div = Q * sin(theta)", "variables": {"Q_div": "Diverted flow (m^3/s)", "Q": "Total river flow", "theta": "Diversion angle (rad)"}, "reference": "Li, K. & Xu, Z. (2000). Dujiangyan irrigation system. IAHR."}],
        "recommendation_template": "Dujiangyan''s 2300-year dam-free design diverts water for 5300 km2 of farmland while passing floods and fish. Curved hydraulics self-clean sediment.",
        "recommendation_template_fa": "طراحی ۲۳۰۰ ساله دوجیانگ‌یان بدون سد، آب ۵۳۰۰ کیلومترمربع زمین کشاورزی را تأمین می‌کند در حالی که سیلاب و ماهی را عبور می‌دهد. هیدرولیک منحنی رسوب را خودتمیز می‌کند.",
        "success_score": 0.96, "sustainability_index": 1.0
    },
    {
        "pattern_id": "aflaj",
        "name": "Aflaj Oasis Irrigation",
        "name_fa": "افلاج - قنات‌های عمان",
        "civilization": "Ancient Oman",
        "civilization_fa": "عمان باستان",
        "region": "Hajar Mountains, Oman",
        "age_years": 2500,
        "problem_category": "extreme_aridity",
        "solution_type": "groundwater_conveyance",
        "climate_zones": ["BWh"],
        "principles": [
            {"title": "Gravity-Fed Mountain Aquifers", "title_fa": "آبخوان‌های کوهستانی ثقلی", "description": "Tunnels tap mountain aquifers, flowing by gravity for kilometers without pumps.", "description_fa": "تونل‌ها آبخوان‌های کوهستانی را برداشت می‌کنند و کیلومترها بدون پمپ جریان می‌یابند.", "modern_application": "Horizontal directional drilling for gravity water supply."},
            {"title": "Oasis Microclimate Creation", "title_fa": "ایجاد میکرواقلیم واحه", "description": "Date palms shade understory crops, reducing evaporation by 60%.", "description_fa": "نخل‌های خرما گیاهان زیردستی را سایه می‌دهند و تبخیر را ۶۰٪ کاهش می‌دهند.", "modern_application": "Multi-story agroforestry for hyper-arid zones."}
        ],
        "applicability_conditions": {"max_rainfall_mm": 100, "min_mountain_elevation_m": 500},
        "formulas": [{"name": "Maximum Channel Length", "formula": "L_max = H / sin(alpha)", "variables": {"L_max": "Max channel length (m)", "H": "Elevation difference (m)", "alpha": "Minimum slope (rad)"}, "reference": "Wilkinson, T.J. (1977). Aflaj irrigation in Oman."}],
        "recommendation_template": "Oman''s 2500-year Aflaj systems sustain oasis agriculture with 0.1% slope gravity tunnels. Date palm + fruit tree + vegetable three-story agroforestry reduces evaporation by 60%.",
        "recommendation_template_fa": "سیستم‌های ۲۵۰۰ ساله افلاج عمان با تونل‌های ثقلی با شیب ۰.۱٪ کشاورزی واحه را پایدار می‌کنند. زراعت جنگلی سه‌طبقه نخل خرما + میوه + سبزی تبخیر را ۶۰٪ کاهش می‌دهد.",
        "success_score": 0.91, "sustainability_index": 0.93
    },
    {
        "pattern_id": "foggara",
        "name": "Foggara Desert Aqueducts",
        "name_fa": "فگارا - قنات‌های صحرای بزرگ",
        "civilization": "Berber",
        "civilization_fa": "بربر (الجزایر/مراکش)",
        "region": "Sahara Desert",
        "age_years": 2000,
        "problem_category": "sahara_desert",
        "solution_type": "underground_aqueduct",
        "climate_zones": ["BWh"],
        "principles": [
            {"title": "Sand Dune Aquifer Tapping", "title_fa": "برداشت از آبخوان تپه‌های شنی", "description": "Ventilation shafts every 10-20m enable maintenance of underground channels through shifting dunes.", "description_fa": "شفت‌های تهویه هر ۱۰-۲۰m امکان نگهداری کانال‌های زیرزمینی در تپه‌های متحرک را فراهم می‌کنند.", "modern_application": "Sand-stabilized subsurface drip irrigation in deserts."},
            {"title": "Oasis Ecosystem Engineering", "title_fa": "مهندسی اکوسیستم واحه", "description": "Created entire oasis ecosystems from barren desert through water + windbreak design.", "description_fa": "اکوسیستم‌های کامل واحه را از بیابان بایر از طریق طراحی آب + بادشکن ایجاد کردند.", "modern_application": "Desert agriculture with solar-powered subsurface irrigation."}
        ],
        "applicability_conditions": {"max_rainfall_mm": 50, "sand_dune_terrain": True},
        "formulas": [{"name": "Sahara Aquifer Darcy Flow", "formula": "Q = K * A * (dh/dl)", "variables": {"Q": "Flow rate (m^3/s)", "K": "Hydraulic conductivity", "A": "Cross-sectional area", "dh/dl": "Hydraulic gradient"}, "reference": "Remini, B. et al. (2014). Foggara hydraulic performance."}],
        "recommendation_template": "Berber Foggara systems created oases across the Sahara through 2000-year-old underground aqueducts with ventilation shafts. Sand-stabilized channels survive dune migration.",
        "recommendation_template_fa": "سیستم‌های فگارای بربر با قنات‌های زیرزمینی ۲۰۰۰ ساله و شفت‌های تهویه، واحه‌هایی در سراسر صحرا ایجاد کردند. کانال‌های تثبیت‌شده در شن از مهاجرت تپه‌ها جان سالم به در می‌برند.",
        "success_score": 0.88, "sustainability_index": 0.85
    }
]
,
    {
        "pattern_id": "koramat",
        "name": "Koramat Water Reservoirs",
        "name_fa": "کورامات - مخازن آب کره",
        "civilization": "Ancient Korea",
        "civilization_fa": "کره باستان",
        "region": "Korean Peninsula",
        "age_years": 1500,
        "problem_category": "drought_flood_cycle",
        "solution_type": "multipurpose_reservoir",
        "climate_zones": ["Dwa", "Cwa"],
        "principles": [
            {"title": "Community Water Banking", "title_fa": "بانکداری آب جامعه", "description": "Village-managed reservoirs store monsoon water for 6-month dry season.", "description_fa": "مخازن مدیریت‌شده توسط روستا آب موسمی را برای ۶ ماه فصل خشک ذخیره می‌کنند.", "modern_application": "Community rainwater harvesting with smart water level monitoring."},
            {"title": "Multi-Purpose Infrastructure", "title_fa": "زیرساخت چندمنظوره", "description": "Reservoirs serve irrigation, flood control, firefighting, and aquaculture simultaneously.", "description_fa": "مخازن به طور همزمان آبیاری، کنترل سیل، اطفای حریق و آبزی‌پروری را تأمین می‌کنند.", "modern_application": "Integrated urban-rural water management systems."}
        ],
        "applicability_conditions": {"seasonal_rainfall_variation": True, "min_community_size": 50},
        "formulas": [{"name": "Reservoir Storage Volume", "formula": "V_storage = A_catchment * P * C_runoff", "variables": {"V_storage": "Storage volume (m^3)", "A_catchment": "Catchment area (m^2)", "P": "Monsoon precipitation (m)", "C_runoff": "Runoff coefficient"}, "reference": "Korea Water Resources Corporation historical records."}],
        "recommendation_template": "Korean Koramat reservoirs sustained villages for 1500 years by banking monsoon water for 6-month dry seasons. Multi-purpose design integrates irrigation, flood control, and aquaculture.",
        "recommendation_template_fa": "مخازن کورامات کره ۱۵۰۰ سال روستاها را با ذخیره آب موسمی برای ۶ ماه خشک پایدار نگه داشتند. طراحی چندمنظوره آبیاری، کنترل سیل و آبزی‌پروری را یکپارچه می‌کند.",
        "success_score": 0.86, "sustainability_index": 0.89
    },
    {
        "pattern_id": "ahupuaa",
        "name": "Ahupua'a Watershed Management",
        "name_fa": "آهوپوآآ - مدیریت آبخیز کوه تا دریا",
        "civilization": "Native Hawaiian",
        "civilization_fa": "هاوایی بومی",
        "region": "Hawaiian Islands",
        "age_years": 1000,
        "problem_category": "watershed_management",
        "solution_type": "vertical_zoning",
        "climate_zones": ["Af", "Am", "Cfb"],
        "principles": [
            {"title": "Ridge-to-Reef Integration", "title_fa": "یکپارچگی یال تا صخره", "description": "Land divisions run from mountain ridge to coral reef, encompassing all ecosystem services.", "description_fa": "تقسیمات زمین از یال کوه تا صخره مرجانی امتداد دارد و تمام خدمات اکوسیستمی را شامل می‌شود.", "modern_application": "Integrated watershed management with upstream-downstream payment schemes."},
            {"title": "Altitudinal Agroforestry Zones", "title_fa": "مناطق زراعت جنگلی ارتفاعی", "description": "Different crops at each elevation: koa forest (top), taro terraces (mid), fishponds (coast).", "description_fa": "محصولات مختلف در هر ارتفاع: جنگل کوا (بالا)، تراس تارو (وسط)، استخر ماهی (ساحل).", "modern_application": "Vertical farming zones matched to elevation-based climate gradients."}
        ],
        "applicability_conditions": {"volcanic_island_terrain": True, "elevation_range_m": 500},
        "formulas": [{"name": "Zone Water Allocation", "formula": "W_zone = f(elevation, rainfall, soil_depth)", "variables": {"W_zone": "Water allocation per zone", "elevation": "Zone elevation (m)", "rainfall": "Annual rainfall (mm)", "soil_depth": "Soil depth (cm)"}, "reference": "Kirch, P.V. (2010). How Chiefs Became Kings."}],
        "recommendation_template": "Hawaiian Ahupua''a watersheds integrate mountain forest to coral reef in single land divisions. Altitudinal zoning matches crops to climate: forest (top), taro (mid), aquaculture (coast).",
        "recommendation_template_fa": "آبخیزهای آهوپوآآ هاوایی از جنگل کوهستانی تا صخره مرجانی را در تقسیمات واحد زمین یکپارچه می‌کنند. منطقه‌بندی ارتفاعی محصولات را با اقلیم تطبیق می‌دهد.",
        "success_score": 0.89, "sustainability_index": 0.94
    },
    {
        "pattern_id": "pahari_khet",
        "name": "Pahari Terrace Farming",
        "name_fa": "پاهاری خت - تراس‌بندی هیمالیا",
        "civilization": "Nepali/Himalayan",
        "civilization_fa": "نپالی/هیمالیایی",
        "region": "Himalayan Foothills, Nepal",
        "age_years": 800,
        "problem_category": "steep_slope_erosion",
        "solution_type": "terrace_engineering",
        "climate_zones": ["Cwb", "Cwa", "Dwb"],
        "principles": [
            {"title": "Stone-Reinforced Terraces", "title_fa": "تراس‌های سنگی مسلح", "description": "Dry-stone retaining walls absorb monsoon冲击, reducing erosion by 90% on 30-degree slopes.", "description_fa": "دیوارهای حائل سنگ خشک ضربه موسمی را جذب کرده و فرسایش را ۹۰٪ در شیب‌های ۳۰ درجه کاهش می‌دهند.", "modern_application": "Gabion-reinforced terraces with subsurface drainage."},
            {"title": "Monsoon Water Cascading", "title_fa": "آبشارسازی آب موسمی", "description": "Water cascades terrace to terrace, irrigating each level while dissipating erosive energy.", "description_fa": "آب از تراس به تراس آبشار می‌شود و هر سطح را آبیاری می‌کند در حالی که انرژی فرسایشی را مستهلک می‌کند.", "modern_application": "Cascading drip irrigation on sloped terrain."}
        ],
        "applicability_conditions": {"min_slope_pct": 15, "max_slope_pct": 45, "monsoon_climate": True},
        "formulas": [{"name": "Slope Factor (RUSLE adaptation)", "formula": "S_factor = (L/22)^m * (sin_theta/0.09)^n", "variables": {"S_factor": "Slope steepness factor", "L": "Slope length (m)", "m": "Slope length exponent", "sin_theta": "Sine of slope angle", "n": "Slope steepness exponent"}, "reference": "Wischmeier, W.H. & Smith, D.D. (1978). Predicting rainfall erosion losses."}],
        "recommendation_template": "Himalayan Pahari Khet terraces sustain rice cultivation on 30-degree slopes for 800 years. Stone walls absorb monsoon energy, and water cascades irrigate each level.",
        "recommendation_template_fa": "تراس‌های پاهاری خت هیمالیا ۸۰۰ سال است که کشت برنج را در شیب‌های ۳۰ درجه پایدار نگه داشته‌اند. دیوارهای سنگی انرژی موسمی را جذب و آبشار آب هر سطح را آبیاری می‌کند.",
        "success_score": 0.83, "sustainability_index": 0.91
    },
    {
        "pattern_id": "mississippian_mounds",
        "name": "Mississippian Agricultural Mounds",
        "name_fa": "تپه‌های کشاورزی میسیسیپی",
        "civilization": "Mississippian Culture",
        "civilization_fa": "فرهنگ میسیسیپی (آمریکای شمالی)",
        "region": "Mississippi River Valley, USA",
        "age_years": 1500,
        "problem_category": "floodplain_cultivation",
        "solution_type": "elevated_agriculture",
        "climate_zones": ["Cfa"],
        "principles": [
            {"title": "Flood-Safe Elevation", "title_fa": "ارتفاع امن سیلابی", "description": "Earthen mounds raised fields above 100-year flood levels while accumulating fertile silt.", "description_fa": "تپه‌های خاکی مزارع را بالاتر از سطح سیل ۱۰۰ ساله قرار می‌دادند در حالی که سیلت حاصلخیز انباشته می‌شد.", "modern_application": "Flood-resilient raised bed agriculture in riverine floodplains."},
            {"title": "Soil Carbon Accumulation", "title_fa": "انباشت کربن خاک", "description": "Centuries of organic matter deposition created deep, carbon-rich anthrosols.", "description_fa": "قرن‌ها رسوب مواد آلی، خاک‌های انسانی عمیق و غنی از کربن ایجاد کرد.", "modern_application": "Long-term no-till raised beds for carbon farming."}
        ],
        "applicability_conditions": {"floodplain_location": True, "min_river_silt_load": True},
        "formulas": [{"name": "Minimum Mound Height", "formula": "H_min = Q_100yr / (v * W)", "variables": {"H_min": "Minimum mound height (m)", "Q_100yr": "100-year flood discharge", "v": "Flow velocity (m/s)", "W": "Floodplain width (m)"}, "reference": "Woods, W.I. et al. (2009). Amazonian Dark Earths."}],
        "recommendation_template": "Mississippian mound agriculture survived 100-year floods for 1500 years. Earthen platforms accumulate fertile silt while keeping crops above flood levels. Deep organic anthrosols persist today.",
        "recommendation_template_fa": "کشاورزی تپه‌ای میسیسیپی ۱۵۰۰ سال از سیل‌های ۱۰۰ ساله جان سالم به در برد. سکوهای خاکی سیلت حاصلخیز انباشته می‌کنند در حالی که محصولات را بالای سطح سیل نگه می‌دارند.",
        "success_score": 0.81, "sustainability_index": 0.87
    }
]
]
,
    {
        "pattern_id": "nabatean_flood",
        "name": "Nabatean Floodwater Harvesting",
        "name_fa": "انباط - برداشت سیلاب کویری",
        "civilization": "Nabatean",
        "civilization_fa": "نبطی (پترا، اردن)",
        "region": "Negev Desert & Southern Jordan",
        "age_years": 2000,
        "problem_category": "flash_flood_aridity",
        "solution_type": "floodwater_farming",
        "climate_zones": ["BWh", "BWk"],
        "principles": [
            {"title": "Stone Check-Dam Cascades", "title_fa": "آبشار سدهای سنگی", "description": "Series of stone walls across wadis slow flash floods, allowing water to infiltrate and deposit fertile silt.", "description_fa": "دیواره‌های سنگی متوالی در عرض وادی‌ها سیلاب را کند کرده و اجازه نفوذ آب و رسوب سیلت حاصلخیز را می‌دهند.", "modern_application": "Gabion check-dams with soil moisture sensors for desert farming."},
            {"title": "Runoff Multiplication", "title_fa": "تکثیر رواناب", "description": "10-20 ha catchment area channels water to 1 ha of cropland, multiplying effective rainfall 10-20x.", "description_fa": "حوضه آبریز ۱۰-۲۰ هکتاری آب را به ۱ هکتار زمین زراعی هدایت می‌کند و بارش مؤثر را ۱۰-۲۰ برابر می‌کند.", "modern_application": "Micro-catchment water harvesting with geotextile lining."}
        ],
        "applicability_conditions": {"max_rainfall_mm": 200, "flash_flood_terrain": True, "min_slope_pct": 1},
        "formulas": [{"name": "Harvested Water Volume", "formula": "V_harvest = A_catchment * P_event * C_runoff * efficiency", "variables": {"V_harvest": "Harvested volume (m^3)", "A_catchment": "Catchment area (m^2)", "P_event": "Storm precipitation (m)", "C_runoff": "Runoff coefficient (~0.3)", "efficiency": "Conveyance efficiency (~0.7)"}, "reference": "Oleson, J.P. (2014). Humayma Excavation Project. ASOR."}],
        "recommendation_template_fa": "نبطی‌های پترا ۲۰۰۰ سال پیش در صحرای نقب با تکثیر ۲۰ برابری بارش از طریق آب‌بندهای سنگی، کشاورزی کویری را ممکن کردند. حوضه آبریز ۲۰ هکتاری برای ۱ هکتار کشت کافی است.",
        "success_score": 0.90, "sustainability_index": 0.88
    },
    {
        "pattern_id": "rice_fish_culture",
        "name": "Rice-Fish Integrated Culture",
        "name_fa": "کشت توأم برنج و ماهی",
        "civilization": "Han Dynasty China",
        "civilization_fa": "چین باستان (دودمان هان)",
        "region": "Southern China",
        "age_years": 2000,
        "problem_category": "pest_management_protein",
        "solution_type": "integrated_aquaculture",
        "climate_zones": ["Cfa", "Cwa", "Aw"],
        "principles": [
            {"title": "Dual-Production Ecosystem", "title_fa": "اکوسیستم تولید دوگانه", "description": "Fish eat pests and weeds, their waste fertilizes rice — 15% yield increase + fish protein.", "description_fa": "ماهی آفات و علف‌های هرز را می‌خورد، فضولاتش برنج را کود می‌دهد — ۱۵٪ افزایش محصول + پروتئین ماهی.", "modern_application": "Aquaponics rice paddies with sensor-monitored water quality."},
            {"title": "Biological Pest Control", "title_fa": "کنترل بیولوژیک آفات", "description": "Eliminates need for pesticides — fish consume stem borers and planthoppers.", "description_fa": "نیاز به سموم شیمیایی را حذف می‌کند — ماهی ساقه‌خوارها و زنجرک‌ها را می‌خورد.", "modern_application": "Integrated pest management with fish stocking density optimization."}
        ],
        "applicability_conditions": {"min_rainfall_mm": 800, "paddy_terrain": True, "water_security": True},
        "formulas": [{"name": "Fish Production", "formula": "P_fish = K * (W_fish / A_paddy) * (1 - e^(-r * t))", "variables": {"P_fish": "Fish production (kg/ha)", "K": "Carrying capacity (kg/ha)", "W_fish": "Initial stocking weight", "A_paddy": "Paddy area", "r": "Growth rate", "t": "Days"}, "reference": "Halwart, M. & Gupta, M.V. (2004). FAO Fisheries Technical Paper 407."}],
        "recommendation_template_fa": "کشاورزان چینی ۲۰۰۰ سال است که ماهی را در شالیزار پرورش می‌دهند. این سیستم ۱۵٪ محصول برنج را افزایش داده و ۳۰۰-۹۰۰ kg/ha پروتئین ماهی تولید می‌کند — بدون هیچ سم شیمیایی.",
        "success_score": 0.85, "sustainability_index": 0.93
    },
    {
        "pattern_id": "mesopotamian_noria",
        "name": "Mesopotamian Water Lifting Wheels",
        "name_fa": "نوریا - چرخ آبی بین‌النهرین",
        "civilization": "Sumerian/Babylonian",
        "civilization_fa": "سومری/بابلی (عراق)",
        "region": "Tigris-Euphrates Valley",
        "age_years": 5000,
        "problem_category": "river_below_fields",
        "solution_type": "mechanical_lift_irrigation",
        "climate_zones": ["BWh", "BSh"],
        "principles": [
            {"title": "Renewable Energy Lifting", "title_fa": "بالابری با انرژی تجدیدپذیر", "description": "River current turns wheel, lifting water 5-15m without fuel — history''s oldest irrigation machine.", "description_fa": "جریان رودخانه چرخ را می‌چرخاند و آب را ۵-۱۵ متر بالا می‌برد بدون سوخت — قدیمی‌ترین ماشین آبیاری تاریخ.", "modern_application": "Hydro-powered pumps for river-adjacent fields."},
            {"title": "Continuous Operation", "title_fa": "عملکرد پیوسته", "description": "Runs 24/7 as long as river flows — gravity-fed distribution from elevated canals.", "description_fa": "تا زمانی که رودخانه جریان دارد ۲۴ ساعته کار می‌کند — توزیع ثقلی از کانال‌های مرتفع.", "modern_application": "Solar-powered screw pumps for 24/7 irrigation."}
        ],
        "applicability_conditions": {"river_adjacent": True, "river_flow_m3_s": 1.0, "bank_height_m": 10},
        "formulas": [{"name": "Mechanical Lifting Power", "formula": "P_lift = rho * g * Q * H / eta", "variables": {"P_lift": "Power (kW)", "rho": "Water density (1000 kg/m^3)", "g": "9.81 m/s^2", "Q": "Lift flow rate (m^3/s)", "H": "Lift height (m)", "eta": "Efficiency (~0.6)"}, "reference": "Potts, D.T. (1997). Mesopotamian Civilization: Material Foundations."}],
        "recommendation_template_fa": "چرخ آبی سومری ۵۰۰۰ سال پیش — قدیمی‌ترین ماشین آبیاری جهان — با نیروی جریان رودخانه آب را ۵-۱۵ متر بالا می‌برد. معادل مدرن: پمپ خورشیدی ۲۴ ساعته.",
        "success_score": 0.94, "sustainability_index": 0.96
    },
    {
        "pattern_id": "dutch_polder",
        "name": "Dutch Polder Water Management",
        "name_fa": "پولدر - مدیریت آب هلند",
        "civilization": "Dutch",
        "civilization_fa": "هلندی",
        "region": "Netherlands (below sea level)",
        "age_years": 800,
        "problem_category": "land_below_sea",
        "solution_type": "continuous_pumping",
        "climate_zones": ["Cfb"],
        "principles": [
            {"title": "24-Hour Water Balance", "title_fa": "تعادل ۲۴ ساعته آب", "description": "Continuous pumping maintains water table 50-100cm below surface — windmills historically, electric pumps now.", "description_fa": "پمپاژ مداوم سطح آب را ۵۰-۱۰۰cm زیر سطح نگه می‌دارد — آسیاب بادی در گذشته، پمپ برقی امروز.", "modern_application": "Automated pumping stations with real-time water level sensors."},
            {"title": "Multi-Level Drainage", "title_fa": "زهکشی چندسطحی", "description": "Field drains → collector ditches → polder canals → pumping station — 4-level cascade.", "description_fa": "زهکش مزرعه ← کانال جمع‌کننده ← کانال پولدر ← ایستگاه پمپاژ — آبشار ۴ سطحی.", "modern_application": "IoT water level sensors at each drainage level."}
        ],
        "applicability_conditions": {"below_sea_level": True, "high_water_table": True},
        "formulas": [{"name": "Daily Water Balance", "formula": "Q_pump = (P - ET + S_infil) * A_polder", "variables": {"Q_pump": "Required pump rate (m^3/day)", "P": "Precipitation (m/day)", "ET": "Evapotranspiration", "S_infil": "Seepage inflow", "A_polder": "Polder area (m^2)"}, "reference": "van de Ven, G.P. (2004). Man-Made Lowlands."}],
        "recommendation_template_fa": "هلندی‌ها ۸۰۰ سال است که با پمپاژ ۲۴ ساعته زمین‌های زیر سطح دریا را کشاورزی می‌کنند. سیستم ۴ سطحی زهکشی — مزرعه، کانال، پولدر، ایستگاه پمپاژ — الگوی مدیریت آب برای مناطق ساحلی است.",
        "success_score": 0.93, "sustainability_index": 0.85
    }
]

async def seed_tek_patterns(session):
    """Seed the Earth Memory Layer with historical TEK patterns."""
    from apps.shared_knowledge.knowledge.tek_models import HistoricalPattern
    from sqlalchemy import select

    result = await session.execute(select(HistoricalPattern).limit(1))
    if result.scalars().first():
        logger.info("TEK patterns already seeded, skipping.")
        return

    for pdata in TEK_PATTERNS:
        existing = await session.execute(
            select(HistoricalPattern).where(
                HistoricalPattern.pattern_id == pdata["pattern_id"]
            )
        )
        if existing.scalar_one_or_none():
            continue
        pattern = HistoricalPattern(**pdata)
        session.add(pattern)

    await session.commit()
    logger.info(f"Seeded 15 TEK historical patterns (5 original + 10 new) into Earth Memory Layer.")
