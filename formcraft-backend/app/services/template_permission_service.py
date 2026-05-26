"""Granular template access policy evaluation."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.core.audit import AuditLogger
from app.models.enums import Role
from app.models.user import UserProfile
from app.schemas.template_permissions import (
    TemplateAccessDecisionResponse,
    TemplateAccessPolicyRequest,
    TemplateAccessPolicyResponse,
)


ADMIN_CAPABILITIES = {
    "view",
    "edit",
    "clone",
    "import",
    "export",
    "submit_review",
    "review",
    "publish",
    "fill",
    "print",
    "reprint",
    "report",
}


class TemplatePermissionService:
    """Evaluate and manage template-scoped permissions."""

    def __init__(self, client: Client):
        self.client = client
        self.audit = AuditLogger(client)

    async def replace_policy(
        self,
        template_id: UUID,
        org_id: UUID,
        request: TemplateAccessPolicyRequest,
        actor_id: UUID,
    ) -> TemplateAccessPolicyResponse:
        template = self._get_template(template_id, org_id)

        existing = (
            self.client.table("template_access_policies")
            .select("id")
            .eq("template_id", str(template_id))
            .eq("org_id", str(org_id))
            .eq("is_active", True)
            .execute()
        )
        for row in existing.data or []:
            (
                self.client.table("template_access_policies")
                .update({"is_active": False, "updated_at": self._now()})
                .eq("id", row["id"])
                .execute()
            )

        policy_row = {
            "org_id": str(org_id),
            "template_id": str(template_id),
            "name": request.name,
            "description": request.description,
            "default_import_policy": request.default_import_policy,
            "is_active": True,
            "created_by": str(actor_id),
        }
        policy_result = (
            self.client.table("template_access_policies")
            .insert(policy_row)
            .execute()
        )
        policy = (policy_result.data or [policy_row])[0]
        policy_id = policy.get("id")

        grant_rows = []
        for grant in request.grants:
            row = {
                "org_id": str(org_id),
                "policy_id": policy_id,
                "effect": grant.effect,
                "principal_type": grant.principal_type,
                "principal_id": grant.principal_id,
                "capabilities": list(grant.capabilities),
                "lifecycle_states": list(grant.lifecycle_states),
                "created_by": str(actor_id),
            }
            grant_rows.append(row)

        inserted_grants = []
        if grant_rows:
            grants_result = (
                self.client.table("template_access_grants")
                .insert(grant_rows)
                .execute()
            )
            inserted_grants = grants_result.data or grant_rows

        await self.audit.log_event(
            user_id=str(actor_id),
            action="template_permission.policy_replaced",
            resource_type="template",
            resource_id=str(template_id),
            metadata={
                "policy_id": policy_id,
                "grant_count": len(grant_rows),
                "template_status": template.get("status"),
            },
        )

        return self._policy_response(template_id, policy, inserted_grants)

    async def evaluate_access(
        self,
        template_id: UUID,
        capability: str,
        user: UserProfile,
        persist: bool = True,
    ) -> TemplateAccessDecisionResponse:
        if not user.org_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "User has no organization")

        template = self._get_template(template_id, user.org_id)
        policy = self._get_active_policy(template_id, user.org_id)
        role_sources = self._role_sources(user)
        custom_role_ids = self._active_custom_role_ids(user.id, user.org_id)
        matched_grants: list[dict] = []
        matched_restrictions: list[dict] = []
        scope_matches: set[str] = set()

        if not policy:
            allowed = user.role == Role.ADMIN
            reason = "admin_only_import_default" if allowed else "no_policy_admin_only"
            decision = self._decision(
                allowed=allowed,
                reason=reason,
                capability=capability,
                template_id=template_id,
                user_id=user.id,
                matched_grants=[],
                matched_restrictions=[],
                role_sources=role_sources,
                scope_matches=["admin"] if allowed else [],
            )
            if persist:
                await self._record_decision(user, decision, template)
            return decision

        grants = self._get_policy_grants(policy["id"], user.org_id)
        for grant in grants:
            if not self._grant_applies_to_capability(grant, capability):
                continue
            if not self._grant_applies_to_state(grant, template.get("status")):
                continue
            if not self._principal_matches(grant, user, custom_role_ids, scope_matches):
                continue
            if grant.get("effect") == "deny":
                matched_restrictions.append(self._grant_diagnostic(grant))
            else:
                matched_grants.append(self._grant_diagnostic(grant))

        if matched_restrictions:
            allowed = False
            reason = "explicit_deny_matched"
        elif matched_grants:
            allowed = True
            reason = "allow_grant_matched"
        elif user.role == Role.ADMIN:
            allowed = True
            reason = "base_admin_fallback"
            scope_matches.add("admin")
        else:
            allowed = False
            reason = "no_matching_grant"

        decision = self._decision(
            allowed=allowed,
            reason=reason,
            capability=capability,
            template_id=template_id,
            user_id=user.id,
            matched_grants=matched_grants,
            matched_restrictions=matched_restrictions,
            role_sources=role_sources + [f"custom:{role_id}" for role_id in custom_role_ids],
            scope_matches=sorted(scope_matches),
        )
        if persist:
            await self._record_decision(user, decision, template)
        return decision

    async def diagnose_access(
        self,
        template_id: UUID,
        capability: str,
        user_id: UUID,
        org_id: UUID,
    ) -> TemplateAccessDecisionResponse:
        profile = self._get_profile(user_id, org_id)
        return await self.evaluate_access(template_id, capability, profile)

    def _get_template(self, template_id: UUID, org_id: UUID) -> dict:
        result = (
            self.client.table("templates")
            .select("*")
            .eq("id", str(template_id))
            .eq("org_id", str(org_id))
            .single()
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Template not found")
        return result.data

    def _get_profile(self, user_id: UUID, org_id: UUID) -> UserProfile:
        result = (
            self.client.table("profiles")
            .select("*")
            .eq("id", str(user_id))
            .eq("org_id", str(org_id))
            .single()
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User profile not found")
        return UserProfile(**result.data)

    def _get_active_policy(self, template_id: UUID, org_id: UUID) -> dict | None:
        result = (
            self.client.table("template_access_policies")
            .select("*")
            .eq("template_id", str(template_id))
            .eq("org_id", str(org_id))
            .eq("is_active", True)
            .execute()
        )
        rows = result.data or []
        return rows[0] if rows else None

    def _get_policy_grants(self, policy_id: str, org_id: UUID) -> list[dict]:
        result = (
            self.client.table("template_access_grants")
            .select("*")
            .eq("policy_id", policy_id)
            .eq("org_id", str(org_id))
            .execute()
        )
        return result.data or []

    def _active_custom_role_ids(self, user_id: UUID, org_id: UUID) -> set[str]:
        result = (
            self.client.table("custom_template_role_assignments")
            .select("role_id,custom_template_roles(id,is_active,capabilities)")
            .eq("user_id", str(user_id))
            .eq("org_id", str(org_id))
            .eq("is_active", True)
            .execute()
        )
        role_ids = set()
        for assignment in result.data or []:
            role = assignment.get("custom_template_roles") or {}
            if role.get("is_active", True):
                role_ids.add(str(assignment.get("role_id") or role.get("id")))
        return role_ids

    def _principal_matches(
        self,
        grant: dict,
        user: UserProfile,
        custom_role_ids: set[str],
        scope_matches: set[str],
    ) -> bool:
        principal_type = grant.get("principal_type")
        principal_id = str(grant.get("principal_id"))
        if principal_type == "base_role" and principal_id == user.role.value:
            scope_matches.add("base_role")
            return True
        if principal_type == "custom_role" and principal_id in custom_role_ids:
            scope_matches.add("custom_role")
            return True
        if principal_type == "department" and user.department_id and principal_id == str(user.department_id):
            scope_matches.add("department")
            return True
        if principal_type == "branch" and user.branch_id and principal_id == str(user.branch_id):
            scope_matches.add("branch")
            return True
        if principal_type == "user" and principal_id == str(user.id):
            scope_matches.add("user")
            return True
        return False

    @staticmethod
    def _grant_applies_to_capability(grant: dict, capability: str) -> bool:
        capabilities = grant.get("capabilities") or []
        return capability in capabilities or "*" in capabilities

    @staticmethod
    def _grant_applies_to_state(grant: dict, state: str | None) -> bool:
        states = grant.get("lifecycle_states") or []
        return not states or state in states

    @staticmethod
    def _grant_diagnostic(grant: dict) -> dict:
        return {
            "id": grant.get("id"),
            "effect": grant.get("effect"),
            "principal_type": grant.get("principal_type"),
            "principal_id": grant.get("principal_id"),
            "capabilities": grant.get("capabilities") or [],
            "lifecycle_states": grant.get("lifecycle_states") or [],
        }

    @staticmethod
    def _role_sources(user: UserProfile) -> list[str]:
        return [user.role.value]

    @staticmethod
    def _decision(**kwargs) -> TemplateAccessDecisionResponse:
        return TemplateAccessDecisionResponse(stale_cache=False, **kwargs)

    async def _record_decision(
        self,
        user: UserProfile,
        decision: TemplateAccessDecisionResponse,
        template: dict,
    ) -> None:
        row = {
            "org_id": str(user.org_id),
            "template_id": str(decision.template_id),
            "user_id": str(decision.user_id),
            "capability": decision.capability,
            "allowed": decision.allowed,
            "reason": decision.reason,
            "matched_grants": decision.matched_grants,
            "matched_restrictions": decision.matched_restrictions,
            "stale_cache": decision.stale_cache,
        }
        try:
            self.client.table("template_access_decisions").insert(row).execute()
        except Exception:
            pass

        if not decision.allowed:
            await self.audit.log_event(
                user_id=str(user.id),
                action="template_access.denied",
                resource_type="template",
                resource_id=str(decision.template_id),
                metadata={
                    "capability": decision.capability,
                    "reason": decision.reason,
                    "template_status": template.get("status"),
                },
            )

    @staticmethod
    def _policy_response(
        template_id: UUID,
        policy: dict,
        grants: list[dict],
    ) -> TemplateAccessPolicyResponse:
        return TemplateAccessPolicyResponse(
            id=policy.get("id"),
            template_id=template_id,
            name=policy["name"],
            description=policy.get("description"),
            is_active=policy.get("is_active", True),
            default_import_policy=policy.get("default_import_policy", "admin_only"),
            grants=grants,
        )

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()
