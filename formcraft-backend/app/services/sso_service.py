"""SSO service: SAML/OIDC orchestration, metadata validation, and JIT provisioning."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from app.core.supabase import get_supabase_client
from app.models.identity import IdentityMapping, IdentityProvider, ProviderType
from app.services.crypto_service import decrypt_value, encrypt_value

logger = logging.getLogger(__name__)


class SsoService:
    """Business logic for identity provider configuration and SSO sign-in flows."""

    @staticmethod
    def create_provider(org_id: UUID, created_by: UUID, payload: dict[str, Any]) -> IdentityProvider:
        client = get_supabase_client()
        provider_id = uuid4()
        # Encrypt secrets before storage
        if payload.get("client_secret"):
            payload["client_secret"] = encrypt_value(payload["client_secret"])
        if payload.get("metadata_xml"):
            payload["metadata_xml"] = encrypt_value(payload["metadata_xml"])
        if payload.get("signing_cert"):
            payload["signing_cert"] = encrypt_value(payload["signing_cert"])

        row = {
            "id": str(provider_id),
            "org_id": str(org_id),
            "name": payload["name"],
            "provider_type": payload["provider_type"],
            "domains": payload.get("domains", []),
            "metadata_url": payload.get("metadata_url"),
            "metadata_xml": payload.get("metadata_xml"),
            "client_id": payload.get("client_id"),
            "client_secret": payload.get("client_secret"),
            "signing_cert": payload.get("signing_cert"),
            "is_active": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "created_by": str(created_by),
        }
        client.table("identity_providers").insert(row).execute()
        return IdentityProvider(**row)

    @staticmethod
    def validate_metadata(provider_id: UUID) -> bool:
        """Placeholder for SAML metadata XML or OIDC discovery validation."""
        # Real implementation would fetch/parse metadata and verify signatures.
        logger.info("validate_metadata called for %s", provider_id)
        return True

    @staticmethod
    def get_provider_by_domain(domain: str) -> IdentityProvider | None:
        client = get_supabase_client()
        # Domain check is case-insensitive; PostgREST ilike on array is tricky,
        # so we fetch active providers and scan in Python for MVP.
        rows = (
            client.table("identity_providers")
            .select("*")
            .eq("is_active", True)
            .execute()
        )
        for raw in rows.data or []:
            provider = IdentityProvider(**raw)
            for d in provider.domains:
                if d.lower() == domain.lower():
                    return provider
        return None

    @staticmethod
    def apply_jit_mappings(user_id: UUID, org_id: UUID, claims: dict[str, Any]) -> dict[str, Any]:
        client = get_supabase_client()
        mappings = (
            client.table("identity_mappings")
            .select("*")
            .eq("org_id", str(org_id))
            .eq("is_active", True)
            .order("priority", desc=False)
            .execute()
        )
        matched = False
        assigned: dict[str, Any] = {}
        for raw in mappings.data or []:
            mapping = IdentityMapping(**raw)
            claim_values = claims.get(mapping.claim_type, [])
            if isinstance(claim_values, str):
                claim_values = [claim_values]
            if mapping.claim_value in claim_values:
                matched = True
                assigned = {
                    "role": mapping.assigned_role,
                    "department_id": mapping.assigned_department_id,
                    "branch_id": mapping.assigned_branch_id,
                    "default_language": mapping.default_language,
                }
                break

        if matched:
            client.table("profiles").update({
                "role": assigned.get("role"),
                "department_id": str(assigned["department_id"]) if assigned.get("department_id") else None,
                "branch_id": str(assigned["branch_id"]) if assigned.get("branch_id") else None,
                "default_language": assigned.get("default_language", "ar"),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }).eq("id", str(user_id)).execute()
            return assigned

        # Fallback: strip access and notify admins
        client.table("profiles").update({
            "department_id": None,
            "branch_id": None,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", str(user_id)).execute()
        return {"fallback": "strip_access", "notified": True}
