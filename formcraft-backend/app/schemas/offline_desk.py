from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class DeviceStatus(StrEnum):
    ACTIVE = "active"
    REVOKED = "revoked"
    WIPED = "wiped"


class SyncStatus(StrEnum):
    PENDING = "pending"
    SYNCING = "syncing"
    SUBMITTED = "submitted"
    FAILED = "failed"
    CONFLICT = "conflict"


class SyncOperationType(StrEnum):
    DRAFT = "draft"
    SUBMISSION = "submission"
    ATTACHMENT = "attachment"
    STATUS_UPDATE = "status_update"


class ConflictType(StrEnum):
    TEMPLATE_VERSION = "template_version"
    CUSTOMER_PROFILE = "customer_profile"
    REFERENCE_DATA = "reference_data"
    USER_PERMISSION = "user_permission"
    DUPLICATE_SUBMISSION = "duplicate_submission"
    ACCOUNT_STATUS = "account_status"
    DEVICE_REVOKED = "device_revoked"


class ConflictResolution(StrEnum):
    DISCARD = "discard"
    RELOAD_TEMPLATE = "reload_template"
    MANAGER_APPROVE = "manager_approve"
    RETRY = "retry"


class OfflinePolicyResponse(BaseModel):
    max_offline_age_hours: int = 168
    max_storage_mb: int = 250
    wipe_on_revocation: bool = True


class RegisterDeviceRequest(BaseModel):
    device_fingerprint: str = Field(min_length=8, max_length=256)
    display_name: str | None = Field(default=None, max_length=120)
    public_key: str = Field(min_length=16)


class DeviceResponse(BaseModel):
    id: UUID
    status: DeviceStatus
    policy: OfflinePolicyResponse


class ManifestTemplate(BaseModel):
    template_id: UUID
    template_version: int
    name: str
    language: str | None = None
    reference_snapshot_version: str | None = None


class OfflineManifestResponse(BaseModel):
    device_id: UUID
    expires_at: datetime
    templates: list[ManifestTemplate]
    policy: OfflinePolicyResponse


class SyncRequest(BaseModel):
    device_id: UUID
    idempotency_key: str = Field(min_length=8, max_length=128)
    operation_type: SyncOperationType
    template_id: UUID
    template_version: int = Field(ge=1)
    payload_digest: str = Field(min_length=8, max_length=160)
    client_created_at: datetime
    encrypted_payload: str = Field(min_length=1)


class SyncConflictResponse(BaseModel):
    id: UUID
    conflict_type: ConflictType
    blocking_reason: str
    allowed_resolutions: list[ConflictResolution]


class SyncResponse(BaseModel):
    operation_id: UUID
    status: SyncStatus
    submitted_id: UUID | None = None
    conflicts: list[SyncConflictResponse] = []


class ResolveConflictRequest(BaseModel):
    resolution: ConflictResolution


class ResolveConflictResponse(BaseModel):
    id: UUID
    status: str
    resolution: ConflictResolution


class RevokeDeviceRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


class RevokeDeviceResponse(BaseModel):
    id: UUID
    status: DeviceStatus
    wipe_on_next_contact: bool
