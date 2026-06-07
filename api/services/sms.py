"""SMS OTP delivery — Kavenegar (Iran) or Twilio."""

import logging

import httpx

from api.core.config import settings

logger = logging.getLogger(__name__)


async def send_otp_sms(phone: str, code: str) -> bool:
    provider = (settings.SMS_PROVIDER or "none").lower()
    if provider == "kavenegar":
        return await _kavenegar(phone, code)
    if provider == "twilio":
        return await _twilio(phone, code)
    if settings.OTP_DEV_MODE:
        logger.info("OTP dev mode — SMS skipped for %s code %s", phone, code)
        return True
    logger.error("SMS_PROVIDER not configured and OTP_DEV_MODE=false")
    return False


async def _kavenegar(phone: str, code: str) -> bool:
    if not settings.KAVENEGAR_API_KEY:
        return False
    receptor = phone.lstrip("+")
    if receptor.startswith("98"):
        receptor = "0" + receptor[2:]
    url = f"https://api.kavenegar.com/v1/{settings.KAVENEGAR_API_KEY}/verify/lookup.json"
    params = {
        "receptor": receptor,
        "token": code,
        "template": settings.KAVENEGAR_TEMPLATE,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.get(url, params=params)
        if res.status_code == 200:
            data = res.json()
            return data.get("return", {}).get("status") == 200
        logger.error("Kavenegar error %s %s", res.status_code, res.text)
        return False


async def _twilio(phone: str, code: str) -> bool:
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        return False
    try:
        from twilio.rest import Client

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=f"Econojin code: {code}",
            from_=settings.TWILIO_FROM_NUMBER,
            to=phone if phone.startswith("+") else f"+{phone}",
        )
        return True
    except Exception as exc:
        logger.error("Twilio error: %s", exc)
        return False
