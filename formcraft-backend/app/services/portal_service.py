"""Portal orchestration service for config lookup, session pinning, and submission."""

import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.core.audit import AuditLogger
from app.schemas.portal import (
    PortalAnalyticsResponse,
    PortalConfiguration,
    PortalConfigurationUpdate,
    PortalTemplateListResponse,
    PublicFormSession,
    PublicPortalSettings,
    PublicSubmissionRequest,
    PublicSubmissionResponse,
)
from app.services.condition_engine import ConditionEngine
from app.services.validators.registry import ValidatorRegistry
from app.services.validators.egypt import EgyptNationalIdValidator, EgyptIbanValidator, EgyptPhoneValidator
from app.services.validators.saudi import SaudiNationalIdValidator, SaudiIbanValidator, SaudiVatValidator
from app.services.validators.uae import UaeIbanValidator, UaeTrnValidator

logger = logging.getLogger(__name__)

SESSION_TTL_MINUTES = 120
PDF_TOKEN_TTL_MINUTES = 30
REFERENCE_PREFIX = "PUB-"
MAX_AUDIT_SUMMARY_FIELDS = 50
MAX_AUDIT_SUMMARY_LENGTH = 200

_validator_registry = ValidatorRegistry()
_validator_registry.register(EgyptNationalIdValidator())
_validator_registry.register(EgyptIbanValidator())
_validator_registry.register(EgyptPhoneValidator())
_validator_registry.register(SaudiNationalIdValidator())
_validator_registry.register(SaudiIbanValidator())
_validator_registry.register(SaudiVatValidator())
_validator_registry.register(UaeIbanValidator())
_validator_registry.register(UaeTrnValidator())

_condition_engine = ConditionEngine()


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _generate_opaque_token() -> str:
    return secrets.token_urlsafe(32)


def _generate_reference_number() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    rand = secrets.token_hex(4).upper()
    return f"{REFERENCE_PREFIX}{ts}-{rand}"


def _build_redacted_summary(field_values: dict) -> dict:
    """Build a bounded, redacted field summary for audit logs."""
    summary = {}
    for idx, (key, value) in enumerate(field_values.items()):
        if idx >= MAX_AUDIT_SUMMARY_FIELDS:
            summary["_truncated"] = True
            break
        s = str(value)
        if len(s) > MAX_AUDIT_SUMMARY_LENGTH:
            s = s[:MAX_AUDIT_SUMMARY_LENGTH] + "..."
        # Redact likely sensitive keys
        lowered = key.lower()
        if any(
            x in lowered
            for x in ("password", "secret", "token", "iban", "card", "cvv", "pin")
        ):
            s = "[REDACTED]"
        summary[key] = s
    return summary


class PortalService:
    """Service for portal configuration, session management, and public submission orchestration."""

    def __init__(self, client: Client):
        self.client = client

    # ------------------------------------------------------------------
    # Hashing / token helpers
    # ------------------------------------------------------------------

    def hash_token(self, token: str) -> str:
        return _hash(token)

    def hash_contact(self, contact: str) -> str:
        return _hash(contact.lower().strip())

    def hash_ip(self, ip: str) -> str:
        return _hash(ip.strip())

    def hash_browser_key(self, browser_key: str) -> str:
        return _hash(browser_key.strip())

    def generate_session_token(self) -> str:
        return _generate_opaque_token()

    def generate_pdf_download_token(self) -> str:
        return _generate_opaque_token()

    # ------------------------------------------------------------------
    # Configuration lookup
    # ------------------------------------------------------------------

    async def get_portal_config_by_slug(
        self, org_slug: str, public_slug: str
    ) -> PortalConfiguration | None:
        """Resolve an enabled portal configuration by org slug and public slug."""
        # Lookup org by slug or custom domain
        org_resp = (
            self.client.table("organizations")
            .select("id")
            .or_(f"slug.eq.{org_slug},custom_domain.eq.{org_slug}")
            .limit(1)
            .execute()
        )
        orgs = org_resp.data or []
        if not orgs:
            return None
        org_id = orgs[0]["id"]

        config_resp = (
            self.client.table("portal_configurations")
            .select(
                "*, templates!inner(id, name, version, status, country, language_default)"
            )
            .eq("org_id", org_id)
            .eq("public_slug", public_slug)
            .eq("enabled", True)
            .limit(1)
            .execute()
        )
        rows = config_resp.data or []
        if not rows:
            return None
        row = rows[0]
        template = row.get("templates", {})
        return self._row_to_config(row, template)

    async def get_portal_config_by_template(
        self, org_id: UUID, template_id: UUID
    ) -> PortalConfiguration | None:
        resp = (
            self.client.table("portal_configurations")
            .select("*, templates!inner(id, name, version, status, country, language_default)")
            .eq("org_id", str(org_id))
            .eq("template_id", str(template_id))
            .limit(1)
            .execute()
        )
        rows = resp.data or []
        if not rows:
            return None
        row = rows[0]
        template = row.get("templates", {})
        return self._row_to_config(row, template)

    def _row_to_config(self, row: dict, template: dict) -> PortalConfiguration:
        org_id = row["org_id"]
        org_resp = (
            self.client.table("organizations")
            .select("slug, custom_domain")
            .eq("id", org_id)
            .limit(1)
            .execute()
        )
        orgs = org_resp.data or []
        org = orgs[0] if orgs else {}
        slug = org.get("slug", "")
        custom_domain = org.get("custom_domain")
        public_path = f"/forms/{slug}/{row['public_slug']}"
        public_url = f"https://{custom_domain}{public_path}" if custom_domain else public_path

        return PortalConfiguration(
            template_id=row["template_id"],
            public_slug=row["public_slug"],
            public_url=public_url,
            public_qr_svg=None,
            enabled=row["enabled"],
            verification_required=row["verification_required"],
            allowed_otp_modes=row.get("allowed_otp_modes", []),
            captcha_enabled=row["captcha_enabled"],
            captcha_provider=row.get("captcha_provider"),
            allow_pdf_download=row["allow_pdf_download"],
            send_email_confirmation=row["send_email_confirmation"],
            rate_limit_max=row["rate_limit_max"],
            rate_limit_window_minutes=row["rate_limit_window_minutes"],
        )

    # ------------------------------------------------------------------
    # Session creation
    # ------------------------------------------------------------------

    async def create_portal_session(
        self,
        config: PortalConfiguration,
        template: dict,
        ip_address: str,
        browser_fingerprint: str | None = None,
    ) -> tuple[str, UUID]:
        """Create a pinned portal session and return the opaque token and session ID."""
        token = self.generate_session_token()
        token_hash = self.hash_token(token)
        ip_hash = self.hash_ip(ip_address)
        browser_hash = self.hash_browser_key(browser_fingerprint) if browser_fingerprint else None
        expires = datetime.now(timezone.utc) + timedelta(minutes=SESSION_TTL_MINUTES)

        data = {
            "org_id": str(config.template_id),  # will be overridden below using org from config
            "portal_configuration_id": str(config.template_id),  # placeholder; corrected below
            "template_id": str(config.template_id),
            "template_version": template.get("version", 1),
            "session_token_hash": token_hash,
            "ip_hash": ip_hash,
            "browser_fingerprint_hash": browser_hash,
            "expires_at": expires.isoformat(),
        }

        # Resolve org_id from config row
        config_row = (
            self.client.table("portal_configurations")
            .select("org_id, id")
            .eq("template_id", str(config.template_id))
            .limit(1)
            .execute()
        )
        rows = config_row.data or []
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portal configuration not found",
            )
        data["org_id"] = rows[0]["org_id"]
        data["portal_configuration_id"] = rows[0]["id"]

        resp = self.client.table("portal_sessions").insert(data).execute()
        session_id = resp.data[0]["id"]
        return token, UUID(session_id)

    async def get_session_by_token(self, token: str) -> dict | None:
        """Fetch a non-expired portal session by its opaque token."""
        token_hash = self.hash_token(token)
        now = datetime.now(timezone.utc).isoformat()
        resp = (
            self.client.table("portal_sessions")
            .select(
                "*, portal_configurations!inner(*, templates!inner(id, name, version, status, country, language_default, pages(id, elements(*))))"
            )
            .eq("session_token_hash", token_hash)
            .gt("expires_at", now)
            .limit(1)
            .execute()
        )
        rows = resp.data or []
        if not rows:
            return None
        row = rows[0]
        if row["status"] == "expired":
            return None
        return row

    def _session_to_public_form(self, session: dict) -> PublicFormSession:
        config = session.get("portal_configurations", {})
        template = config.get("templates", {})
        pages = template.get("pages", [])
        fields = []
        for page in pages:
            for el in page.get("elements", []):
                fields.append(el)
        settings = PublicPortalSettings(
            otp_required=config.get("verification_required", False),
            allowed_otp_modes=config.get("allowed_otp_modes", []),
            captcha_enabled=config.get("captcha_enabled", False),
            captcha_provider=config.get("captcha_provider"),
            allow_pdf_download=config.get("allow_pdf_download", False),
        )
        return PublicFormSession(
            session_token="",  # caller must attach the real token
            template_id=template.get("id"),
            template_version=session["template_version"],
            title=template.get("name", ""),
            language_default=template.get("language_default", "ar"),
            fields=fields,
            settings=settings,
        )

    # ------------------------------------------------------------------
    # Submission orchestration
    # ------------------------------------------------------------------

    async def submit_public_form(
        self,
        session: dict,
        request: PublicSubmissionRequest,
        ip_address: str,
    ) -> PublicSubmissionResponse:
        """Orchestrate public form submission with validation parity and metadata."""
        if session["status"] in ("submitted", "expired", "locked"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Session already submitted or expired",
            )

        config = session.get("portal_configurations", {})
        template = config.get("templates", {})
        template_id = UUID(template["id"])
        template_version = session["template_version"]
        org_id = UUID(session["org_id"])
        portal_configuration_id = UUID(session["portal_configuration_id"])
        portal_session_id = UUID(session["id"])

        # Validation parity with existing services
        elements = []
        for page in template.get("pages", []):
            elements.extend(page.get("elements", []))

        visible_keys = _condition_engine.evaluate_visibility(elements, request.field_values)
        clean_values = _condition_engine.strip_hidden_values(request.field_values, visible_keys)
        required_keys = _condition_engine.evaluate_required(elements, clean_values, visible_keys)
        validation_errors = []
        for key in required_keys:
            val = clean_values.get(key)
            if val is None or val == "":
                validation_errors.append({"field": key, "error": "required"})

        # Run deterministic validators
        country = template.get("country", "SA")
        for el in elements:
            key = el.get("key")
            if not key:
                continue
            val = clean_values.get(key)
            if val is None or val == "":
                continue
            validator_type = el.get("validation_type")
            if validator_type:
                ok, msg = _validator_registry.validate(validator_type, str(val), country=country)
                if not ok:
                    validation_errors.append({"field": key, "error": msg})

        if validation_errors:
            await self._audit(
                org_id=org_id,
                portal_session_id=portal_session_id,
                action="public_submission_validation_failed",
                metadata={"errors": validation_errors[:20]},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"validation_errors": validation_errors},
            )

        # Compute tafqeet for numeric fields
        tafqeet_map = {}
        for el in elements:
            key = el.get("key")
            if not key:
                continue
            if el.get("type") == "number" and clean_values.get(key) is not None:
                try:
                    from app.services.tafqeet.service import TafqeetService
                    tafqeet_service = TafqeetService()
                    tafqeet_map[key] = tafqeet_service.convert(
                        float(clean_values[key]), language=template.get("language_default", "ar")
                    )
                except Exception:
                    pass

        reference_number = _generate_reference_number()

        # Insert submission
        submission_data = {
            "template_id": str(template_id),
            "template_version": template_version,
            "field_values": clean_values,
            "reference_number": reference_number,
            "org_id": str(org_id),
            "source": "public_portal",
            "status": "submitted",
        }
        sub_resp = self.client.table("submissions").insert(submission_data).execute()
        submission_id = UUID(sub_resp.data[0]["id"])

        # Email confirmation
        email_status = "not_requested"
        email_failure_reason = None
        if config.get("send_email_confirmation", False):
            email_status = "queued"
            try:
                # Attempt to send confirmation via existing notification infrastructure
                contact = clean_values.get("email") or clean_values.get("email_address")
                if contact:
                    from app.services.notification_service import NotificationService
                    notif_service = NotificationService(self.client)
                    await notif_service.send_email(
                        to=contact,
                        subject="تأكيد الإرسال / Submission Confirmation",
                        body=f"رقم المرجع: {reference_number}",
                    )
                    email_status = "sent"
                else:
                    email_status = "failed"
                    email_failure_reason = "no_email_field"
            except Exception as exc:
                email_status = "failed"
                email_failure_reason = str(exc)[:200]
                logger.warning("Email confirmation failed for submission %s: %s", submission_id, exc)

        # Public submission metadata
        pdf_token = None
        pdf_token_hash = None
        pdf_expires = None
        if config.get("allow_pdf_download", False):
            pdf_token = self.generate_pdf_download_token()
            pdf_token_hash = self.hash_token(pdf_token)
            pdf_expires = datetime.now(timezone.utc) + timedelta(minutes=PDF_TOKEN_TTL_MINUTES)

        audit_summary = _build_redacted_summary(clean_values)

        meta_data = {
            "org_id": str(org_id),
            "submission_id": str(submission_id),
            "portal_configuration_id": str(portal_configuration_id),
            "portal_session_id": str(portal_session_id),
            "source": "public_portal",
            "template_version": template_version,
            "verified_contact_mode": session.get("verified_contact_mode"),
            "verified_contact_hash": session.get("verified_contact_hash"),
            "submission_ip_hash": self.hash_ip(ip_address),
            "captcha_verified": False,  # set by caller if verified
            "audit_field_summary": audit_summary,
            "pdf_download_token_hash": pdf_token_hash,
            "pdf_download_expires_at": pdf_expires.isoformat() if pdf_expires else None,
            "email_confirmation_status": email_status,
            "email_confirmation_sent_at": datetime.now(timezone.utc).isoformat() if email_status in ("sent", "queued") else None,
            "email_confirmation_failure_reason": email_failure_reason,
        }
        self.client.table("public_submission_metadata").insert(meta_data).execute()

        # Transition session to submitted
        self.client.table("portal_sessions").update({"status": "submitted"}).eq("id", str(portal_session_id)).execute()

        # Audit success
        await self._audit(
            org_id=org_id,
            portal_session_id=portal_session_id,
            action="public_submission_succeeded",
            metadata={
                "reference_number": reference_number,
                "submission_id": str(submission_id),
                "template_version": template_version,
                "field_summary_keys": list(audit_summary.keys())[:MAX_AUDIT_SUMMARY_FIELDS],
            },
        )

        pdf_download_url = None
        if pdf_token:
            pdf_download_url = f"/api/public/submissions/{reference_number}/pdf?token={pdf_token}"

        return PublicSubmissionResponse(
            reference_number=reference_number,
            pdf_download_url=pdf_download_url,
            email_confirmation_status=email_status,
        )

    # ------------------------------------------------------------------
    # Admin portal methods
    # ------------------------------------------------------------------

    async def list_portal_templates(self, org_id: UUID) -> PortalTemplateListResponse:
        resp = (
            self.client.table("portal_configurations")
            .select("*, templates!inner(id, name, version, status)")
            .eq("org_id", str(org_id))
            .execute()
        )
        rows = resp.data or []
        items = []
        for row in rows:
            template = row.get("templates", {})
            items.append(self._row_to_config(row, template))
        return PortalTemplateListResponse(items=items)

    async def update_portal_configuration(
        self,
        org_id: UUID,
        template_id: UUID,
        update: PortalConfigurationUpdate,
        user_id: UUID,
    ) -> PortalConfiguration:
        # Validate published template guard
        template_resp = (
            self.client.table("templates")
            .select("status")
            .eq("id", str(template_id))
            .eq("org_id", str(org_id))
            .limit(1)
            .execute()
        )
        templates = template_resp.data or []
        if not templates:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found",
            )
        if update.enabled and templates[0].get("status") != "published":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Template must be published before enabling portal",
            )

        # Validate OTP modes
        if update.verification_required and not update.allowed_otp_modes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Select OTP modes when verification is required",
            )

        # Validate CAPTCHA provider
        if update.captcha_enabled and not update.captcha_provider:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Select a CAPTCHA provider when CAPTCHA is enabled",
            )

        # Slug uniqueness within org
        existing = (
            self.client.table("portal_configurations")
            .select("id")
            .eq("org_id", str(org_id))
            .eq("public_slug", update.public_slug)
            .neq("template_id", str(template_id))
            .limit(1)
            .execute()
        )
        if (existing.data or []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Public slug already in use",
            )

        data = {
            "public_slug": update.public_slug,
            "enabled": update.enabled,
            "verification_required": update.verification_required,
            "allowed_otp_modes": update.allowed_otp_modes,
            "captcha_enabled": update.captcha_enabled,
            "captcha_provider": update.captcha_provider,
            "allow_pdf_download": update.allow_pdf_download,
            "send_email_confirmation": update.send_email_confirmation,
            "rate_limit_max": update.rate_limit_max,
            "rate_limit_window_minutes": update.rate_limit_window_minutes,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        resp = (
            self.client.table("portal_configurations")
            .update(data)
            .eq("org_id", str(org_id))
            .eq("template_id", str(template_id))
            .execute()
        )
        rows = resp.data or []
        if not rows:
            # Upsert if row does not exist
            data["org_id"] = str(org_id)
            data["template_id"] = str(template_id)
            data["created_by"] = str(user_id)
            resp = self.client.table("portal_configurations").insert(data).execute()
            rows = resp.data

        row = rows[0]
        template = template_resp.data[0] if template_resp.data else {}

        action = "portal_enabled" if update.enabled else "portal_disabled"
        await self._audit(
            org_id=org_id,
            portal_session_id=None,
            action=action,
            metadata={"template_id": str(template_id), "public_slug": update.public_slug},
        )

        return self._row_to_config(row, template)

    async def get_portal_analytics(
        self,
        org_id: UUID,
        template_id: UUID | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> PortalAnalyticsResponse:
        query = self.client.table("public_submission_metadata").select("*").eq("org_id", str(org_id))
        if template_id:
            # join through portal_configuration_id to filter by template
            pass
        if date_from:
            query = query.gte("created_at", date_from)
        if date_to:
            query = query.lte("created_at", date_to)
        resp = query.execute()
        rows = resp.data or []

        submission_count = len(rows)
        email_confirmation_failure_count = sum(
            1 for r in rows if r.get("email_confirmation_status") == "failed"
        )

        # OTP stats
        otp_query = self.client.table("portal_otp_verifications").select("*").eq("org_id", str(org_id))
        if date_from:
            otp_query = otp_query.gte("created_at", date_from)
        if date_to:
            otp_query = otp_query.lte("created_at", date_to)
        otp_resp = otp_query.execute()
        otp_rows = otp_resp.data or []
        otp_sent_count = sum(1 for r in otp_rows if r.get("sent_at"))
        otp_failure_count = sum(
            1 for r in otp_rows if r.get("status") in ("failed", "locked", "provider_failed")
        )

        # Rate limited count
        rate_query = (
            self.client.table("portal_rate_limit_events")
            .select("*")
            .eq("org_id", str(org_id))
            .eq("allowed", False)
        )
        if date_from:
            rate_query = rate_query.gte("created_at", date_from)
        if date_to:
            rate_query = rate_query.lte("created_at", date_to)
        rate_resp = rate_query.execute()
        rate_limited_count = len(rate_resp.data or [])

        return PortalAnalyticsResponse(
            submission_count=submission_count,
            otp_sent_count=otp_sent_count,
            otp_failure_count=otp_failure_count,
            rate_limited_count=rate_limited_count,
            email_confirmation_failure_count=email_confirmation_failure_count,
        )

    # ------------------------------------------------------------------
    # Audit helpers
    # ------------------------------------------------------------------

    async def _audit(
        self,
        org_id: UUID,
        portal_session_id: UUID | None,
        action: str,
        metadata: dict | None = None,
    ) -> None:
        try:
            data = {
                "org_id": str(org_id),
                "action": action,
                "resource_type": "portal",
                "metadata": metadata or {},
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            if portal_session_id:
                data["portal_session_id"] = str(portal_session_id)
            self.client.table("audit_logs").insert(data).execute()
        except Exception as exc:
            logger.warning("Audit log failed for action %s: %s", action, exc)
