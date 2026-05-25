"""Unit tests for TemplateGovernanceService."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pytest

from app.schemas.admin_templates import BulkActionRequest
from app.services.template_governance_service import TemplateGovernanceService
from tests.conftest import make_supabase_response


def _make_template(template_id=None, status="draft"):
    return {
        "id": str(template_id or uuid4()),
        "name": "Test Template",
        "category": "general",
        "status": status,
        "version": 1,
        "created_by": str(UUID("22222222-2222-2222-2222-222222222222")),
        "department_id": None,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "org_id": str(UUID("44444444-4444-4444-4444-444444444444")),
    }


class TestListTemplates:
    @pytest.mark.asyncio
    async def test_list_templates_basic(self):
        mock_client = MagicMock()
        template = _make_template()
        template["profiles"] = {"display_name": "Test Designer"}
        template["departments"] = None

        query_chain = MagicMock()
        query_chain.eq.return_value = query_chain
        query_chain.range.return_value = query_chain
        query_chain.order.return_value = query_chain
        query_chain.execute.return_value = make_supabase_response([template])

        mock_table = MagicMock()
        mock_table.select.return_value = query_chain
        mock_client.table.return_value = mock_table

        service = TemplateGovernanceService(mock_client)
        items, total = await service.list_templates(
            org_id=UUID("44444444-4444-4444-4444-444444444444")
        )

        assert len(items) == 1
        assert total == 1
        assert items[0]["name"] == "Test Template"
        assert items[0]["designer_name"] == "Test Designer"

    @pytest.mark.asyncio
    async def test_list_templates_with_status_filter(self):
        mock_client = MagicMock()
        template = _make_template(status="published")
        template["profiles"] = None
        template["departments"] = None

        query_chain = MagicMock()
        query_chain.eq.return_value = query_chain
        query_chain.range.return_value = query_chain
        query_chain.order.return_value = query_chain
        query_chain.execute.return_value = make_supabase_response([template])

        mock_table = MagicMock()
        mock_table.select.return_value = query_chain
        mock_client.table.return_value = mock_table

        service = TemplateGovernanceService(mock_client)
        items, total = await service.list_templates(
            org_id=UUID("44444444-4444-4444-4444-444444444444"),
            status_filter="published",
        )

        assert len(items) == 1
        assert items[0]["status"] == "published"


class TestPreviewBulkAction:
    @pytest.mark.asyncio
    async def test_preview_archive_draft(self):
        mock_client = MagicMock()
        template_id = uuid4()
        template = _make_template(template_id=template_id, status="draft")

        query_chain = MagicMock()
        query_chain.in_.return_value = query_chain
        query_chain.eq.return_value = query_chain
        query_chain.execute.return_value = make_supabase_response([template])

        mock_table = MagicMock()
        mock_table.select.return_value = query_chain
        mock_client.table.return_value = mock_table

        service = TemplateGovernanceService(mock_client)
        result = await service.preview_bulk_action(
            org_id=UUID("44444444-4444-4444-4444-444444444444"),
            request=BulkActionRequest(
                action="archive",
                template_ids=[template_id],
                dry_run=True,
            ),
        )

        assert result["action"] == "archive"
        assert result["dry_run"] is True
        assert result["affected_count"] == 1
        assert len(result["warnings"]) == 0

    @pytest.mark.asyncio
    async def test_preview_archive_published_warning(self):
        mock_client = MagicMock()
        template_id = uuid4()
        template = _make_template(template_id=template_id, status="published")

        query_chain = MagicMock()
        query_chain.in_.return_value = query_chain
        query_chain.eq.return_value = query_chain
        query_chain.execute.return_value = make_supabase_response([template])

        mock_table = MagicMock()
        mock_table.select.return_value = query_chain

        # Mock form_submissions query
        usage_chain = MagicMock()
        usage_chain.in_.return_value = usage_chain
        usage_chain.gte.return_value = usage_chain
        usage_chain.execute.return_value = make_supabase_response([])

        def table_side_effect(name):
            if name == "form_submissions":
                mock_fs = MagicMock()
                mock_fs.select.return_value = usage_chain
                return mock_fs
            return mock_table

        mock_client.table.side_effect = table_side_effect

        service = TemplateGovernanceService(mock_client)
        result = await service.preview_bulk_action(
            org_id=UUID("44444444-4444-4444-4444-444444444444"),
            request=BulkActionRequest(
                action="archive",
                template_ids=[template_id],
                dry_run=True,
            ),
        )

        assert result["action"] == "archive"
        assert len(result["warnings"]) == 1
        assert "published" in result["warnings"][0]


class TestExecuteBulkAction:
    @pytest.mark.asyncio
    async def test_execute_archive(self):
        mock_client = MagicMock()
        template_id = uuid4()
        template = _make_template(template_id=template_id, status="draft")

        query_chain = MagicMock()
        query_chain.in_.return_value = query_chain
        query_chain.eq.return_value = query_chain
        query_chain.execute.return_value = make_supabase_response([template])

        update_chain = MagicMock()
        update_chain.eq.return_value = update_chain
        update_chain.execute.return_value = make_supabase_response(
            [{"id": str(template_id)}]
        )

        mock_table = MagicMock()
        mock_table.select.return_value = query_chain
        mock_table.update.return_value = update_chain
        mock_client.table.return_value = mock_table

        # Mock audit logger
        import asyncio

        mock_audit = MagicMock()
        mock_audit.log_event = MagicMock(return_value=asyncio.Future())
        mock_audit.log_event.return_value.set_result(None)

        with patch(
            "app.core.audit.AuditLogger",
            return_value=mock_audit,
        ):
            service = TemplateGovernanceService(mock_client)
            result = await service.execute_bulk_action(
                org_id=UUID("44444444-4444-4444-4444-444444444444"),
                request=BulkActionRequest(
                    action="archive",
                    template_ids=[template_id],
                    dry_run=False,
                ),
                actor_id=UUID("11111111-1111-1111-1111-111111111111"),
            )

        assert result["action"] == "archive"
        assert result["dry_run"] is False
        assert result["affected_count"] == 1
        mock_audit.log_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_reassign_missing_designer(self):
        mock_client = MagicMock()
        template_id = uuid4()
        template = _make_template(template_id=template_id)

        query_chain = MagicMock()
        query_chain.in_.return_value = query_chain
        query_chain.eq.return_value = query_chain
        query_chain.execute.return_value = make_supabase_response([template])

        mock_table = MagicMock()
        mock_table.select.return_value = query_chain
        mock_client.table.return_value = mock_table

        service = TemplateGovernanceService(mock_client)

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await service.execute_bulk_action(
                org_id=UUID("44444444-4444-4444-4444-444444444444"),
                request=BulkActionRequest(
                    action="reassign",
                    template_ids=[template_id],
                    dry_run=False,
                ),
                actor_id=UUID("11111111-1111-1111-1111-111111111111"),
            )

        assert exc_info.value.status_code == 422
        assert "new_designer_id" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_execute_unknown_action(self):
        mock_client = MagicMock()
        template_id = uuid4()
        template = _make_template(template_id=template_id)

        query_chain = MagicMock()
        query_chain.in_.return_value = query_chain
        query_chain.eq.return_value = query_chain
        query_chain.execute.return_value = make_supabase_response([template])

        mock_table = MagicMock()
        mock_table.select.return_value = query_chain
        mock_client.table.return_value = mock_table

        service = TemplateGovernanceService(mock_client)

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await service.execute_bulk_action(
                org_id=UUID("44444444-4444-4444-4444-444444444444"),
                request=BulkActionRequest(
                    action="unknown_action",
                    template_ids=[template_id],
                    dry_run=False,
                ),
                actor_id=UUID("11111111-1111-1111-1111-111111111111"),
            )

        assert exc_info.value.status_code == 422
        assert "Unknown action" in str(exc_info.value.detail)
