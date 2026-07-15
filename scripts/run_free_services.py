#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""تست سرویس‌های رایگان Eco Nojin"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

def test_supabase():
    try:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        if not url or not key:
            return "❌ SUPABASE_URL یا SUPABASE_ANON_KEY تنظیم نشده"
        client = create_client(url, key)
        result = client.table("users").select("*").limit(1).execute()
        return "✅ اتصال به Supabase برقرار است"
    except Exception as e:
        return f"❌ خطا: {e}"

def test_openrouter():
    try:
        import httpx
        key = os.getenv("OPENROUTER_API_KEY")
        if not key:
            return "❌ OPENROUTER_API_KEY تنظیم نشده"
        return "✅ کلید OpenRouter تنظیم شده است"
    except Exception as e:
        return f"❌ خطا: {e}"

def test_yahoo():
    try:
        import yfinance as yf
        ticker = yf.Ticker("AAPL")
        data = ticker.history(period="1d")
        if len(data) > 0:
            return f"✅ اتصال برقرار است. قیمت: {data['Close'].iloc[-1]}"
        return "⚠️ داده‌ای دریافت نشد"
    except ImportError:
        return "⚠️ yfinance نصب نشده (pip install yfinance)"
    except Exception as e:
        return f"❌ خطا: {e}"

print("\n" + "=" * 60)
print("🆓 تست سرویس‌های رایگان")
print("=" * 60)
print(f"Supabase: {test_supabase()}")
print(f"OpenRouter: {test_openrouter()}")
print(f"Yahoo Finance: {test_yahoo()}")
print("=" * 60)
