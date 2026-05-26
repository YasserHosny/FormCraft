from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from supabase import Client

from app.models.user import UserProfile
from app.schemas.offline_desk import (
    ConflictResolution,
    ConflictType,
    DeviceResponse,
    DeviceStatus,
    ManifestTemplate,
    OfflineManifestResponse,
    OfflinePolicyResponse,
    RegisterDeviceRequest,
    ResolveConflictResponse,
    RevokeDeviceResponse,
    SyncConflictResponse,
    SyncRequest,
    SyncResponse,
    SyncStatus,
)

DEFAULT_POLICY = OfflinePolicyResponse()


class OfflineDeskService:
    """Server authority for offline device policy, sync, and conflict decisions."""

    def __init__(self, client: Client):
        self.client = client

    async def register_device(self, payload: RegisterDeviceRequest, user: UserProfile) -> DeviceResponse:
        org_id = self._require_org(user)
        existing = self._single(
            self.client.table("offline_devices")
            .select("*")
            .eq("org_id", str(org_id))
            .eq("user_id", str(user.id))
            .eq("device_fingerprint", payload.device_fingerprint)
            .execute()
        )
        if existing:
            device_id = UUID(str(existing["id"]))
            if existing.get("status") != DeviceStatus.ACTIVE.value:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Device is revoked")
        else:
            device_id = uuid4()
            self.client.table("offline_devices").insert(
                {
                    "id": str(device_id),
                    "org_id": str(org_id),
                    "user_id": str(user.id),
                    "device_fingerprint": payload.device_fingerprint,
                    "display_name": payload.display_name,
                    "public_key": payload.public_key,
                    "status": DeviceStatus.ACTIVE.value,
                    "last_seen_at": self._now_iso(),
                    "created_by": str(user.id),
                }
            ).execute()
        return DeviceResponse(id=device_id, status=DeviceStatus.ACTIVE, policy=self.get_policy(org_id))

    async def get_manifest(self, device_id: UUID, user: UserProfile) -> OfflineManifestResponse:
        org_id = self._require_org(user)
        device = self._require_active_device(device_id, user)
        policy = self.get_policy(org_id)
        result = (
            self.client.table("templates")
            .select("id, name, version, language")
            .eq("org_id", str(org_id))
            .eq("status", "published")
            .limit(50)
            .execute()
        )
        templates = [
            ManifestTemplate(
                template_id=UUID(str(row["id"])),
                template_version=int(row.get("version") or 1),
                name=row.get("name") or "",
                language=row.get("language"),
                reference_snapshot_version=f"ref-{datetime.now(UTC).date().isoformat()}",
            )
            for row in (result.data or [])
        ]
        self.client.table("offline_devices").update({"last_seen_at": self._now_iso()}).eq("id", str(device["id"])).execute()
        return OfflineManifestResponse(
            device_id=device_id,
            expires_at=datetime.now(UTC) + timedelta(hours=policy.max_offline_age_hours),
            templates=templates,
            policy=policy,
        )

    async def sync(self, payload: SyncRequest, user: UserProfile) -> SyncResponse:
        org_id = self._require_org(user)
        self._require_active_device(payload.device_id, user)
        duplicate = self._single(
            self.client.table("offline_sync_operations")
            .select("*")
            .eq("org_id", str(org_id))
            .eq("idempotency_key", payload.idempotency_key)
            .execute()
        )
        if duplicate:
            return SyncResponse(
                operation_id=UUID(str(duplicate["id"])),
                status=SyncStatus(duplicate.get("status", SyncStatus.SUBMITTED.value)),
                submitted_id=UUID(str(duplicate["submitted_id"])) if duplicate.get("submitted_id") else None,
            )

        operation_id = uuid4()
        conflict = self._detect_conflict(payload, user)
        if conflict:
            self.client.table("offline_sync_operations").insert(self._operation_row(operation_id, payload, user, SyncStatus.CONFLICT)).execute()
            self.client.table("offline_sync_conflicts").insert(
                {
                    "id": str(conflict.id),
                    "sync_operation_id": str(operation_id),
                    "conflict_type": conflict.conflict_type.value,
                    "status": "open",
                    "blocking_reason": conflict.blocking_reason,
                    "created_by": str(user.id),
                }
            ).execute()
            return SyncResponse(operation_id=operation_id, status=SyncStatus.CONFLICT, conflicts=[conflict])

        submitted_id = uuid4()
        row = self._operation_row(operation_id, payload, user, SyncStatus.SUBMITTED)
        row["submitted_id"] = str(submitted_id)
        self.client.table("offline_sync_operations").insert(row).execute()
        return SyncResponse(operation_id=operation_id, status=SyncStatus.SUBMITTED, submitted_id=submitted_id)

    async def resolve_conflict(self, conflict_id: UUID, resolution: ConflictResolution, user: UserProfile) -> ResolveConflictResponse:
        self._require_org(user)
        self.client.table("offline_sync_conflicts").update(
            {"status": "resolved", "resolution": resolution.value, "resolved_by": str(user.id), "resolved_at": self._now_iso()}
        ).eq("id", str(conflict_id)).execute()
        return ResolveConflictResponse(id=conflict_id, status="resolved", resolution=resolution)

    async def revoke_device(self, device_id: UUID, user: UserProfile, reason: str) -> RevokeDeviceResponse:
        self._require_org(user)
        policy = self.get_policy(user.org_id)
        self.client.table("offline_devices").update(
            {"status": DeviceStatus.REVOKED.value, "revoked_at": self._now_iso(), "revoked_by": str(user.id), "revocation_reason": reason}
        ).eq("id", str(device_id)).execute()
        return RevokeDeviceResponse(id=device_id, status=DeviceStatus.REVOKED, wipe_on_next_contact=policy.wipe_on_revocation)

    def get_policy(self, org_id: UUID | None) -> OfflinePolicyResponse:
        if not org_id:
            return DEFAULT_POLICY
        row = self._single(self.client.table("offline_policies").select("*").eq("org_id", str(org_id)).execute())
        if not row:
            return DEFAULT_POLICY
        return OfflinePolicyResponse(
            max_offline_age_hours=row.get("max_offline_age_hours") or DEFAULT_POLICY.max_offline_age_hours,
            max_storage_mb=row.get("max_storage_mb") or DEFAULT_POLICY.max_storage_mb,
            wipe_on_revocation=row.get("wipe_on_revocation", DEFAULT_POLICY.wipe_on_revocation),
        )

    def _detect_conflict(self, payload: SyncRequest, user: UserProfile) -> SyncConflictResponse | None:
        if not user.is_active:
            return self._conflict(ConflictType.ACCOUNT_STATUS, "User account is not active.", [ConflictResolution.DISCARD])
        template = self._single(self.client.table("templates").select("id, version, status").eq("id", str(payload.template_id)).execute())
        if not template or template.get("status") != "published":
            return self._conflict(
                ConflictType.TEMPLATE_VERSION,
                "Template is no longer published for offline submission.",
                [ConflictResolution.DISCARD, ConflictResolution.RELOAD_TEMPLATE],
            )
        if int(template.get("version") or 0) != payload.template_version:
            return self._conflict(
                ConflictType.TEMPLATE_VERSION,
                "Template version changed while this device was offline.",
                [ConflictResolution.DISCARD, ConflictResolution.RELOAD_TEMPLATE],
            )
        return None

    def _require_active_device(self, device_id: UUID, user: UserProfile) -> dict:
        org_id = self._require_org(user)
        device = self._single(
            self.client.table("offline_devices").select("*").eq("id", str(device_id)).eq("org_id", str(org_id)).eq("user_id", str(user.id)).execute()
        )
        if not device:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offline device not found")
        if device.get("status") != DeviceStatus.ACTIVE.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Offline device is revoked")
        return device

    def _operation_row(self, operation_id: UUID, payload: SyncRequest, user: UserProfile, sync_status: SyncStatus) -> dict:
        return {
            "id": str(operation_id),
            "org_id": str(user.org_id),
            "device_id": str(payload.device_id),
            "user_id": str(user.id),
            "template_id": str(payload.template_id),
            "template_version": payload.template_version,
            "idempotency_key": payload.idempotency_key,
            "operation_type": payload.operation_type.value,
            "status": sync_status.value,
            "payload_digest": payload.payload_digest,
            "client_created_at": payload.client_created_at.isoformat(),
            "server_received_at": self._now_iso(),
            "created_by": str(user.id),
        }

    def _conflict(self, conflict_type: ConflictType, reason: str, resolutions: list[ConflictResolution]) -> SyncConflictResponse:
        return SyncConflictResponse(id=uuid4(), conflict_type=conflict_type, blocking_reason=reason, allowed_resolutions=resolutions)

    def _require_org(self, user: UserProfile) -> UUID:
        if not user.org_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization context is required")
        return user.org_id

    def _single(self, result) -> dict | None:
        data = getattr(result, "data", None)
        if isinstance(data, list):
            return data[0] if data else None
        return data

    def _now_iso(self) -> str:
        return datetime.now(UTC).isoformat()
