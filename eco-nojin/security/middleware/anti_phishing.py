
"""Spider Web Security - Anti-Phishing Protection."""
from __future__ import annotations

import re
from urllib.parse import urlparse


class AntiPhishingGuard:
    ALLOWED_DOMAINS = {"econojin.com","www.econojin.com","supabase.co","qdrant.io","github.com"}
    SUSPICIOUS_TLDS = {".tk",".ml",".ga",".cf",".gq",".xyz",".top",".work",".click"}

    @classmethod
    def is_suspicious_url(cls, url: str) -> tuple[bool, str]:
        try:
            parsed = urlparse(url)
        except Exception:
            return True, "Invalid URL"
        host = parsed.hostname or ""
        if host and not any(host.endswith(d) for d in cls.ALLOWED_DOMAINS):
            for tld in cls.SUSPICIOUS_TLDS:
                if host.endswith(tld):
                    return True, f"Suspicious TLD: {tld}"
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", host):
            return True, "IP instead of domain"
        if "@" in url or "%00" in url:
            return True, "Suspicious characters"
        return False, ""

    @classmethod
    def sanitize_input(cls, text: str) -> str:
        for url in re.findall(r"https?://[^\s<>\"]+", text):
            bad, _ = cls.is_suspicious_url(url)
            if bad:
                text = text.replace(url, "[URL-removed]")
        return text
