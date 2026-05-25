"""CAPTCHA verification adapter for hCaptcha and reCAPTCHA."""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

VERIFY_URLS = {
    "hcaptcha": "https://hcaptcha.com/siteverify",
    "recaptcha": "https://www.google.com/recaptcha/api/siteverify",
}


class CaptchaService:
    """Adapter for verifying CAPTCHA tokens via hCaptcha or reCAPTCHA."""

    def __init__(self, provider: str | None = None, secret_key: str | None = None):
        self.provider = provider
        self.secret_key = secret_key

    async def verify(self, token: str | None) -> tuple[bool, str | None]:
        """Verify a CAPTCHA token. Returns (success, error_message)."""
        if not self.provider or not self.secret_key:
            return True, None  # CAPTCHA not configured; treat as pass in dev

        if not token:
            return False, "CAPTCHA token required"

        url = VERIFY_URLS.get(self.provider)
        if not url:
            return False, f"Unknown CAPTCHA provider: {self.provider}"

        payload = {
            "secret": self.secret_key,
            "response": token,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, data=payload)
                response.raise_for_status()
                data: dict[str, Any] = response.json()
                success = data.get("success", False)
                if not success:
                    errors = data.get("error-codes", ["unknown"])
                    return False, f"CAPTCHA verification failed: {', '.join(errors)}"
                return True, None
        except httpx.HTTPError as exc:
            logger.warning("CAPTCHA verification HTTP error: %s", exc)
            return False, "CAPTCHA verification service error"
        except Exception as exc:
            logger.warning("CAPTCHA verification unexpected error: %s", exc)
            return False, "CAPTCHA verification error"
