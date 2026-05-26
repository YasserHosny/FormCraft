"""MFA routes: enrollment, challenge, verify, recovery."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.models.identity import MfaMethodType
from app.models.user import UserProfile
from app.schemas.identity import (
    MfaEnrollRequest,
    MfaEnrollResponse,
    MfaVerifyRequest,
    MfaVerifyResponse,
    MfaChallengeResponse,
    MfaChallengeVerifyResponse,
    MfaRecoveryRequest,
    MfaRecoveryResponse,
)
from app.services.mfa_service import MfaService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/mfa", tags=["MFA"])


@router.post("/enroll", response_model=MfaEnrollResponse, status_code=status.HTTP_201_CREATED)
async def enroll(
    body: MfaEnrollRequest,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    try:
        result = MfaService.begin_enrollment(
            user_id=current_user.id,
            method_type=body.method_type,
            phone_number=body.phone_number,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return MfaEnrollResponse(**result)


@router.post("/enroll/{enrollment_id}/verify", response_model=MfaVerifyResponse)
async def verify_enrollment(
    enrollment_id: str,
    body: MfaVerifyRequest,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    from uuid import UUID
    try:
        result = MfaService.verify_enrollment(
            enrollment_id=UUID(enrollment_id),
            user_id=current_user.id,
            code=body.code,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return MfaVerifyResponse(**result)


@router.post("/challenge", response_model=MfaChallengeResponse)
async def challenge(
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    try:
        result = MfaService.generate_challenge(user_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return MfaChallengeResponse(**result)


@router.post("/challenge/{challenge_id}/verify", response_model=MfaChallengeVerifyResponse)
async def verify_challenge(
    challenge_id: str,
    body: MfaVerifyRequest,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    ok = MfaService.verify_challenge(user_id=current_user.id, code=body.code)
    if not ok:
        raise HTTPException(status_code=401, detail="Invalid MFA code")
    # In a real implementation, issue a JWT with mfa_verified claim here
    return MfaChallengeVerifyResponse(token="jwt-with-mfa-verified-claim")


@router.post("/recovery", response_model=MfaRecoveryResponse)
async def recovery(
    body: MfaRecoveryRequest,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    try:
        result = MfaService.use_recovery_code(
            user_id=current_user.id,
            recovery_code=body.recovery_code,
        )
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    return MfaRecoveryResponse(**result)
