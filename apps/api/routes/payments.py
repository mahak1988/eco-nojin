"""FastAPI routes: /api/v1/payments/*"""
from __future__ import annotations

import os
from typing import Any, Optional

from fastapi import APIRouter, Header, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from apps.api.services.payment_gateway import (
    apply_stripe_event,
    create_checkout,
    gateway_status,
    get_intent,
    mark_demo_paid,
    stripe_webhook_construct,
    zarinpal_verify,
)

router = APIRouter(prefix="/api/v1/payments", tags=["Payments"])
PUBLIC_WEB_URL = os.getenv("PUBLIC_WEB_URL", "http://localhost:5173").rstrip("/")


class CheckoutIn(BaseModel):
    amount: float = Field(..., gt=0)
    currency: str = "USD"
    description: str = "Eco Nojin payment"
    invoice_id: Optional[str] = None
    provider: str = "auto"
    customer_email: Optional[str] = None


@router.get("/status")
async def status() -> dict[str, Any]:
    return gateway_status()


@router.post("/checkout")
async def checkout(body: CheckoutIn) -> dict[str, Any]:
    try:
        return await create_checkout(
            amount=body.amount,
            currency=body.currency,
            description=body.description,
            invoice_id=body.invoice_id,
            provider=body.provider,
            customer_email=body.customer_email,
        )
    except ValueError as e:
        raise HTTPException(400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(503, detail=str(e)) from e


@router.get("/intent/{intent_id}")
async def intent(intent_id: str) -> dict[str, Any]:
    m = get_intent(intent_id)
    if not m:
        raise HTTPException(404, detail="intent not found")
    return m


@router.post("/demo/complete/{intent_id}")
async def demo_complete(intent_id: str) -> dict[str, Any]:
    m = mark_demo_paid(intent_id)
    if not m:
        raise HTTPException(404, detail="intent not found")
    return m


@router.get("/zarinpal/callback")
async def zarinpal_callback(
    intent: str = Query(...),
    Authority: str = Query(""),
    Status: str = Query(""),
) -> RedirectResponse:
    result = await zarinpal_verify(intent, Authority, Status)
    if result.get("ok"):
        return RedirectResponse(
            f"{PUBLIC_WEB_URL}/payments/success?intent={intent}&ref={result.get('ref_id', '')}",
            status_code=302,
        )
    return RedirectResponse(
        f"{PUBLIC_WEB_URL}/payments/cancel?intent={intent}&reason={result.get('status', 'fail')}",
        status_code=302,
    )


@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
) -> dict[str, Any]:
    payload = await request.body()
    try:
        event = stripe_webhook_construct(payload, stripe_signature or "")
    except PermissionError as e:
        raise HTTPException(400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(400, detail=f"webhook error: {e}") from e
    return apply_stripe_event(event)
