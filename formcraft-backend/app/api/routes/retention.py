"""Retention API routes (F044)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.supabase import get_supabase_client
from app.middleware.org_context import OrgContext, require_org_admin, get_org_context
from app.schemas.retention import (
    PolicyCreate,
    PolicyUpdate,
    HoldCreate,
    JobCreate,
    PrivacyRequestCreate,
    PrivacyRequestResolve,
    PreviewResponse,
)
from app.schemas.job import JobPauseRequest, RestoreRequest
from app.services.retention_policy_service import RetentionPolicyService
from app.services.retention_job_service import RetentionJobService
from app.services.preview_service import PreviewService
from app.services.legal_hold_service import LegalHoldService
from app.services.archive_manifest_service import ArchiveManifestService
from app.services.privacy_request_service import PrivacyRequestService

router = APIRouter(prefix="/retention", tags=["Retention"])


# ------------------------------------------------------------------
# Retention Policies
# ------------------------------------------------------------------

@router.post("/policies", status_code=201)
async def create_policy(
    body: PolicyCreate,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    client = get_supabase_client()
    service = RetentionPolicyService(client)
    return await service.create_policy(ctx.org_id, body, ctx.user_id)


@router.get("/policies")
async def list_policies(
    ctx: Annotated[OrgContext, Depends(get_org_context)],
    data_class: str | None = Query(None),
    action: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    client = get_supabase_client()
    service = RetentionPolicyService(client)
    return await service.list_policies(ctx.org_id, data_class, action, page, page_size)


@router.get("/policies/{policy_id}")
async def get_policy(
    policy_id: UUID,
    ctx: Annotated[OrgContext, Depends(get_org_context)],
):
    client = get_supabase_client()
    service = RetentionPolicyService(client)
    return await service.get_policy(ctx.org_id, policy_id)


@router.put("/policies/{policy_id}")
async def update_policy(
    policy_id: UUID,
    body: PolicyUpdate,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    client = get_supabase_client()
    service = RetentionPolicyService(client)
    return await service.update_policy(ctx.org_id, policy_id, body)


@router.delete("/policies/{policy_id}", status_code=204)
async def delete_policy(
    policy_id: UUID,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    client = get_supabase_client()
    service = RetentionPolicyService(client)
    await service.delete_policy(ctx.org_id, policy_id)
    return {}


@router.post("/policies/{policy_id}/preview")
async def preview_policy(
    policy_id: UUID,
    ctx: Annotated[OrgContext, Depends(get_org_context)],
):
    client = get_supabase_client()
    service = PreviewService(client)
    return await service.generate_preview(ctx.org_id, policy_id)


# ------------------------------------------------------------------
# Retention Jobs
# ------------------------------------------------------------------

@router.get("/jobs")
async def list_jobs(
    ctx: Annotated[OrgContext, Depends(get_org_context)],
    policy_id: UUID | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    client = get_supabase_client()
    service = RetentionJobService(client)
    # Reuse policy service to resolve org-scoped job query
    # For MVP, return empty list with pagination shape
    return {"items": [], "total": 0, "page": page, "page_size": page_size}


@router.post("/jobs", status_code=201)
async def create_job(
    body: JobCreate,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    client = get_supabase_client()
    service = RetentionJobService(client)
    return await service.create_job(ctx.org_id, body)


@router.get("/jobs/{job_id}")
async def get_job(
    job_id: UUID,
    ctx: Annotated[OrgContext, Depends(get_org_context)],
):
    client = get_supabase_client()
    # Direct query for MVP
    resp = client.table("retention_jobs").select("*").eq("id", str(job_id)).single().execute()
    return resp.data


@router.post("/jobs/{job_id}/pause")
async def pause_job(
    job_id: UUID,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    client = get_supabase_client()
    service = RetentionJobService(client)
    return await service.pause_job(ctx.org_id, job_id)


@router.post("/jobs/{job_id}/resume")
async def resume_job(
    job_id: UUID,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    client = get_supabase_client()
    service = RetentionJobService(client)
    return await service.resume_job(ctx.org_id, job_id)


# ------------------------------------------------------------------
# Legal Holds
# ------------------------------------------------------------------

@router.get("/holds")
async def list_holds(
    ctx: Annotated[OrgContext, Depends(get_org_context)],
    scope_type: str | None = Query(None),
    hold_type: str | None = Query(None),
):
    client = get_supabase_client()
    service = LegalHoldService(client)
    return await service.list_holds(ctx.org_id, scope_type, hold_type)


@router.post("/holds", status_code=201)
async def create_hold(
    body: HoldCreate,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    client = get_supabase_client()
    service = LegalHoldService(client)
    return await service.create_hold(ctx.org_id, body, ctx.user_id)


@router.delete("/holds/{hold_id}", status_code=204)
async def delete_hold(
    hold_id: UUID,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    client = get_supabase_client()
    service = LegalHoldService(client)
    await service.release_hold(ctx.org_id, hold_id)
    return {}


# ------------------------------------------------------------------
# Archive Manifests
# ------------------------------------------------------------------

@router.get("/manifests")
async def list_manifests(
    ctx: Annotated[OrgContext, Depends(get_org_context)],
    job_id: UUID | None = Query(None),
    integrity_status: str | None = Query(None),
):
    client = get_supabase_client()
    service = ArchiveManifestService(client)
    return await service.list_manifests(ctx.org_id, job_id, integrity_status)


@router.get("/manifests/{manifest_id}")
async def get_manifest(
    manifest_id: UUID,
    ctx: Annotated[OrgContext, Depends(get_org_context)],
):
    client = get_supabase_client()
    service = ArchiveManifestService(client)
    return await service.get_manifest(ctx.org_id, manifest_id)


@router.post("/manifests/{manifest_id}/restore")
async def restore_manifest(
    manifest_id: UUID,
    body: RestoreRequest,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    client = get_supabase_client()
    service = ArchiveManifestService(client)
    return await service.request_restore(ctx.org_id, manifest_id, body.reason)


# ------------------------------------------------------------------
# Privacy Requests
# ------------------------------------------------------------------

@router.get("/privacy-requests")
async def list_privacy_requests(
    ctx: Annotated[OrgContext, Depends(get_org_context)],
    status: str | None = Query(None),
    request_type: str | None = Query(None),
):
    client = get_supabase_client()
    service = PrivacyRequestService(client)
    return await service.list_requests(ctx.org_id, status, request_type)


@router.post("/privacy-requests", status_code=201)
async def create_privacy_request(
    body: PrivacyRequestCreate,
    ctx: Annotated[OrgContext, Depends(get_org_context)],
):
    client = get_supabase_client()
    service = PrivacyRequestService(client)
    return await service.create_request(ctx.org_id, body, ctx.user_id)


@router.post("/privacy-requests/{request_id}/resolve")
async def resolve_privacy_request(
    request_id: UUID,
    body: PrivacyRequestResolve,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    client = get_supabase_client()
    service = PrivacyRequestService(client)
    return await service.resolve_request(ctx.org_id, request_id, body)
