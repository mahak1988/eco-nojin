from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import json

from apps.shared_knowledge.knowledge.repository import KnowledgeRepository

logger = logging.getLogger(__name__)


class RulesEngine:
    """موتور ارزیابی و اجرای قوانین کسب‌وکار."""
    
    def __init__(self, session: AsyncSession):
        self.repo = KnowledgeRepository(session)
    
    async def evaluate(
        self,
        agent_type: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """ارزیابی قوانین و بازگرداندن اقدامات."""
        logger.info(f"⚖️ Evaluating rules for {agent_type}")
        
        rules = await self.repo.get_active_rules(agent_type)
        
        matched_rules = []
        for rule in rules:
            if self._check_condition(rule.condition, context):
                matched_rules.append({
                    "rule_name": rule.rule_name,
                    "action": rule.action,
                    "priority": rule.priority
                })
        
        # مرتب‌سازی بر اساس priority
        matched_rules.sort(key=lambda x: x["priority"], reverse=True)
        
        logger.info(f"✅ Matched {len(matched_rules)} rules")
        return matched_rules
    
    def _check_condition(self, condition_json: str, context: Dict[str, Any]) -> bool:
        """بررسی تطابق شرط با context."""
        try:
            condition = json.loads(condition_json)
            
            # بررسی keywords
            if "keywords" in condition:
                keywords = condition["keywords"]
                query = context.get("query", "").lower()
                
                for keyword in keywords:
                    if keyword.lower() in query:
                        return True
            
            # بررسی context fields
            if "context" in condition:
                context_key = condition["context"]
                if context_key in context:
                    return True
            
            return False
        
        except Exception as e:
            logger.error(f"❌ Error checking condition: {e}")
            return False
    
    async def get_actions_summary(
        self,
        agent_type: str,
        context: Dict[str, Any]
    ) -> str:
        """دریافت خلاصه اقدامات قوانین."""
        rules = await self.evaluate(agent_type, context)
        
        if not rules:
            return ""
        
        summary_parts = ["⚖️ قوانین اعمال‌شده:"]
        for rule in rules:
            summary_parts.append(f"- {rule['rule_name']}: {rule['action']}")
        
        return "\n".join(summary_parts)