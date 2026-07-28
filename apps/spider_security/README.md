# SpiderGuard — Minimal spider/bot detection + per-IP rate limiter

SpiderGuard is a small FastAPI/Starlette middleware intended as a starting point
for defending simple endpoints from obvious crawlers and accidental scans.

Features
- UA substring heuristics for common bots/crawlers
- In-memory per-IP sliding-window rate limiter
- FastAPI/Starlette middleware (plug-and-play)

Usage
1. Add to your FastAPI app:

```python
from apps.spider_security.middleware import SpiderGuardMiddleware

app.add_middleware(SpiderGuardMiddleware, max_requests=60, window_seconds=60, block_after=True)
```

Notes
- In-memory storage is suitable for development and single-instance deployments only.
  For production or multi-instance setups, configure a shared store (Redis) and
  replace the internal `_hits` map with Redis-based counters or sorted sets.
- Extend UA heuristics, add JS-challenge or CAPTCHA for suspicious clients, and
  forward logs to ELK/Prometheus for monitoring.
