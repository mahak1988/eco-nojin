# agents/policies/policy_engine.py
"""
موتور سیاست: اعتبارسنجی ایمنی قبل از اجرای هر tool call
"""
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List

import structlog

logger = structlog.get_logger()


class PolicyAction(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    LOG_ONLY = "log_only"


@dataclass
class PolicyRule:
    """قانون سیاست"""

    name: str
    description: str
    pattern: str  # regex برای matching
    action: PolicyAction
    reason: str


class PolicyEngine:
    """موتور سیاست برای TRiSM compliance"""

    def __init__(self):
        self.rules: List[PolicyRule] = []
        self.logger = logger.bind(component="policy_engine")
        self._load_default_rules()

    def _load_default_rules(self):
        """بارگذاری قوانین پیش‌فرض"""
        self.rules = [
            PolicyRule(
                name="block_file_deletion",
                description="جلوگیری از حذف فایل‌های سیستمی",
                pattern=r"(rm -rf|del /s|remove.*\/)",
                action=PolicyAction.DENY,
                reason="File deletion operations are blocked for safety",
            ),
            PolicyRule(
                name="block_database_drop",
                description="جلوگیری از DROP DATABASE",
                pattern=r"(DROP\s+DATABASE|TRUNCATE\s+TABLE)",
                action=PolicyAction.DENY,
                reason="Destructive database operations require manual approval",
            ),
            PolicyRule(
                name="require_approval_for_payments",
                description="تأیید انسانی برای تراکنش‌های مالی",
                pattern=r"(transfer|payment|withdraw|send.*money)",
                action=PolicyAction.REQUIRE_APPROVAL,
                reason="Financial transactions require human approval",
            ),
            PolicyRule(
                name="log_api_calls",
                description="لاگ تمام API callها",
                pattern=r"(api|http|fetch|request)",
                action=PolicyAction.LOG_ONLY,
                reason="API calls logged for audit trail",
            ),
        ]

    def validate_tool_call(self, tool_name: str, tool_args: Dict[str, Any]) -> PolicyAction:
        """
        اعتبارسنجی یک tool call

        Args:
            tool_name: نام tool
            tool_args: آرگومان‌های tool

        Returns:
            PolicyAction: اقدام مجاز
        """
        tool_string = f"{tool_name}: {tool_args}"

        for rule in self.rules:
            if re.search(rule.pattern, tool_string, re.IGNORECASE):
                self.logger.warning(
                    "policy_triggered",
                    rule=rule.name,
                    tool=tool_name,
                    action=rule.action.value,
                    reason=rule.reason,
                )
                return rule.action

        return PolicyAction.ALLOW


# تست سریع
if __name__ == "__main__":
    engine = PolicyEngine()

    # تست‌های مختلف
    test_cases = [
        ("file_delete", {"command": "rm -rf /tmp/*"}),
        ("database", {"query": "DROP DATABASE production"}),
        ("payment", {"action": "transfer $1000"}),
        ("api_call", {"url": "https://api.example.com/data"}),
        ("safe_action", {"data": "read only"}),
    ]

    print("\n🔒 Policy Engine Test Results:")
    for tool_name, args in test_cases:
        action = engine.validate_tool_call(tool_name, args)
        print(f"  {tool_name:20} → {action.value:20}")
