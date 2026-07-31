
"""Spider Web Security - AI/LLM Prompt Injection Prevention."""
from __future__ import annotations

import re


class AISecurityGuard:
    INJECTION = [
        re.compile(r"(?i)ignore\s+(all\s+)?previous\s+instructions"),
        re.compile(r"(?i)disregard\s+(all\s+)?(prior|previous|above)"),
        re.compile(r"(?i)you\s+are\s+now\s+(a|an|the)"),
        re.compile(r"(?i)system\s*:\s*"),
        re.compile(r"(?i)\[\s*INST\s*\]"),
        re.compile(r"(?i)<\s*/?\s*system\s*>"),
        re.compile(r"(?i)pretend\s+(you|to\s+be)"),
        re.compile(r"(?i)jailbreak|DAN\s+mode|developer\s+mode"),
    ]
    OUTPUT = [
        re.compile(r"(?i)(api[_-]?key|secret[_-]?key|password|token)\s*[:=]"),
        re.compile(r"(?i)postgresql://[^\s]+"),
        re.compile(r"(?i)sk-[a-zA-Z0-9]{20,}"),
        re.compile(r"(?i)ghp_[a-zA-Z0-9]{36}"),
    ]

    @classmethod
    def detect_injection(cls, prompt: str) -> tuple[bool, str]:
        for p in cls.INJECTION:
            if p.search(prompt):
                return True, "Prompt injection detected"
        return False, ""

    @classmethod
    def sanitize_prompt(cls, prompt: str) -> str:
        s = prompt
        for p in cls.INJECTION:
            s = p.sub("[FILTERED]", s)
        return s[:10000]

    @classmethod
    def filter_output(cls, output: str) -> str:
        s = output
        for p in cls.OUTPUT:
            s = p.sub("[REDACTED]", s)
        return s
