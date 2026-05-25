"""Unit tests for ExportService."""

from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import UUID

import pytest
from fastapi import HTTPException

from app.schemas.export import ExportFilters, ExportPreviewRequest
from app.services.export_service import ExportService


class TestFetchSubmissionRows:
    def test_fetch_applies_org_id_filter(self):
        from unittest.mock import MagicMock
        from tests.conftest import make_supabase_response

        mock_client = MagicMock()
        org_id = UUID("44444444-4444-4444-4444-444444444444")
        rows = [{"id": "test-1", "field_values": {}}]
        count = 1

        select_chain = MagicMock()
        select_chain.eq.return_value = select_chain
        select_chain.order.return_value = select_chain
        select_chain.range.return_value = select_chain
        select_chain.execute.return_value = make_supabase_response(rows, count=count)

        mock_table = MagicMock()
        mock_table.select.return_value = select_chain
        mock_client.table.return_value = mock_table

        service = ExportService(mock_client)
        result_rows, total = service._fetch_submission_rows(org_id, ExportFilters(), limit=100)

        assert total == 1
        assert len(result_rows) == 1
        # Verify org_id filter was applied
        select_chain.eq.assert_any_call("org_id", str(org_id))

    def test_fetch_applies_all_filters(self):
        from unittest.mock import MagicMock
        from tests.conftest import make_supabase_response

        mock_client = MagicMock()
        org_id = UUID("44444444-4444-4444-4444-444444444444")
        template_id = UUID("55555555-5555-5555-5555-555555555555")
        branch_id = UUID("66666666-6666-6666-6666-666666666666")
        operator_id = UUID("77777777-7777-7777-7777-777777777777")
        date_from = "2026-01-01"
        date_to = "2026-12-31"
        status = "completed"

        select_chain = MagicMock()
        select_chain.eq.return_value = select_chain
        select_chain.gte.return_value = select_chain
        select_chain.lte.return_value = select_chain
        select_chain.order.return_value = select_chain
        select_chain.range.return_value = select_chain
        select_chain.execute.return_value = make_supabase_response([], count=0)

        mock_table = MagicMock()
        mock_table.select.return_value = select_chain
        mock_client.table.return_value = mock_table

        filters = ExportFilters(
            template_id=template_id,
            date_from=date_from,
            date_to=date_to,
            branch_id=branch_id,
            operator_id=operator_id,
            status=status,
        )

        service = ExportService(mock_client)
        service._fetch_submission_rows(org_id, filters, limit=100)

        # Verify all filters were applied
        select_chain.eq.assert_any_call("org_id", str(org_id))
        select_chain.eq.assert_any_call("template_id", str(template_id))
        select_chain.eq.assert_any_call("branch_id", str(branch_id))
        select_chain.eq.assert_any_call("operator_id", str(operator_id))
        select_chain.eq.assert_any_call("status", status)
        select_chain.gte.assert_called_once_with("created_at", date_from)
        select_chain.lte.assert_called_once_with("created_at", date_to)


class TestRenderExport:
    def test_flattened_csv_has_field_key_columns(self):
        mock_client = MagicMock()
        service = ExportService(mock_client)

        rows = [
            {
                "id": "sub-1",
                "reference_number": "REF001",
                "template_id": "tmpl-1",
                "template_version": 1,
                "status": "completed",
                "operator_id": "op-1",
                "branch_id": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "field_values": {"name": "Alice", "amount": 100},
            }
        ]

        request = ExportPreviewRequest(filters=ExportFilters(), format="csv", scope="flattened")
        content, media_type, suffix = service._render_export(rows, request)

        assert suffix == "csv"
        assert media_type == "text/csv; charset=utf-8"
        text = content.decode("utf-8")
        assert "name" in text
        assert "amount" in text
        assert "Alice" in text
        assert "100" in text

    def test_structured_json_preserves_field_values(self):
        mock_client = MagicMock()
        service = ExportService(mock_client)

        rows = [
            {
                "id": "sub-1",
                "reference_number": "REF001",
                "template_id": "tmpl-1",
                "template_version": 1,
                "status": "completed",
                "operator_id": "op-1",
                "branch_id": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "field_values": {"name": "Bob", "email": "bob@example.com"},
            }
        ]

        request = ExportPreviewRequest(filters=ExportFilters(), format="json", scope="structured")
        content, media_type, suffix = service._render_export(rows, request)

        assert suffix == "json"
        assert media_type == "application/json; charset=utf-8"
        import json
        data = json.loads(content.decode("utf-8"))
        assert len(data) == 1
        assert data[0]["field_values"]["name"] == "Bob"
        assert data[0]["field_values"]["email"] == "bob@example.com"

    def test_arabic_text_preserved_in_csv(self):
        mock_client = MagicMock()
        service = ExportService(mock_client)

        rows = [
            {
                "id": "sub-1",
                "reference_number": "REF001",
                "template_id": "tmpl-1",
                "template_version": 1,
                "status": "completed",
                "operator_id": "op-1",
                "branch_id": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "field_values": {"name": "مرحبا", "mixed": "Hello مرحبا"},
            }
        ]

        request = ExportPreviewRequest(filters=ExportFilters(), format="csv", scope="flattened")
        content, _, _ = service._render_export(rows, request)

        text = content.decode("utf-8")
        assert "مرحبا" in text
        assert "Hello مرحبا" in text

    def test_formula_escaping(self):
        mock_client = MagicMock()
        service = ExportService(mock_client)

        rows = [
            {
                "id": "sub-1",
                "reference_number": "REF001",
                "template_id": "tmpl-1",
                "template_version": 1,
                "status": "completed",
                "operator_id": "op-1",
                "branch_id": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "field_values": {
                    "formula": "=SUM(A1:A10)",
                    "plus": "+100",
                    "minus": "-50",
                    "at": "@username",
                },
            }
        ]

        request = ExportPreviewRequest(filters=ExportFilters(), format="csv", scope="flattened")
        content, _, _ = service._render_export(rows, request)

        text = content.decode("utf-8")
        assert "'=SUM(A1:A10)" in text
        assert "'+100" in text
        assert "'-50" in text
        assert "'@username" in text

    def test_empty_export_returns_valid_csv(self):
        mock_client = MagicMock()
        service = ExportService(mock_client)

        request = ExportPreviewRequest(filters=ExportFilters(), format="csv", scope="flattened")
        content, media_type, suffix = service._render_export([], request)

        assert suffix == "csv"
        text = content.decode("utf-8")
        assert "\ufeff" in text  # BOM marker for UTF-8


class TestFilterWarnings:
    def test_department_filter_warning(self):
        service = ExportService(None)
        filters = ExportFilters(department_id=UUID("88888888-8888-8888-8888-888888888888"))
        warnings = service._filter_warnings(filters)
        assert len(warnings) == 1
        assert "department_filter_unavailable" in warnings[0]

    def test_no_warning_without_department(self):
        service = ExportService(None)
        filters = ExportFilters()
        warnings = service._filter_warnings(filters)
        assert len(warnings) == 0


class TestDownloadSubmissions:
    @pytest.mark.asyncio
    async def test_oversized_export_raises_413(self):
        from unittest.mock import MagicMock, patch
        from tests.conftest import make_supabase_response
        import asyncio

        mock_client = MagicMock()
        org_id = UUID("44444444-4444-4444-4444-444444444444")
        actor_id = UUID("11111111-1111-1111-1111-111111111111")

        select_chain = MagicMock()
        select_chain.eq.return_value = select_chain
        select_chain.order.return_value = select_chain
        select_chain.range.return_value = select_chain
        select_chain.execute.return_value = make_supabase_response([], count=15000)

        mock_table = MagicMock()
        mock_table.select.return_value = select_chain
        mock_client.table.return_value = mock_table

        insert_chain = MagicMock()
        insert_chain.execute.return_value = make_supabase_response([{"id": str(UUID("99999999-9999-9999-9999-999999999999"))}])
        mock_client.table.return_value.insert.return_value = insert_chain

        mock_audit = MagicMock()
        mock_audit.log_event = MagicMock(return_value=asyncio.Future())
        mock_audit.log_event.return_value.set_result(None)

        request = ExportPreviewRequest(filters=ExportFilters(), format="csv", scope="flattened")

        with patch("app.services.export_service.AuditLogger", return_value=mock_audit):
            service = ExportService(mock_client)
            with pytest.raises(HTTPException) as exc_info:
                await service.download_submissions(org_id, actor_id, request)

        assert exc_info.value.status_code == 413
        assert "limit" in str(exc_info.value.detail)