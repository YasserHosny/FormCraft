from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest

from app.models.user import UserProfile
from app.services.template_permission_service import TemplatePermissionService
from tests.conftest import make_supabase_response


ORG_ID = UUID("44444444-4444-4444-4444-444444444444")
ADMIN_ID = UUID("11111111-1111-1111-1111-111111111111")
USER_ID = UUID("22222222-2222-2222-2222-222222222222")
BRANCH_ID = UUID("55555555-5555-5555-5555-555555555555")
DEPARTMENT_ID = UUID("66666666-6666-6666-6666-666666666666")


def _profile(user_id=USER_ID, role="operator", branch_id=BRANCH_ID):
    return UserProfile(
        id=user_id,
        role=role,
        language="ar",
        display_name="Test User",
        is_active=True,
        org_id=ORG_ID,
        branch_id=branch_id,
        department_id=DEPARTMENT_ID,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def _template(template_id):
    return {
        "id": str(template_id),
        "org_id": str(ORG_ID),
        "status": "published",
        "name": "Cheque Template",
    }


def _policy(policy_id):
    return {
        "id": str(policy_id),
        "org_id": str(ORG_ID),
        "template_id": str(uuid4()),
        "name": "Policy",
        "is_active": True,
        "default_import_policy": "admin_only",
    }


def _grant(effect, principal_type, principal_id, capability="print"):
    return {
        "id": str(uuid4()),
        "effect": effect,
        "principal_type": principal_type,
        "principal_id": str(principal_id),
        "capabilities": [capability],
        "lifecycle_states": ["published"],
    }


def _chain(data):
    chain = MagicMock()
    chain.select.return_value = chain
    chain.eq.return_value = chain
    chain.single.return_value = chain
    chain.insert.return_value = chain
    chain.execute.return_value = make_supabase_response(data)
    return chain


def _client(template, policy=None, grants=None, custom_assignments=None):
    client = MagicMock()
    tables = {
        "templates": _chain(template),
        "template_access_policies": _chain([policy] if policy else []),
        "template_access_grants": _chain(grants or []),
        "custom_template_role_assignments": _chain(custom_assignments or []),
        "template_access_decisions": _chain([{"id": str(uuid4())}]),
    }

    def table(name):
        return tables.get(name, _chain([]))

    client.table.side_effect = table
    return client


@pytest.mark.asyncio
async def test_explicit_deny_overrides_inherited_allow():
    template_id = uuid4()
    policy_id = uuid4()
    grants = [
        _grant("allow", "branch", BRANCH_ID),
        _grant("deny", "user", USER_ID),
    ]
    client = _client(_template(template_id), _policy(policy_id), grants)

    with patch("app.services.template_permission_service.AuditLogger") as audit_cls:
        audit_cls.return_value.log_event = AsyncMock()
        service = TemplatePermissionService(client)
        decision = await service.evaluate_access(template_id, "print", _profile())

    assert decision.allowed is False
    assert decision.reason == "explicit_deny_matched"
    assert len(decision.matched_grants) == 1
    assert len(decision.matched_restrictions) == 1
    audit_cls.return_value.log_event.assert_awaited_once()


@pytest.mark.asyncio
async def test_missing_policy_defaults_to_admin_only_for_imported_templates():
    template_id = uuid4()
    client = _client(_template(template_id), policy=None)

    with patch("app.services.template_permission_service.AuditLogger") as audit_cls:
        audit_cls.return_value.log_event = AsyncMock()
        service = TemplatePermissionService(client)
        operator_decision = await service.evaluate_access(
            template_id, "view", _profile(role="operator")
        )
        admin_decision = await service.evaluate_access(
            template_id, "view", _profile(user_id=ADMIN_ID, role="admin")
        )

    assert operator_decision.allowed is False
    assert operator_decision.reason == "no_policy_admin_only"
    assert admin_decision.allowed is True
    assert admin_decision.reason == "admin_only_import_default"


@pytest.mark.asyncio
async def test_deactivated_custom_role_assignment_does_not_authorize_user():
    template_id = uuid4()
    policy_id = uuid4()
    custom_role_id = uuid4()
    grants = [_grant("allow", "custom_role", custom_role_id, capability="review")]
    inactive_assignment = {
        "role_id": str(custom_role_id),
        "custom_template_roles": {
            "id": str(custom_role_id),
            "is_active": False,
            "capabilities": ["review"],
        },
    }
    client = _client(
        _template(template_id),
        _policy(policy_id),
        grants,
        custom_assignments=[inactive_assignment],
    )

    with patch("app.services.template_permission_service.AuditLogger") as audit_cls:
        audit_cls.return_value.log_event = AsyncMock()
        service = TemplatePermissionService(client)
        decision = await service.evaluate_access(template_id, "review", _profile())

    assert decision.allowed is False
    assert decision.reason == "no_matching_grant"
    assert decision.matched_grants == []


@pytest.mark.asyncio
async def test_diagnostics_include_scope_and_role_sources():
    template_id = uuid4()
    policy_id = uuid4()
    grants = [_grant("allow", "branch", BRANCH_ID, capability="fill")]
    client = _client(_template(template_id), _policy(policy_id), grants)
    profile_chain = _chain(_profile().model_dump(mode="json"))

    def table(name):
        if name == "profiles":
            return profile_chain
        return _client(_template(template_id), _policy(policy_id), grants).table(name)

    client.table.side_effect = table

    with patch("app.services.template_permission_service.AuditLogger") as audit_cls:
        audit_cls.return_value.log_event = AsyncMock()
        service = TemplatePermissionService(client)
        decision = await service.diagnose_access(
            template_id=template_id,
            capability="fill",
            user_id=USER_ID,
            org_id=ORG_ID,
        )

    assert decision.allowed is True
    assert decision.reason == "allow_grant_matched"
    assert "operator" in decision.role_sources
    assert "branch" in decision.scope_matches
