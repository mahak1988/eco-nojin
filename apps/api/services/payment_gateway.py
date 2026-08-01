"""
Payment gateway — Stripe Checkout + Zarinpal request/verify.
Keys from environment; without keys returns configured=false.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import time
import uuid
from typing import Any, Optional

import httpx

logger = logging.getLogger("econojin.payments")

STRIPE_SECRET = os.getenv("STRIPE_SECRET_KEY", "").strip()
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "").strip()
STRIPE_PUBLISHABLE = os.getenv("STRIPE_PUBLISHABLE_KEY", "").strip()
ZARINPAL_MERCHANT = os.getenv("ZARINPAL_MERCHANT_ID", "").strip()
ZARINPAL_SANDBOX = os.getenv("ZARINPAL_SANDBOX", "true").lower() in ("1", "true", "yes")
PUBLIC_WEB_URL = os.getenv("PUBLIC_WEB_URL", "http://localhost:5173").rstrip("/")
API_PUBLIC_URL = os.getenv("API_PUBLIC_URL", "http://localhost:8000").rstrip("/")

_INTENTS: dict[str, dict[str, Any]] = {}


def gateway_status() -> dict[str, Any]:
    return {
        "stripe": {
            "configured": bool(STRIPE_SECRET),
            "publishable_key": STRIPE_PUBLISHABLE or None,
            "webhook_configured": bool(STRIPE_WEBHOOK_SECRET),
        },
        "zarinpal": {
            "configured": bool(ZARINPAL_MERCHANT),
            "sandbox": ZARINPAL_SANDBOX,
        },
        "demo_fallback": not (STRIPE_SECRET or ZARINPAL_MERCHANT),
    }


def _zp_base() -> str:
    if ZARINPAL_SANDBOX:
        return "https://sandbox.zarinpal.com"
    return "https://api.zarinpal.com"


def _zp_start_pay() -> str:
    if ZARINPAL_SANDBOX:
        return "https://sandbox.zarinpal.com/pg/StartPay/"
    return "https://www.zarinpal.com/pg/StartPay/"


async def create_checkout(
    *,
    amount: float,
    currency: str,
    description: str,
    invoice_id: Optional[str] = None,
    provider: str = "auto",
    customer_email: Optional[str] = None,
) -> dict[str, Any]:
    currency = (currency or "USD").upper()
    intent_id = f"pi_{uuid.uuid4().hex[:16]}"
    meta: dict[str, Any] = {
        "intent_id": intent_id,
        "amount": amount,
        "currency": currency,
        "description": description[:200],
        "invoice_id": invoice_id,
        "created_at": time.time(),
        "status": "created",
    }

    if provider == "auto":
        if currency in ("IRR", "IRT", "TOMAN") and ZARINPAL_MERCHANT:
            provider = "zarinpal"
        elif STRIPE_SECRET:
            provider = "stripe"
        elif ZARINPAL_MERCHANT:
            provider = "zarinpal"
        else:
            provider = "demo"

    if provider == "stripe":
        if not STRIPE_SECRET:
            raise RuntimeError("STRIPE_SECRET_KEY not configured")
        result = await _stripe_checkout(meta, customer_email)
        meta.update(result)
        meta["provider"] = "stripe"
        _INTENTS[intent_id] = meta
        return meta

    if provider == "zarinpal":
        if not ZARINPAL_MERCHANT:
            raise RuntimeError("ZARINPAL_MERCHANT_ID not configured")
        result = await _zarinpal_request(meta)
        meta.update(result)
        meta["provider"] = "zarinpal"
        _INTENTS[intent_id] = meta
        return meta

    success = f"{PUBLIC_WEB_URL}/payments/success?intent={intent_id}&demo=1"
    cancel = f"{PUBLIC_WEB_URL}/payments/cancel?intent={intent_id}"
    meta.update(
        {
            "provider": "demo",
            "checkout_url": success,
            "cancel_url": cancel,
            "status": "pending_demo",
            "message": "No merchant keys — demo mode. Set STRIPE_SECRET_KEY or ZARINPAL_MERCHANT_ID.",
        }
    )
    _INTENTS[intent_id] = meta
    return meta


async def _stripe_checkout(meta: dict[str, Any], email: Optional[str]) -> dict[str, Any]:
    amount = meta["amount"]
    currency = meta["currency"].lower()
    zero_decimal = currency in ("jpy", "krw", "vnd")
    unit = int(round(amount if zero_decimal else amount * 100))
    if unit < 1:
        raise ValueError("amount too small")

    data = {
        "mode": "payment",
        "success_url": f"{PUBLIC_WEB_URL}/payments/success?intent={meta['intent_id']}&session_id={{CHECKOUT_SESSION_ID}}",
        "cancel_url": f"{PUBLIC_WEB_URL}/payments/cancel?intent={meta['intent_id']}",
        "line_items[0][price_data][currency]": currency,
        "line_items[0][price_data][product_data][name]": meta["description"] or "Eco Nojin payment",
        "line_items[0][price_data][unit_amount]": str(unit),
        "line_items[0][quantity]": "1",
        "metadata[intent_id]": meta["intent_id"],
        "metadata[invoice_id]": meta.get("invoice_id") or "",
        "client_reference_id": meta["intent_id"],
    }
    if email:
        data["customer_email"] = email

    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(
            "https://api.stripe.com/v1/checkout/sessions",
            data=data,
            auth=(STRIPE_SECRET, ""),
        )
        if r.status_code >= 400:
            logger.error("Stripe error: %s", r.text[:500])
            raise RuntimeError(f"Stripe API error: {r.status_code}")
        body = r.json()
        return {
            "checkout_url": body["url"],
            "provider_ref": body["id"],
            "status": "redirect",
        }


async def _zarinpal_request(meta: dict[str, Any]) -> dict[str, Any]:
    amount_rial = int(round(meta["amount"]))
    if meta["currency"] in ("IRT", "TOMAN"):
        amount_rial = amount_rial * 10
    if amount_rial < 1000:
        raise ValueError("Zarinpal minimum amount not met")

    callback = f"{API_PUBLIC_URL}/api/v1/payments/zarinpal/callback?intent={meta['intent_id']}"
    payload = {
        "merchant_id": ZARINPAL_MERCHANT,
        "amount": amount_rial,
        "callback_url": callback,
        "description": meta["description"] or "Eco Nojin",
        "metadata": {
            "invoice_id": meta.get("invoice_id") or "",
            "intent_id": meta["intent_id"],
        },
    }
    url = f"{_zp_base()}/pg/v4/payment/request.json"
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(url, json=payload)
        body = r.json()
        data = body.get("data") or {}
        code = data.get("code")
        if code != 100:
            logger.error("Zarinpal request failed: %s", body)
            raise RuntimeError(f"Zarinpal request failed code={code}")
        authority = data["authority"]
        return {
            "checkout_url": f"{_zp_start_pay()}{authority}",
            "provider_ref": authority,
            "status": "redirect",
            "amount_rial": amount_rial,
        }


async def zarinpal_verify(intent_id: str, authority: str, status_q: str) -> dict[str, Any]:
    meta = _INTENTS.get(intent_id)
    if not meta:
        return {"ok": False, "error": "unknown_intent"}
    if status_q != "OK":
        meta["status"] = "cancelled"
        return {"ok": False, "status": "cancelled", "intent": meta}

    amount_rial = meta.get("amount_rial") or int(round(meta["amount"]))
    payload = {
        "merchant_id": ZARINPAL_MERCHANT,
        "amount": amount_rial,
        "authority": authority,
    }
    url = f"{_zp_base()}/pg/v4/payment/verify.json"
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(url, json=payload)
        body = r.json()
        data = body.get("data") or {}
        code = data.get("code")
        if code in (100, 101):
            meta["status"] = "completed"
            meta["ref_id"] = data.get("ref_id")
            meta["provider_ref"] = authority
            return {"ok": True, "status": "completed", "ref_id": data.get("ref_id"), "intent": meta}
        meta["status"] = "failed"
        return {"ok": False, "status": "failed", "code": code, "intent": meta}


def stripe_webhook_construct(payload: bytes, sig_header: str) -> dict[str, Any]:
    if not STRIPE_WEBHOOK_SECRET:
        raise RuntimeError("STRIPE_WEBHOOK_SECRET not set")
    parts = dict(p.split("=", 1) for p in sig_header.split(",") if "=" in p)
    t = parts.get("t", "")
    v1 = parts.get("v1", "")
    signed = f"{t}.{payload.decode('utf-8')}".encode()
    expected = hmac.new(STRIPE_WEBHOOK_SECRET.encode(), signed, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, v1):
        logger.warning("Stripe signature mismatch")
        if os.getenv("ENVIRONMENT", "local") != "local":
            raise PermissionError("invalid stripe signature")
    return json.loads(payload.decode("utf-8"))


def apply_stripe_event(event: dict[str, Any]) -> dict[str, Any]:
    etype = event.get("type")
    obj = (event.get("data") or {}).get("object") or {}
    intent_id = (obj.get("metadata") or {}).get("intent_id") or obj.get("client_reference_id")
    if not intent_id:
        return {"handled": False, "reason": "no_intent"}
    meta = _INTENTS.get(intent_id) or {
        "intent_id": intent_id,
        "provider": "stripe",
        "status": "unknown",
    }
    if etype == "checkout.session.completed":
        meta["status"] = "completed"
        meta["provider_ref"] = obj.get("id")
        meta["amount_total"] = obj.get("amount_total")
    elif etype in ("checkout.session.expired", "payment_intent.payment_failed"):
        meta["status"] = "failed"
    _INTENTS[intent_id] = meta
    return {"handled": True, "intent": meta}


def get_intent(intent_id: str) -> Optional[dict[str, Any]]:
    return _INTENTS.get(intent_id)


def mark_demo_paid(intent_id: str) -> Optional[dict[str, Any]]:
    meta = _INTENTS.get(intent_id)
    if not meta:
        return None
    if meta.get("provider") != "demo":
        return meta
    meta["status"] = "completed_demo"
    return meta
