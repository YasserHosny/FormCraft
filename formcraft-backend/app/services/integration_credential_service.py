import hashlib
import hmac
import secrets


class IntegrationCredentialService:
    """F32 scoped integration credential service."""

    SECRET_PREFIX = "fc_live_"

    def __init__(self, supabase_client):
        self.client = supabase_client

    @classmethod
    def generate_secret(cls) -> tuple[str, str, str]:
        """Create a one-time plaintext secret plus persistent prefix and hash."""
        secret = f"{cls.SECRET_PREFIX}{secrets.token_urlsafe(32)}"
        return secret, cls.prefix_for_secret(secret), cls.hash_secret(secret)

    @staticmethod
    def hash_secret(secret: str) -> str:
        return hashlib.sha256(secret.encode("utf-8")).hexdigest()

    @staticmethod
    def prefix_for_secret(secret: str) -> str:
        return secret[:16]

    @classmethod
    def verify_secret(cls, secret: str, expected_hash: str) -> bool:
        return hmac.compare_digest(cls.hash_secret(secret), expected_hash)

    @staticmethod
    def has_scope(scopes: list[str], required_scope: str) -> bool:
        return required_scope in scopes

    async def create_credential(self, org_id, actor_id, name, scopes):
        """Create a new integration credential."""
        from uuid import uuid4
        from datetime import datetime, timezone
        secret, prefix, hash_value = self.generate_secret()
        row = {
            "id": str(uuid4()),
            "org_id": str(org_id),
            "created_by": str(actor_id),
            "name": name,
            "prefix": prefix,
            "secret_hash": hash_value,
            "scopes": scopes,
            "status": "active",
            "expires_at": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        result = self.client.table("integration_credentials").insert(row).execute()
        if result.data:
            data = dict(result.data[0])
            data["secret"] = secret  # One-time only
            return data
        return None

    async def list_credentials(self, org_id):
        """List credentials for an org."""
        result = (
            self.client.table("integration_credentials")
            .select("id, name, prefix, scopes, status, expires_at, last_used_at, created_at")
            .eq("org_id", str(org_id))
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []

    async def revoke_credential(self, org_id, credential_id, actor_id):
        """Revoke a credential."""
        from datetime import datetime, timezone
        result = (
            self.client.table("integration_credentials")
            .update({"status": "revoked", "updated_at": datetime.now(timezone.utc).isoformat()})
            .eq("id", str(credential_id))
            .eq("org_id", str(org_id))
            .execute()
        )
        return result.data[0] if result.data else None
