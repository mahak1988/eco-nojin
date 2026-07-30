"""curl/wget must not be classified as bots."""

from apps.spider_security.middleware import BOT_UA_PATTERNS
import re


def test_curl_not_bot():
    ua = "curl/8.0"
    for p in BOT_UA_PATTERNS:
        assert re.search(p, ua) is None


def test_googlebot_is_bot():
    ua = "Mozilla/5.0 (compatible; Googlebot/2.1)"
    assert any(re.search(p, ua.lower()) for p in BOT_UA_PATTERNS)
