"""User invitation service (T022)."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.core.audit import AuditLogger


class InvitationService:
    """Handles the full invitation lifecycle: create, list, cancel, accept, expire."""

    def __init__(self, client: Client):
        self.client = client
        self.audit = AuditLogger(client)

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------

    async def create_invitation(
        self, org_id: UUID, data: dict, invited_by: UUID
    ) -> dict:
        email = data["email"].lower().strip()
        self._check_user_limit(org_id)

        # Check for an existing active user with this email in the org
        existing_profiles = (
            self.client.table("profiles")
            .select("id,is_active")
            .eq("org_id", str(org_id))
            .execute()
        )
        if existing_profiles.data:
            for p in existing_profiles.data:
                try:
                    auth_user = self.client.auth.admin.get_user_by_id(p["id"])
                    if (
                        auth_user.user.email
                        and auth_user.user.email.lower() == email
                        and p.get("is_active", True)
                    ):
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail="User already exists in this organization",
                        )
                except HTTPException:
                    raise
                except Exception:
                    continue

        # Cancel any existing pending invitation for the same email + org
        pending = (
            self.client.table("user_invitations")
            .select("id")
            .eq("email", email)
            .eq("org_id", str(org_id))
            .eq("status", "pending")
            .execute()
        )
        if pending.data:
            self.client.table("user_invitations").update(
                {"status": "expired"}
            ).eq("id", pending.data[0]["id"]).execute()

        row = {
            "email": email,
            "role": data["role"],
            "org_id": str(org_id),
            "department_id": (
                str(data["department_id"]) if data.get("department_id") else None
            ),
            "branch_id": (
                str(data["branch_id"]) if data.get("branch_id") else None
            ),
            "invited_by": str(invited_by),
            "status": "pending",
        }
        result = self.client.table("user_invitations").insert(row).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create invitation",
            )
        invitation = result.data[0]
        await self.audit.log_event(
            user_id=str(invited_by),
            action="invitation_created",
            resource_type="invitation",
            resource_id=invitation["id"],
            metadata={"email": email, "role": data["role"]},
        )
        return invitation

    # ------------------------------------------------------------------
    # LIST
    # ------------------------------------------------------------------

    async def list_invitations(
        self,
        org_id: UUID,
        status_filter: str | None = None,
    ) -> list[dict]:
        query = (
            self.client.table("user_invitations")
            .select("*")
            .eq("org_id", str(org_id))
        )
        if status_filter:
            query = query.eq("status", status_filter)
        result = query.order("created_at", desc=True).execute()
        return result.data or []

    # ------------------------------------------------------------------
    # CANCEL
    # ------------------------------------------------------------------

    async def cancel_invitation(
        self, invitation_id: UUID, org_id: UUID, cancelled_by: UUID
    ) -> None:
        result = (
            self.client.table("user_invitations")
            .update({"status": "expired"})
            .eq("id", str(invitation_id))
            .eq("org_id", str(org_id))
            .eq("status", "pending")
            .execute()
        )
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found or already processed",
            )
        await self.audit.log_event(
            user_id=str(cancelled_by),
            action="invitation_cancelled",
            resource_type="invitation",
            resource_id=str(invitation_id),
        )

    # ------------------------------------------------------------------
    # ACCEPT (public — no auth required)
    # ------------------------------------------------------------------

    async def accept_invitation(
        self, token: str, display_name: str, password: str
    ) -> dict:
        result = (
            self.client.table("user_invitations")
            .select("*")
            .eq("token", token)
            .eq("status", "pending")
            .single()
            .execute()
        )
        raw = result.data
        if isinstance(raw, list):
            raw = raw[0] if raw else None
        if not raw:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Invitation expired or already accepted",
            )
        invitation = raw

        # Check expiry
        expires_at = datetime.fromisoformat(
            invitation["expires_at"].replace("Z", "+00:00")
        )
        if expires_at < datetime.now(timezone.utc):
            self.client.table("user_invitations").update(
                {"status": "expired"}
            ).eq("id", invitation["id"]).execute()
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Invitation has expired",
            )

        # Create auth user (or find existing)
        user_id: str | None = None
        try:
            auth_response = self.client.auth.admin.create_user(
                {
                    "email": invitation["email"],
                    "password": password,
                    "email_confirm": True,
                }
            )
            user_id = str(auth_response.user.id)
        except Exception as exc:
            if "already been registered" in str(exc).lower():
                users = self.client.auth.admin.list_users()
                for u in users:
                    if u.email and u.email.lower() == invitation["email"].lower():
                        user_id = str(u.id)
                        break
                if not user_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to create user account",
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to create user account: {exc}",
                )

        # Create profile
        profile_data = {
            "id": user_id,
            "role": invitation["role"],
            "language": "ar",
            "display_name": display_name,
            "is_active": True,
            "org_id": invitation["org_id"],
            "department_id": invitation.get("department_id"),
            "branch_id": invitation.get("branch_id"),
            "created_by": invitation["invited_by"],
        }
        self.client.table("profiles").insert(profile_data).execute()

        # Mark invitation accepted
        self.client.table("user_invitations").update(
            {
                "status": "accepted",
                "accepted_at": datetime.now(timezone.utc).isoformat(),
            }
        ).eq("id", invitation["id"]).execute()

        await self.audit.log_event(
            user_id=user_id,
            action="invitation_accepted",
            resource_type="invitation",
            resource_id=invitation["id"],
            metadata={
                "email": invitation["email"],
                "org_id": invitation["org_id"],
            },
        )
        return {
            "user_id": user_id,
            "email": invitation["email"],
            "role": invitation["role"],
            "org_id": invitation["org_id"],
            "department_id": invitation.get("department_id"),
            "branch_id": invitation.get("branch_id"),
        }

    # ------------------------------------------------------------------
    # TIER LIMIT ENFORCEMENT (G-1)
    # ------------------------------------------------------------------

    def _check_user_limit(self, org_id: UUID) -> None:
        org_result = self.client.table("organizations").select("subscription_tier,purchased_seat_allowance").eq("id", str(org_id)).single().execute()
        if not org_result.data:
            return
        org = org_result.data
        tier = org.get("subscription_tier", "starter")
        limits = self.client.table("tier_limits").select("user_limit").eq("tier", tier).limit(1).execute()
        if not limits.data:
            return
        user_limit = int(limits.data[0]["user_limit"])
        if user_limit <= 0:
            return  # legacy row with 0 = unlimited
        effective_limit = user_limit + int(org.get("purchased_seat_allowance") or 0)
        active = self.client.table("profiles").select("id", count="exact").eq("org_id", str(org_id)).eq("is_active", True).execute()
        pending = self.client.table("user_invitations").select("id", count="exact").eq("org_id", str(org_id)).eq("status", "pending").execute()
        total = (active.count or 0) + (pending.count or 0)
        if total >= effective_limit:
            raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, "billing.user_limit_reached")

    # ------------------------------------------------------------------
    # EXPIRE STALE
    # ------------------------------------------------------------------

    async def expire_stale_invitations(self) -> int:
        """Mark all pending invitations past their expires_at as expired."""
        result = (
            self.client.table("user_invitations")
            .update({"status": "expired"})
            .eq("status", "pending")
            .lt("expires_at", datetime.now(timezone.utc).isoformat())
            .execute()
        )
        return len(result.data) if result.data else 0
